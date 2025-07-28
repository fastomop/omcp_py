import asyncio
from mcp import MCPClient

async def main():
    # Connect to the FastMCP server via stdio
    client = await MCPClient.create_stdio()

    # 1. Create a sandbox
    print("Creating sandbox...")
    resp = await client.call_tool("create_sandbox", {})
    assert resp["success"], f"Failed to create sandbox: {resp}"
    sandbox_id = resp["sandbox_id"]
    print(f"Sandbox created: {sandbox_id}")

    # 2. Install duckdb in the sandbox
    print("Installing duckdb in sandbox...")
    resp = await client.call_tool("install_package", {"sandbox_id": sandbox_id, "package": "duckdb"})
    print(f"Install output: {resp['output']}")
    
    # 3. Execute code to query the DuckDB file
    code = '''
import duckdb
con = duckdb.connect('/data/synthea.duckdb')
result = con.execute('SELECT COUNT(*) FROM person').fetchall()
print(result)
'''
    print("Executing code in sandbox...")
    resp = await client.call_tool("execute_python_code", {"sandbox_id": sandbox_id, "code": code})
    print(f"Execution output: {resp['output']}")

    # 4. Clean up: remove the sandbox
    print("Removing sandbox...")
    await client.call_tool("remove_sandbox", {"sandbox_id": sandbox_id, "force": True})
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main()) 