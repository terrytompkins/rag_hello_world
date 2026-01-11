"""Helper queries for diagnostics viewer."""

from diagnostics.db import execute_query


def get_visit_summary(limit: int = 20):
    """Get summary of recent visits."""
    sql = """
    SELECT 
        v.visit_id, 
        v.visit_datetime, 
        p.name AS pet_name, 
        p.species, 
        v.chief_complaint
    FROM visits v 
    JOIN pets p ON p.pet_id = v.pet_id
    ORDER BY v.visit_datetime DESC
    LIMIT ?
    """
    return execute_query(sql, (limit,))


def get_visit_tests(visit_id: str):
    """Get all tests for a specific visit."""
    sql = """
    SELECT 
        test_id,
        test_name,
        specimen_type,
        ordered_datetime,
        result_datetime,
        status
    FROM tests
    WHERE visit_id = ?
    ORDER BY ordered_datetime
    """
    return execute_query(sql, (visit_id,))


def get_abnormal_results(visit_id: str):
    """Get abnormal results (H or L flags) for a visit."""
    sql = """
    SELECT 
        analyte_code, 
        analyte_name, 
        value_num, 
        value_text,
        unit, 
        flag, 
        test_name
    FROM v_results
    WHERE visit_id = ?
      AND flag IN ('H','L')
    ORDER BY test_name, analyte_code
    LIMIT 50
    """
    return execute_query(sql, (visit_id,))


def get_test_results(visit_id: str, test_name: str = None):
    """Get all results for a visit, optionally filtered by test name."""
    if test_name:
        sql = """
        SELECT 
            analyte_code,
            analyte_name,
            value_num,
            value_text,
            unit,
            flag,
            test_name
        FROM v_results
        WHERE visit_id = ? AND test_name = ?
        ORDER BY analyte_code
        LIMIT 50
        """
        return execute_query(sql, (visit_id, test_name))
    else:
        sql = """
        SELECT 
            analyte_code,
            analyte_name,
            value_num,
            value_text,
            unit,
            flag,
            test_name
        FROM v_results
        WHERE visit_id = ?
        ORDER BY test_name, analyte_code
        LIMIT 50
        """
        return execute_query(sql, (visit_id,))
