"""Local test client that calls FastMCP tools in-process for quick verification.

This bypasses IPC and calls the registered tool functions directly. It is intended
for developer debugging and smoke-testing only.
"""
import asyncio
import json
import sys

# Ensure project source is importable
sys.path.insert(0, 'src')

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager


async def main_flow():
    config = get_config()
    # Use a more feature-complete base image for the smoke test so pip and DB clients are available
    config.docker_image = 'python:3.11-slim'
    sm = SandboxManager(config)

    print("Creating sandbox...")
    sid = sm.create_sandbox()
    print({'sandbox_id': sid})

    print('Installing pandas inside sandbox... (may take a while)')
    install_code = "import subprocess,sys; r=subprocess.run([sys.executable,'-m','pip','install','pandas'],capture_output=True,text=True); print(r.stdout or r.stderr); sys.exit(r.returncode)"
    res = sm.execute_code(sid, install_code)
    print('install result:', {'exit_code': res['exit_code'], 'error': res.get('error')})

    print('Creating OMOP schema...')
    res = sm.execute_code(sid, """
import psycopg2,sys
try:
    conn = psycopg2.connect(dbname=\"%s\", user=\"%s\", password=\"%s\", host=\"%s\", port=%s)
except Exception as e:
    print('DBCONNECTERROR', e); sys.exit(1)
print('DB OK')
""" % (config.db_name, config.db_user, config.db_password, config.db_host, config.db_port))
    print('create schema result:', {'exit_code': res['exit_code'], 'error': res.get('error')})

    print('Removing sandbox...')
    sm.remove_sandbox(sid)

if __name__ == '__main__':
    asyncio.run(main_flow())
