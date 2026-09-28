from server.db import get_connection
from server.tools.audit import log_tool_call

def describe_table(table_name: str) -> list[dict]:
    """Describe a PostgreSQL table including column types and business descriptions."""

    try:
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                col_description(
                    (table_schema || '.' || table_name)::regclass,
                    ordinal_position
                ) AS description
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (table_name,))
                rows = cur.fetchall()

        result = [
            {
                "column_name": row[0],
                "data_type": row[1],
                "is_nullable": row[2],
                "column_default": row[3],
                "description": row[4],
            }
            for row in rows
        ]

        log_tool_call(
            tool_name="get_table_schema",
            status="success",
            query=query.strip(),
        )

        return result

    except Exception as exc:
        log_tool_call(
            tool_name="get_table_schema",
            status="error",
            error_message=str(exc),
        )
        raise
