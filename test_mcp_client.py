"""Quick MCP round-trip test: connect to the local mineru MCP server, list tools, call mineru_info."""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

BASE = r"C:\Users\Emad Karimi\Desktop\MinerU"


async def main():
    params = StdioServerParameters(
        command=rf"{BASE}\.venv\Scripts\python.exe",
        args=[rf"{BASE}\mineru_mcp_server.py"],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            res = await session.call_tool("mineru_info", {})
            for c in res.content:
                if getattr(c, "text", None):
                    print("RESULT:", c.text)


asyncio.run(main())
