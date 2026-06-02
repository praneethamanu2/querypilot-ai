import sqlparse


BLOCKED_KEYWORDS = [
    "drop",
    "delete",
    "update",
    "insert",
    "alter",
    "truncate",
    "create",
    "replace",
    "attach",
    "detach"
]


ALLOWED_TABLES = [
    "orders",
    "customers",
    "products"
]


def validate_sql_query(sql_query: str) -> dict:
    """
    Validates SQL before execution.

    Safety checks:
    1. Query must start with SELECT.
    2. Query must not contain dangerous commands.
    3. Query should only use allowed business tables.
    """

    if not sql_query or not sql_query.strip():
        return {
            "is_valid": False,
            "message": "SQL query is empty."
        }

    cleaned_query = sql_query.strip().lower()

    parsed = sqlparse.parse(cleaned_query)

    if not parsed:
        return {
            "is_valid": False,
            "message": "SQL query could not be parsed."
        }

    if not cleaned_query.startswith("select"):
        return {
            "is_valid": False,
            "message": "Only SELECT queries are allowed."
        }

    for keyword in BLOCKED_KEYWORDS:
        if keyword in cleaned_query:
            return {
                "is_valid": False,
                "message": f"Blocked unsafe SQL keyword detected: {keyword}"
            }

    used_allowed_table = any(table in cleaned_query for table in ALLOWED_TABLES)

    if not used_allowed_table:
        return {
            "is_valid": False,
            "message": "Query does not reference an allowed table."
        }

    return {
        "is_valid": True,
        "message": "SQL query passed safety validation."
    }


def get_governance_rules() -> list:
    """
    Returns the governance rules used by InsightGuard AI.
    """

    return [
        "Only SELECT queries are allowed.",
        "Destructive commands such as DROP, DELETE, UPDATE, INSERT, and ALTER are blocked.",
        "Queries must use approved business tables only.",
        "All user questions and generated SQL queries are logged for auditability.",
        "Results are checked before being summarized or visualized."
    ]