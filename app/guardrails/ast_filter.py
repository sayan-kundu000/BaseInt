"""AST SQL Safety Filter for BaseInt.

Analyzes SQL statements via Abstract Syntax Trees to enforce strict read-only execution.
Blocks INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, and any multi-statement exploits.
"""

from typing import Tuple, List
import re
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML, DDL


FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "RENAME", "REPLACE", "MERGE", "EXEC", "EXECUTE",
    "GRANT", "REVOKE", "ATTACH", "DETACH", "PRAGMA", "VACUUM"
}


def is_safe_select_only(sql_query: str) -> bool:
    """Validate that the query contains solely read-only SELECT statements.
    
    Conforms directly to the project specification requirements.
    """
    if not sql_query or not sql_query.strip():
        return False

    # Check for raw dangerous tokens first
    clean_query = sql_query.strip()
    
    parsed = sqlparse.parse(clean_query)
    if not parsed:
        return False

    for statement in parsed:
        # Check statement type
        stmt_type = statement.get_type()
        if stmt_type != "SELECT":
            return False

        # Verify no nested forbidden DDL/DML tokens exist
        for token in statement.flatten():
            val = token.value.upper()
            if val in FORBIDDEN_KEYWORDS:
                return False

    return True


def validate_ast_safety(sql_query: str) -> Tuple[bool, str]:
    """Perform rigorous AST inspection and return status with descriptive error telemetry."""
    if not sql_query or not sql_query.strip():
        return False, "Empty or whitespace-only SQL query."

    try:
        parsed: List[Statement] = sqlparse.parse(sql_query)
    except Exception as e:
        return False, f"SQL AST Parsing Exception: {str(e)}"

    if not parsed:
        return False, "Failed to parse any valid SQL statement from input."

    if len(parsed) > 1:
        # Multiple statements chained together
        types = [s.get_type() for s in parsed]
        if any(t != "SELECT" for t in types):
            return False, f"Multi-statement execution rejected. Detected operations: {', '.join(types)}"

    for idx, stmt in enumerate(parsed):
        stmt_type = stmt.get_type()
        if stmt_type != "SELECT":
            return False, f"AST Validation Rejected: Operation '{stmt_type}' is prohibited. Only read-only 'SELECT' statements are permitted."

        for token in stmt.flatten():
            token_val = token.value.strip().upper()
            if token_val in FORBIDDEN_KEYWORDS:
                return False, f"AST Validation Rejected: Prohibited keyword '{token_val}' detected inside query structure."

    return True, "AST Validation Passed: Query verified as safe read-only SELECT structure."
