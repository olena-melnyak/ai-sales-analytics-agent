import re

from server.db import get_connection
from server.tools.audit import log_tool_call


def run_sql(query: str) -> list[dict]:
    """Execute a read-only SQL query and return the result as a list of dictionaries."""

    query = query.strip()

    if not query:
        raise ValueError("SQL query cannot be empty.")

    try:
        if not re.match(r"^(SELECT|WITH)\b", query, re.IGNORECASE):
            raise ValueError("Only SELECT queries are allowed.")

        if ";" in query.rstrip(";"):
            raise ValueError("Multiple SQL statements are not allowed.")

        forbidden_keywords = (
            r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|"
            r"GRANT|REVOKE|COMMENT|VACUUM|CALL|COPY)\b"
        )

        if re.search(forbidden_keywords, query, re.IGNORECASE):
            raise ValueError("The query contains a forbidden SQL operation.")

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)

                if cur.description is None:
                    result = []
                else:
                    columns = [column.name for column in cur.description]
                    rows = cur.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]

        log_tool_call(
            tool_name="execute_sql",
            status="success",
            query=query,
        )

        return result

    except Exception as exc:
        log_tool_call(
            tool_name="execute_sql",
            status="error",
            query=query,
            error_message=str(exc),
        )
        raise
