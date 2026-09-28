from server.db import get_connection
from server.tools.audit import log_tool_call


def list_tables() -> list[str]:
    """List all user tables in the PostgreSQL database."""

    try:
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                tables = [row[0] for row in cur.fetchall()]

        log_tool_call(
            tool_name="get_tables",
            status="success",
            query=query.strip(),
        )

        return tables

    except Exception as exc:
        log_tool_call(
            tool_name="get_tables",
            status="error",
            error_message=str(exc),
        )
        raise
