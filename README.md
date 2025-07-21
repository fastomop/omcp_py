# OMCP Python Sandbox Server

## Overview

This project provides a secure, Docker-based Python sandbox server using the Model Context Protocol (MCP). It allows for isolated Python code execution and advanced analytics on OMOP data stored in a PostgreSQL database. The architecture now supports connecting sandbox containers to a dedicated Postgres database container, enabling secure, scalable analytics workflows.

## Key Features
- Secure Python code execution in Docker sandboxes
- Sandboxes connect to a PostgreSQL OMOP database (in a Docker container)
- Tools for creating, listing, removing sandboxes, installing packages, and executing code
- New tool: `execute_sql_in_sandbox` for running SQL queries against the OMOP database from within the sandbox
- Resource limits, user isolation, and enhanced Docker security

## Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py
```

### 2. Start the PostgreSQL OMOP Database
Edit `docker-compose.yml` if you need to load your own OMOP data. Then run:
```bash
docker-compose up -d db
```
This will start a Postgres container with:
- Database: `omop`
- User: `omop_user`
- Password: `omop_pass`

### 3. Start the FastMCP Python Sandbox Server
```bash
export PYTHONPATH=src
python src/omcp_py/main.py
```

### 4. Interact Using an MCP Client (Inspector UI, Cursor, etc.)
- **Create a sandbox** using the `create_sandbox` tool.
- **Install packages** (e.g., `psycopg2-binary`) in the sandbox with `install_package`.
- **Run SQL in the sandbox** using the new `execute_sql_in_sandbox` tool:
  - Arguments:
    - `sandbox_id`: The ID of your sandbox
    - `sql`: Your SQL query (e.g., `SELECT COUNT(*) FROM person;`)
- **Remove the sandbox** when done.

## Example Workflow
1. Create a sandbox.
2. Install `psycopg2-binary` in the sandbox:
   ```python
   install_package(sandbox_id, "psycopg2-binary")
   ```
3. Run a SQL query in the sandbox:
   ```python
   execute_sql_in_sandbox(sandbox_id, "SELECT COUNT(*) FROM person;")
   ```
4. Remove the sandbox.

## Security Notes
- Sandboxes are isolated Docker containers with resource limits and user isolation.
- The Postgres database runs in its own container and is only accessible to sandboxes on the same Docker network.
- By default, the database is accessible for both read and write; for production, consider using a read-only user.

## Advanced
- You can load your own OMOP data by mounting a SQL dump in `docker-compose.yml`.
- You can further restrict sandbox network access to only the database container.

## License
MIT
