"""Agentic RAG orchestrator with tool selection and iteration."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from agentic.tools import search_transcripts, query_diagnostics
import os


@dataclass
class AgenticResponse:
    """Response from agentic chat."""
    final_answer: str
    evidence: Dict
    trace: List[Dict]
    confidence: str
    confidence_reason: str


def run_agentic_chat(
    user_msg: str,
    chat_history: List[Dict],
    rag_store_path: str,
    sqlite_path: str,
    config: Dict
) -> AgenticResponse:
    """
    Run agentic chat with tool selection and iteration.
    
    Args:
        user_msg: User's question
        chat_history: Previous chat messages
        rag_store_path: Path to RAG store
        sqlite_path: Path to SQLite database
        config: Configuration dict with:
            - model: OpenAI model name
            - top_k: Number of chunks to retrieve
            - max_tool_calls: Maximum tool calls (default 3)
            - sql_max_rows: Max rows for SQL queries (default 50)
    
    Returns:
        AgenticResponse with answer, evidence, trace, and confidence
    """
    model = config.get("model", "gpt-4o-mini")
    top_k = config.get("top_k", 4)
    max_tool_calls = config.get("max_tool_calls", 3)
    sql_max_rows = config.get("sql_max_rows", 50)
    
    client = OpenAI()
    trace = []
    evidence = {
        "retrieved_chunks": [],
        "sql_queries": [],
        "sql_results": []
    }
    
    # Step 0: Check if clarification is needed
    clarification_prompt = f"""You are a veterinary clinic assistant for demo purposes only.

The user asked: "{user_msg}"

Do you need clarification to answer this question? 
- If the question mentions a pet name (like "Daisy") and asks about test results, lab values, or visits, you can PROCEED - you can query the database.
- If the question says "most recent", "latest", "last visit", etc., you can PROCEED - you can use SQL ORDER BY to find the most recent.
- Only ask for clarification if the question is completely unclear or missing critical information that cannot be inferred from the database.

Respond with ONLY one of:
- "NEEDS_CLARIFICATION: [your clarifying question]" (only if truly necessary)
- "PROCEED: [brief reason why you can proceed]"
"""
    
    clarification_resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": clarification_prompt}],
        temperature=0.2,
        max_tokens=150
    )
    clarification_text = clarification_resp.choices[0].message.content.strip()
    
    trace.append({
        "step": "clarification_check",
        "decision": clarification_text
    })
    
    if clarification_text.startswith("NEEDS_CLARIFICATION:"):
        question = clarification_text.replace("NEEDS_CLARIFICATION:", "").strip()
        return AgenticResponse(
            final_answer=f"I need a bit more information to help you: {question}",
            evidence=evidence,
            trace=trace,
            confidence="Low",
            confidence_reason="Clarification needed before proceeding"
        )
    
    # Step 1: Determine which tools to use
    tool_selection_prompt = f"""You are a veterinary clinic assistant for demo purposes only.

The user asked: "{user_msg}"

You have two tools available:
1. search_transcripts - Search visit transcripts/conversations
2. query_diagnostics - Query lab test results and diagnostic data

Based on the question, which tool(s) should you use FIRST?
- If question mentions "lab values / test results / abnormal / ALT / WBC / last visit results" → use SQL (query_diagnostics) first
- If question mentions "what did the vet say / symptoms / advice / discharge instructions" → use docs (search_transcripts) first
- If question is "what does this lab mean?" or needs both → use both

Respond with ONLY one of:
- "SQL_ONLY"
- "DOCS_ONLY"
- "BOTH"
"""
    
    tool_resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": tool_selection_prompt}],
        temperature=0.2,
        max_tokens=50
    )
    tool_choice = tool_resp.choices[0].message.content.strip()
    
    trace.append({
        "step": "tool_selection",
        "choice": tool_choice
    })
    
    # Step 2: Execute tools (up to max_tool_calls iterations)
    tool_calls_made = 0
    all_context = []
    
    for iteration in range(max_tool_calls):
        if tool_calls_made >= max_tool_calls:
            break
        
        # Determine what to do in this iteration
        if iteration == 0:
            # First iteration: use the selected tool(s)
            if "SQL" in tool_choice or "BOTH" in tool_choice:
                # Generate SQL query
                sql_prompt = f"""You are a veterinary clinic assistant. Generate a SQL query to answer: "{user_msg}"

Available tables/views:
- v_results: view with visit_id, visit_datetime, pet_name, species, test_name, analyte_code, analyte_name, value_num, value_text, unit, flag
- visits: visit_id, pet_id, visit_datetime, chief_complaint, notes
- pets: pet_id, name, species, breed
- tests: test_id, visit_id, test_name, specimen_type

Important:
- For "most recent", "latest", "last visit" queries, use ORDER BY visit_datetime DESC LIMIT 1
- Filter by pet_name using WHERE pet_name = 'Daisy' (or other pet name from the question)
- Filter by test_name using WHERE test_name = 'CBC' (or other test name)
- Use v_results view when querying test results - it has all the data you need
- Always include LIMIT 50 (or smaller if appropriate)

Examples:
- "most recent CBC for Daisy" → SELECT * FROM v_results WHERE pet_name = 'Daisy' AND test_name = 'CBC' ORDER BY visit_datetime DESC LIMIT 50
- "CBC results for Daisy on 2026-01-09" → SELECT * FROM v_results WHERE pet_name = 'Daisy' AND test_name = 'CBC' AND visit_datetime LIKE '2026-01-09%' LIMIT 50

