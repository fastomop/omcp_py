import asyncio
import pytest
from conftest import require_integration
from mcp import MCPClient


def test_sandbox_duckdb_via_mcp():
    require_integration()

    async def _run():
        try:
            client = await MCPClient.create_stdio()
        except Exception:
            pytest.skip("MCP server not available over stdio")

        resp = await client.call_tool("create_sandbox", {})
        assert resp["success"], f"Failed to create sandbox: {resp}"
        sandbox_id = resp["sandbox_id"]

        try:
            resp = await client.call_tool("install_package", {"sandbox_id": sandbox_id, "package": "duckdb"})
            assert resp["success"] or resp.get("exit_code") == 0

            code = '''
import duckdb
con = duckdb.connect('/data/synthea.duckdb')
result = con.execute('SELECT COUNT(*) FROM person').fetchall()
print(result)
'''
            resp = await client.call_tool("execute_python_code", {"sandbox_id": sandbox_id, "code": code})
            assert "[]" not in resp.get("output", "")
        finally:
            await client.call_tool("remove_sandbox", {"sandbox_id": sandbox_id, "force": True})

    asyncio.run(_run())
