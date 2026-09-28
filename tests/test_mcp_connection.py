import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "server.main"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Available MCP tools:")

            tools = await session.list_tools()

            for tool in tools.tools:
                print(f"- {tool.name}")

            print("\nCalling execute_sql...")

            sql_result = await session.call_tool(
                "execute_sql",
                {
                    "query": """
                        SELECT
                            SUM(amount) AS total_revenue
                        FROM sales
                        WHERE status = 'completed';
                    """
                },
            )

            print("\nSQL result:")

            for content in sql_result.content:
                if hasattr(content, "text"):
                    print(content.text)

            print("\nCalling create_report...")

            result = await session.call_tool(
                "create_report",
                {
                    "report_name": "test_report.html",
                    "html": """
                    <html>
                        <head>
                            <title>Sales Analytics Test</title>
                        </head>
                        <body>
                            <h1>Sales Analytics Report</h1>
                            <p>This report was created through MCP.</p>
                        </body>
                    </html>
                    """,
                },
            )

            print("\nReport result:")

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
