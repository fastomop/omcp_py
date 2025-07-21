# OMCP Python Sandbox Server - WIKI

## Architecture Update: PostgreSQL OMOP Database Integration

The sandbox server now supports connecting sandbox containers to a dedicated PostgreSQL database container running OMOP data. This enables secure, scalable analytics workflows and aligns with best practices for data science environments.

### Key Changes
- **Postgres database runs in its own Docker container** (see `docker-compose.yml`).
- **Sandboxes connect to the database over the Docker network** (no more mounting local DuckDB files for analytics).
- **New MCP tool:** `execute_sql_in_sandbox` allows you to run SQL queries against the OMOP database from within the sandbox, using Python and `psycopg2`.
- **Recommended workflow:** All analytics (Python or SQL) should be run inside the sandbox for maximum security and flexibility.

## Secure Database Access
- The database is only accessible to sandboxes on the same Docker network.
- You can enforce read-only access by creating a read-only user in Postgres.
- Sandboxes are still isolated with resource limits, user isolation, and no internet access.

## Example Workflow
1. **Start the database:**
   ```bash
   docker-compose up -d db
   ```
2. **Start the sandbox server:**
   ```bash
   export PYTHONPATH=src
   python src/omcp_py/main.py
   ```
3. **Create a sandbox** using the MCP client (Inspector UI, etc.).
4. **Install `psycopg2-binary`** in the sandbox with `install_package`.
5. **Run SQL in the sandbox** with `execute_sql_in_sandbox`:
   - Arguments:
     - `sandbox_id`: The ID of your sandbox
     - `sql`: Your SQL query (e.g., `SELECT COUNT(*) FROM person;`)
6. **Remove the sandbox** when done.

## Why This Approach?
- **Separation of concerns:** Database and analytics environments are managed independently.
- **Scalability:** Multiple sandboxes/users can connect to the same database.
- **Security:** Sandboxes are isolated; the database is not exposed to the internet.
- **Flexibility:** You can run multi-step analytics, persist data in memory, and (optionally) enable write access for advanced workflows.

## Advanced Topics
- **Loading OMOP data:** Mount a SQL dump in `docker-compose.yml` to initialize the database.
- **Read-only users:** Create a read-only user in Postgres for analytics sandboxes.
- **Custom networks:** Use a custom Docker network for even tighter access control.

## Tool Reference
- `create_sandbox`: Create a new Python sandbox
- `install_package`: Install Python packages in the sandbox
- `execute_python_code`: Run arbitrary Python code in the sandbox
- `execute_sql_in_sandbox`: Run SQL queries against the OMOP Postgres database from within the sandbox
- `remove_sandbox`: Remove a sandbox

## See Also
- [README.md](README.md) for setup and usage
- [docker-compose.yml](docker-compose.yml) for database configuration 