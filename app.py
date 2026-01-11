
import os
import streamlit as st
from openai import OpenAI
from rag_utils import add_document_to_store, search, load_store, clear_store
from agentic.agentic import run_agentic_chat
from diagnostics.db import init_db, get_db_path
from diagnostics.queries import get_visit_summary, get_visit_tests, get_abnormal_results, get_test_results
from diagnostics.seed import seed_database, clear_database
import pandas as pd

st.set_page_config(page_title="Pet Care Coach - RAG Demo", page_icon="🐾", layout="wide")
st.title("🐾 Pet Care Coach — RAG Demo")
st.caption("Compare Model-only, Classic RAG, and Agentic Context modes.")

if "OPENAI_API_KEY" not in os.environ:
    st.warning("Set the OPENAI_API_KEY environment variable before running. e.g., export OPENAI_API_KEY=sk-...")
client = OpenAI()

# Initialize diagnostics database
init_db()

with st.sidebar:
    st.header("Mode Selection")
    mode = st.radio(
        "Chat Mode",
        ["Model-only (No RAG)", "Classic RAG (Transcript)", "Agentic Context (Transcript + Diagnostics)"],
        help="Select the mode to demonstrate different levels of context"
    )
    
    st.divider()
    st.header("Settings")
    top_k = st.slider("Top-k chunks", 1, 8, 4)
    model = st.text_input("Chat model", value=os.environ.get("CHAT_MODEL", "gpt-4o"))
    
    st.divider()
    st.subheader("Document store")
    store_path = os.environ.get("RAG_STORE_PATH", "rag_store.json")
    store = load_store(store_path)
    st.write(f"Chunks indexed: **{len(store['chunks'])}**")
    if st.button("Clear document store"):
        clear_store(store_path)
        if "processed_files" in st.session_state:
            st.session_state.processed_files = set()
        st.rerun()
    st.subheader("Add documents")
    files = st.file_uploader("Drop markdown (.md) files", type=["md","markdown","txt"], accept_multiple_files=True, key="doc_uploader")
    
    # Track processed files to avoid reprocessing after rerun
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()
    
    # Show success message if files were just processed
    if "upload_success" in st.session_state and st.session_state.upload_success:
        st.success(st.session_state.upload_success)
        # Clear the message after showing it
        st.session_state.upload_success = None
    
    if files:
        # Create a unique identifier for this batch of files
        file_ids = tuple((f.name, f.size) for f in files)
        
        # Only process if we haven't processed these files before
        if file_ids not in st.session_state.processed_files:
            total = 0
            for f in files:
                content = f.read().decode("utf-8", errors="ignore")
                total += add_document_to_store(f.name, content, store_path=store_path)
            
            # Mark these files as processed
            st.session_state.processed_files.add(file_ids)
            # Store success message in session state to show after rerun
            st.session_state.upload_success = f"Indexed {total} chunks from {len(files)} file(s)."
            st.rerun()
    
    st.divider()
    st.subheader("Diagnostics Database")
    if st.button("Load Seed Data", help="Load demo data for Daisy the dog"):
        try:
            seed_database()
            st.success("Seed data loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error loading seed data: {e}")
    if st.button("Clear Diagnostics Database", help="Clear all diagnostics data"):
        try:
            clear_database()
            st.success("Database cleared!")
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing database: {e}")
    
    st.divider()
    show_diagnostics = st.checkbox("Show Diagnostics Viewer", value=False)

# Diagnostics viewer
if show_diagnostics:
    st.header("🔬 Diagnostics Viewer")
    
    # Get visit summary
    visit_summary = get_visit_summary()
    if visit_summary["rows"]:
        visit_ids = [row["visit_id"] for row in visit_summary["rows"]]
        selected_visit = st.selectbox("Select Visit", visit_ids)
        
        if selected_visit:
            # Visit info
            st.subheader("Visit Information")
            visit_info = [v for v in visit_summary["rows"] if v["visit_id"] == selected_visit][0]
            st.json(visit_info)
            
            # Tests
            st.subheader("Tests Performed")
            tests = get_visit_tests(selected_visit)
            if tests["rows"]:
                st.dataframe(pd.DataFrame(tests["rows"]), use_container_width=True)
            else:
                st.info("No tests found for this visit.")
            
            # Abnormal results
            st.subheader("Abnormal Results")
            abnormal = get_abnormal_results(selected_visit)
            if abnormal["rows"]:
                st.dataframe(pd.DataFrame(abnormal["rows"]), use_container_width=True)
            else:
                st.info("No abnormal results found.")
            
            # All results
            st.subheader("All Results")
            all_results = get_test_results(selected_visit)
            if all_results["rows"]:
                st.dataframe(pd.DataFrame(all_results["rows"]), use_container_width=True)
            else:
                st.info("No results found.")
    else:
        st.info("No visits found in database. Load seed data to see diagnostics.")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agentic_responses" not in st.session_state:
    st.session_state.agentic_responses = {}

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Show "How I answered" for assistant messages in agentic mode
        if msg["role"] == "assistant" and idx in st.session_state.agentic_responses:
            resp_data = st.session_state.agentic_responses[idx]
            with st.expander("🔍 How I answered"):
                st.write(f"**Mode:** Agentic Context")
                st.write(f"**Confidence:** {resp_data['confidence']} - {resp_data['confidence_reason']}")
                
                if resp_data["evidence"]["retrieved_chunks"]:
                    st.write("**Retrieved Transcript Chunks:**")
                    for chunk in resp_data["evidence"]["retrieved_chunks"]:
                        st.write(f"- [{chunk['chunk_id']}] {chunk['source_doc']} (score: {chunk['score']:.3f})")
                        with st.expander(f"View chunk {chunk['chunk_id']}"):
                            st.text(chunk["text"])
                
                if resp_data["evidence"]["sql_queries"]:
                    st.write("**SQL Queries Executed:**")
                    for sql_idx, sql_query in enumerate(resp_data["evidence"]["sql_queries"], 1):
                        st.code(sql_query, language="sql")
                        if sql_idx <= len(resp_data["evidence"]["sql_results"]):
                            sql_result = resp_data["evidence"]["sql_results"][sql_idx - 1]
                            st.write(f"Returned {sql_result['row_count']} rows")
                            if sql_result["preview"]:
                                st.dataframe(pd.DataFrame(sql_result["preview"]), use_container_width=True)
                
                st.write("**Trace:**")
                st.json(resp_data["trace"])

