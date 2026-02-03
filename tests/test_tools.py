import asyncio
from omcp_py.main import mcp


def test_registered_tools():
    async def _get_tools():
        return await mcp.get_tools()

    tools = asyncio.run(_get_tools())
    assert any("create_sandbox" in str(t) for t in tools)
