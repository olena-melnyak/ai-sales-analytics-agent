from server.db import get_connection


def log_tool_call(
    tool_name: str,
    status: str,
    query: str | None = None,
    error_message: str | None = None,
) -> None:
    """Write an MCP tool execution event to the audit log."""

    sql = """
        INSERT INTO audit_log (
            tool_name,
            status,
            query,
            error_message
        )
        VALUES (%s, %s, %s, %s);
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    tool_name,
                    status,
                    query,
                    error_message,
                ),
            )
