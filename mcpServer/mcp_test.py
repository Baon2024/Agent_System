import asyncio
from fastmcp import Client

client = Client("http://127.0.0.1:8000/mcp")

async def call_tool(tool: str, query):
    async with client:
        result = await client.call_tool(tool, {"query": query})
        print(result)

asyncio.run(call_tool("search_emails", "Autotrader"))