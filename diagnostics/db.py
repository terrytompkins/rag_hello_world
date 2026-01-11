"""Database initialization and management for diagnostics database."""

import os
import sqlite3
from pathlib import Path

DIAGNOSTICS_DB_PATH = os.environ.get("DIAGNOSTICS_DB_PATH", "diagnostics/diagnostics.db")


def get_db_path():
    """Get the path to the diagnostics database."""
    return DIAGNOSTICS_DB_PATH


def init_db(db_path: str = None):
    """Initialize the database with schema if it doesn't exist."""
    if db_path is None:
        db_path = get_db_path()
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database already exists and has tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='owners'")
        if cursor.fetchone():
            # Database already initialized
            conn.close()
            return
    except:
        pass
    
    # Read and execute schema
    schema_path = Path(__file__).parent / "schema.sql"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
        conn.commit()
    
    conn.close()


def get_connection(db_path: str = None):
    """Get a connection to the diagnostics database."""
    if db_path is None:
        db_path = get_db_path()
    
    # Ensure database is initialized
    init_db(db_path)
    
    return sqlite3.connect(db_path)


def execute_query(sql: str, params: tuple = None, db_path: str = None):
    """Execute a SELECT query and return results."""
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        return {
            "columns": columns,
            "rows": [dict(row) for row in rows],
            "row_count": len(rows)
        }
    finally:
        conn.close()
