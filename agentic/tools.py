"""Agentic tools for search and SQL query."""

from typing import Dict, List
from rag_utils import search as rag_search
from diagnostics.db import execute_query, get_db_path
from agentic.sql_safety import is_safe_sql, enforce_limit


def search_transcripts(query: str, top_k: int = 4, store_path: str = None) -> Dict:
    """
    Search transcript documents using RAG.
    
    Returns:
        {
            "chunks": [
                {"chunk_id": idx, "text": "...", "score": 0.95, "source_doc": "..."}
            ],
            "count": 3
        }
    """
    hits = rag_search(query, k=top_k, store_path=store_path)
    
    chunks = []
    for idx, hit in enumerate(hits, start=1):
        chunks.append({
            "chunk_id": idx,
            "text": hit["text"],
            "score": hit["score"],
            "source_doc": hit["source"]
        })
    
    return {
        "chunks": chunks,
        "count": len(chunks)
    }


def query_diagnostics(sql: str, max_rows: int = 50) -> Dict:
    """
    Execute a read-only SQL query against the diagnostics database.
    
    Returns:
        {
            "columns": [...],
            "rows": [...],
            "row_count": 3,
            "error": None or error message
        }
    """
    # Safety check
    is_safe, error_msg = is_safe_sql(sql)
    if not is_safe:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": error_msg
        }
    
    # Enforce LIMIT
    sql_safe = enforce_limit(sql, max_rows=max_rows)
    
    try:
        result = execute_query(sql_safe)
        result["error"] = None
        return result
    except Exception as e:
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e)
        }
