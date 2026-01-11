"""SQL safety checks for read-only queries."""

import re
from typing import Tuple


FORBIDDEN_KEYWORDS = [
    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'ATTACH', 
    'DETACH', 'PRAGMA', 'VACUUM', 'CREATE', 'REPLACE'
]


def is_safe_sql(sql: str) -> Tuple[bool, str]:
    """
    Check if SQL is safe for read-only execution.
    Returns (is_safe, error_message)
    """
    sql_upper = sql.strip().upper()
    
    # Must start with SELECT
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT statements are allowed"
    
    # Check for forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, sql_upper):
            return False, f"Forbidden keyword detected: {keyword}"
    
    # Check for multiple statements (semicolons)
    if ';' in sql and sql.count(';') > 1:
        return False, "Multiple statements not allowed"
    
    return True, ""


def enforce_limit(sql: str, max_rows: int = 50) -> str:
    """Ensure SQL has a LIMIT clause."""
    sql_upper = sql.strip().upper()
    
    # Check if LIMIT already exists
    if 'LIMIT' in sql_upper:
        # Extract existing limit value and ensure it's not too high
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper, re.IGNORECASE)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit <= max_rows:
                return sql  # Already has acceptable limit
            # Replace with max_rows
            return re.sub(r'LIMIT\s+\d+', f'LIMIT {max_rows}', sql, flags=re.IGNORECASE)
    
    # Add LIMIT if missing
    # Remove trailing semicolon if present, add LIMIT, then add semicolon back if it was there
    has_semicolon = sql.rstrip().endswith(';')
    sql_clean = sql.rstrip().rstrip(';')
    sql_with_limit = f"{sql_clean} LIMIT {max_rows}"
    if has_semicolon:
        sql_with_limit += ";"
    
    return sql_with_limit
