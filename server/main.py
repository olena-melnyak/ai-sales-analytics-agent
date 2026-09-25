
from mcp.server.fastmcp import FastMCP

from server.tools.describe_table import describe_table
from server.tools.list_tables import list_tables
from server.tools.run_sql import run_sql
from server.tools.save_report import save_report

mcp = FastMCP("AI Sales Analytics Agent")


@mcp.tool()
def get_tables() -> list[str]:
    """List all available tables in the sales analytics database."""
    return list_tables()


@mcp.tool()
def get_table_schema(table_name: str) -> list[dict]:
    """Describe a database table with columns, types, nullability, defaults, and business descriptions."""
    return describe_table(table_name)


@mcp.tool()
def execute_sql(query: str) -> list[dict]:
    """Execute a read-only SQL query against the sales analytics database."""
    return run_sql(query)

@mcp.tool()
def create_report(report_name: str, html: str) -> str:
    """Save an HTML analytics report to the reports directory."""
    return save_report(report_name, html)

if __name__ == "__main__":
    mcp.run()
