# Server Implementation Guide

This document provides detailed implementation information for the OMCP Python Sandbox Server.

## 🏗️ Core Architecture Implementation

### 1. FastMCP Server (`src/omcp_py/main.py`)

The server entry point has been refactored to be a lightweight orchestrator. Instead of containing tool logic, it:
1. Initializes the `FastMCP` instance.
2. Loads global configuration.
3. Registers tool modules.

```python
# src/omcp_py/main.py structure
mcp = FastMCP("Python Sandbox")

# Register modular tools
sandbox_tools.register(mcp)
omop_tools.register(mcp)
query_tools.register(mcp)
```

### 2. Modular Tool Implementation (`src/omcp_py/tools/`)

Tools are split into domain-specific modules for better maintainability.

#### Sandbox Tools (`sandbox_tools.py`)
Handles container lifecycle. It interacts directly with the `SandboxManager` singleton.

#### OMOP Tools (`omop_tools.py`)
Handles healthcare logic. Instead of embedding SQL/Python strings, it loads scripts from `src/omcp_py/scripts/omop/` and injects them into the sandbox.

```python
# Script injection pattern
def _get_script_content(name):
    path = Path(__file__).parent.parent / "scripts" / "omop" / name
    return path.read_text()
```

#### Query Tools (`query_tools.py`)
Implements the "Fast Path" for read-only data access, bypassing Docker containers for performance.

### 3. Script Library (`src/omcp_py/scripts/`)

Complex operations are defined in standalone Python files. This allows:
- **Testing**: Scripts can be run independently during CI/CD.
- **Linting**: Standard Python tooling works on these files.
- **Security**: Logic is separated from the transport layer.

Example script (`create_schema.py`):
```python
import os
import psycopg2

def main():
    # Credentials injected via env vars at runtime
    conn = psycopg2.connect(
        dbname=os.environ["OMOP_DB_NAME"],
        ...
    )
    # ... schema creation logic ...
```

### 4. Sandbox Manager (`src/omcp_py/sandbox_manager.py`)

The `SandboxManager` class orchestrates Docker containers. Key implementation details:

#### Container Creation
```python
container = self.client.containers.run(
    self.config.docker_image,
    detach=True,
    network_mode="none",  # Security: No network
    read_only=True,       # Security: Read-only FS
    ...
)
```

#### Code Execution
It uses `docker exec` to run code. Now enhanced with:
- **Consolidated Timeout**: Uses system `timeout` command.
- **Security Validation**: Calls `CodeValidator` before execution.

```python
def execute_code(self, sandbox_id, code, timeout, validate=False):
    if validate:
        validator.validate(code)
    
    cmd = ["timeout", str(timeout), "python3", "-c", code]
    return container.exec_run(cmd)
```

### 5. Configuration System (`src/omcp_py/config.py`)

Configuration is managed via Pydantic/dataclasses and environment variables. `src/omcp_py/core/globals.py` holds the singleton instance.

```python
@dataclass
class SandboxConfig:
    sandbox_timeout: int = 300
    db_host: str = "localhost"
    # ...
```

---

*This guide reflects the modular architecture introduced in v0.2.0.*
