from server.db import get_connection


def list_tables() -> list[str]:
    """List all user tables in the PostgreSQL database."""
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
            return [row[0] for row in cur.fetchall()]
