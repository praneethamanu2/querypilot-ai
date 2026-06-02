import json
from datetime import datetime
from pathlib import Path


AUDIT_LOG_PATH = Path("data/audit_log.jsonl")


def log_query_event(question: str, sql_query: str, status: str, row_count: int):
    """
    Saves query history as JSON lines.

    Each line stores:
    - timestamp
    - user question
    - generated SQL
    - execution status
    - number of result rows
    """

    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "question": question,
        "sql_query": sql_query,
        "status": status,
        "row_count": row_count
    }

    with open(AUDIT_LOG_PATH, "a") as file:
        file.write(json.dumps(event) + "\n")


def read_query_history() -> list:
    """
    Reads query history from the audit log.
    """

    if not AUDIT_LOG_PATH.exists():
        return []

    history = []

    with open(AUDIT_LOG_PATH, "r") as file:
        for line in file:
            history.append(json.loads(line))

    return history[-20:]