prompt = st.chat_input("Ask a question about your docs (or anything)")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if mode == "Model-only (No RAG)":
                # Model-only mode
                system_prompt = "You are a concise, helpful assistant. Answer based on your general knowledge."
                messages = [{"role": "system", "content": system_prompt}]
                history_tail = st.session_state.messages[-4:]
                for m in history_tail:
                    messages.append({"role": m["role"], "content": m["content"]})
                messages.append({"role": "user", "content": prompt})
                
                resp = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
                answer = resp.choices[0].message.content
                st.markdown(answer)
                
            elif mode == "Classic RAG (Transcript)":
                # Classic RAG mode
                context_blocks, citations = [], []
                hits = search(prompt, k=top_k, store_path=store_path)
                if hits:
                    for idx, h in enumerate(hits, start=1):
                        context_blocks.append(f"[{idx}] source: {h['source']}\n{h['text']}")
                        citations.append(f"[{idx}] {h['source']} (score {h['score']:.3f})")
                else:
                    citations.append("_No documents in store or no matches._")

                system_prompt = (
                    "You are a concise, helpful assistant.\n"
                    "If RAG context is provided, ground your answer primarily in that context and reference sources like [1], [2].\n"
                    "If the context is irrelevant or insufficient, say so explicitly before answering from general knowledge.\n"
                )

                messages = [{"role": "system", "content": system_prompt}]
                if context_blocks:
                    messages.append({"role": "user", "content": "RAG context:\n" + "\n\n".join(context_blocks)})
                history_tail = st.session_state.messages[-4:]
                for m in history_tail:
                    messages.append({"role": m["role"], "content": m["content"]})
                messages.append({"role": "user", "content": prompt})

                resp = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
                answer = resp.choices[0].message.content
                st.markdown(answer)
                
                with st.expander("Show retrieved sources"):
                    st.markdown("\n".join(f"- {c}" for c in citations))
                    
            elif mode == "Agentic Context (Transcript + Diagnostics)":
                # Agentic mode
                config = {
                    "model": model,
                    "top_k": top_k,
                    "max_tool_calls": 3,
                    "sql_max_rows": 50
                }
                
                agentic_resp = run_agentic_chat(
                    user_msg=prompt,
                    chat_history=st.session_state.messages[-4:],
                    rag_store_path=store_path,
                    sqlite_path=get_db_path(),
                    config=config
                )
                
                answer = agentic_resp.final_answer
                st.markdown(answer)
                
                # Store response data for "How I answered" panel
                response_idx = len(st.session_state.messages)
                st.session_state.agentic_responses[response_idx] = {
                    "evidence": agentic_resp.evidence,
                    "trace": agentic_resp.trace,
                    "confidence": agentic_resp.confidence,
                    "confidence_reason": agentic_resp.confidence_reason
                }
                
                with st.expander("🔍 How I answered"):
                    st.write(f"**Mode:** Agentic Context")
                    st.write(f"**Confidence:** {agentic_resp.confidence} - {agentic_resp.confidence_reason}")
                    
                    if agentic_resp.evidence["retrieved_chunks"]:
                        st.write("**Retrieved Transcript Chunks:**")
                        for chunk in agentic_resp.evidence["retrieved_chunks"]:
                            st.write(f"- [{chunk['chunk_id']}] {chunk['source_doc']} (score: {chunk['score']:.3f})")
                            with st.expander(f"View chunk {chunk['chunk_id']}"):
                                st.text(chunk["text"])
                    
                    if agentic_resp.evidence["sql_queries"]:
                        st.write("**SQL Queries Executed:**")
                        for sql_idx, sql_query in enumerate(agentic_resp.evidence["sql_queries"], 1):
                            st.code(sql_query, language="sql")
                            if sql_idx <= len(agentic_resp.evidence["sql_results"]):
                                sql_result = agentic_resp.evidence["sql_results"][sql_idx - 1]
                                st.write(f"Returned {sql_result['row_count']} rows")
                                if sql_result["preview"]:
                                    st.dataframe(pd.DataFrame(sql_result["preview"]), use_container_width=True)
                    
                    st.write("**Trace:**")
                    st.json(agentic_resp.trace)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