Generate ONLY a valid SQL SELECT query. Do not include explanations, just the SQL query.
"""
                sql_resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": sql_prompt}],
                    temperature=0.2,
                    max_tokens=200
                )
                sql_query = sql_resp.choices[0].message.content.strip()
                # Clean up SQL (remove markdown code blocks if present)
                if sql_query.startswith("```"):
                    sql_query = sql_query.split("```")[1]
                    if sql_query.startswith("sql"):
                        sql_query = sql_query[3:].strip()
                sql_query = sql_query.rstrip(";").strip()
                
                trace.append({
                    "step": f"iteration_{iteration}_sql_generation",
                    "sql": sql_query
                })
                
                sql_result = query_diagnostics(sql_query, max_rows=sql_max_rows)
                evidence["sql_queries"].append(sql_query)
                if sql_result["error"]:
                    all_context.append(f"SQL Error: {sql_result['error']}")
                else:
                    # Format SQL results for context
                    if sql_result["rows"]:
                        preview_rows = sql_result["rows"][:10]  # First 10 rows for context
                        evidence["sql_results"].append({
                            "query": sql_query,
                            "columns": sql_result["columns"],
                            "row_count": sql_result["row_count"],
                            "preview": preview_rows
                        })
                        context_text = f"Lab Results:\nColumns: {', '.join(sql_result['columns'])}\n"
                        context_text += f"Total rows: {sql_result['row_count']}\n"
                        context_text += "Sample rows:\n"
                        for row in preview_rows:
                            context_text += str(row) + "\n"
                        all_context.append(context_text)
                    else:
                        all_context.append("SQL query returned no results.")
                
                tool_calls_made += 1
            
            if "DOCS" in tool_choice or "BOTH" in tool_choice:
                # Search transcripts
                docs_result = search_transcripts(user_msg, top_k=top_k, store_path=rag_store_path)
                evidence["retrieved_chunks"].extend(docs_result["chunks"])
                
                if docs_result["chunks"]:
                    context_text = "Visit Transcript Excerpts:\n"
                    for chunk in docs_result["chunks"]:
                        context_text += f"[{chunk['chunk_id']}] From {chunk['source_doc']} (score: {chunk['score']:.3f}):\n{chunk['text']}\n\n"
                    all_context.append(context_text)
                else:
                    all_context.append("No relevant transcript excerpts found.")
                
                tool_calls_made += 1
        else:
            # Subsequent iterations: check if we need to refine
            if not all_context or (len(evidence["retrieved_chunks"]) == 0 and len(evidence["sql_results"]) == 0):
                # Try once more with refined query
                if len(evidence["sql_results"]) == 0:
                    # Try SQL with different approach
                    sql_prompt = f"""The user asked: "{user_msg}"

Previous SQL query returned no results. Try a different approach.
Generate a SQL SELECT query using v_results view or other tables.
Always include LIMIT 50. Just the SQL, no explanations.
"""
                    sql_resp = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": sql_prompt}],
                        temperature=0.3,
                        max_tokens=200
                    )
                    sql_query = sql_resp.choices[0].message.content.strip()
                    if sql_query.startswith("```"):
                        sql_query = sql_query.split("```")[1]
                        if sql_query.startswith("sql"):
                            sql_query = sql_query[3:].strip()
                    sql_query = sql_query.rstrip(";").strip()
                    
                    sql_result = query_diagnostics(sql_query, max_rows=sql_max_rows)
                    evidence["sql_queries"].append(sql_query)
                    if not sql_result["error"] and sql_result["rows"]:
                        preview_rows = sql_result["rows"][:10]
                        evidence["sql_results"].append({
                            "query": sql_query,
                            "columns": sql_result["columns"],
                            "row_count": sql_result["row_count"],
                            "preview": preview_rows
                        })
                        context_text = f"Lab Results (refined query):\n"
                        for row in preview_rows:
                            context_text += str(row) + "\n"
                        all_context.append(context_text)
                
                tool_calls_made += 1
            else:
                # We have evidence, proceed to answer
                break
    
    # Step 3: Compose final answer
    system_prompt = """You are a veterinary clinic assistant for demo purposes only.

You must ground answers in:
- transcript excerpts (when available)
- diagnostic data (when available)

If you cannot find evidence, say so explicitly.
Keep medical guidance cautious and phrased as "next steps to discuss with your veterinarian."
Do not invent lab values or test results.
"""
    
    user_context = "\n\n".join(all_context) if all_context else "No evidence found."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Evidence gathered:\n\n{user_context}\n\nUser question: {user_msg}\n\nProvide a helpful answer grounded in the evidence above."}
    ]
    
    # Add recent chat history
    for msg in chat_history[-3:]:
        messages.append(msg)
    
    answer_resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2
    )
    final_answer = answer_resp.choices[0].message.content
    
    # Determine confidence
    has_docs = len(evidence["retrieved_chunks"]) > 0
    has_sql = len(evidence["sql_results"]) > 0 and any(r["row_count"] > 0 for r in evidence["sql_results"])
    
    if has_docs and has_sql:
        confidence = "High"
        confidence_reason = "Answer grounded in both transcript and diagnostic data"
    elif has_docs or has_sql:
        confidence = "Medium"
        confidence_reason = f"Answer grounded in {'transcript' if has_docs else 'diagnostic'} data"
    else:
        confidence = "Low"
        confidence_reason = "Limited evidence available"
    
    trace.append({
        "step": "final_answer",
        "confidence": confidence,
        "has_docs": has_docs,
        "has_sql": has_sql
    })
    
    return AgenticResponse(
        final_answer=final_answer,
        evidence=evidence,
        trace=trace,
        confidence=confidence,
        confidence_reason=confidence_reason
    )
