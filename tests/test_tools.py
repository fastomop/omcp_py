import asyncio
from omcp_py.main import mcp

async def test():
    tools = await mcp.get_tools()
    print(f"Total tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool}")

asyncio.run(test())
