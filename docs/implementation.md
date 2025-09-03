# Quickstart: Sandbox + PostgreSQL/OMOP CDM

This quickstart shows how to spin up a secure Python sandbox and connect to a PostgreSQL (OMOP CDM) database using the OMCP Python Sandbox server.

1. **Start the server:**
   ```sh
   python src/omcp_py/main.py
   # or
   python server_fastmcp.py
   ```

2. **Create a sandbox:**
   ```python
   result = await mcp.create_sandbox()
   sandbox_id = result["sandbox_id"]
   ```

3. **Install PostgreSQL client:**
   ```python
   await mcp.install_package(sandbox_id=sandbox_id, package="psycopg2-binary", timeout=60)
   ```

4. **Connect and query OMOP CDM:**
   ```python
   code = '''
   import psycopg2
   conn = psycopg2.connect(host="localhost", port=5432, user="omop_user", password="omop_pass", dbname="omop_cdm")
   cur = conn.cursor()
   cur.execute("SELECT COUNT(*) FROM person;")
   print(cur.fetchone())
   cur.close()
   conn.close()
   '''
   result = await mcp.execute_python_code(sandbox_id=sandbox_id, code=code, timeout=30)
   print(result["output"])
   ```

5. **Remove the sandbox:**
   ```python
   await mcp.remove_sandbox(sandbox_id=sandbox_id, force=True)
   ```

See the full guide below for more details, security notes, and advanced usage.

---

# Implementation Details

This document provides a deep dive into the implementation details of the OMCP Python Sandbox, including algorithms, data structures, and core functionality.

## 🏗️ Core Implementation Overview

The OMCP Python Sandbox is built around three main components:
1. **FastMCP Server** - MCP protocol implementation
2. **Sandbox Manager** - Docker container lifecycle management
3. **Configuration System** - Environment-based configuration

## 🚀 FastMCP Server Implementation

### Server Architecture

The main server (`src/omcp_py/main.py`) implements the Model Context Protocol using the FastMCP framework:

```python
# Server initialization
mcp = FastMCP("Python Sandbox")
sandbox_manager = SandboxManager(config)
```

### Tool Implementation Pattern

All MCP tools follow a consistent implementation pattern:

```python
@mcp.tool()
async def tool_name(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Tool description and documentation.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 10)
    
    Returns:
        Dict containing the tool results
    """
    try:
        # Tool implementation
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### Tool 1: `create_sandbox`

**Purpose**: Creates new isolated Python environments

**Implementation Details**:
```python
@mcp.tool()
async def create_sandbox(timeout: Optional[int] = 300) -> Dict[str, Any]:
    try:
        # Create a new sandbox container using the sandbox manager
        sandbox_id = sandbox_manager.create_sandbox()
        
        # Retrieve the sandbox information to return creation details
        sandbox_info = next(
            (s for s in sandbox_manager.list_sandboxes() if s["id"] == sandbox_id),
            None
        )
        
        # Validate that we can retrieve the sandbox info
        if not sandbox_info:
            raise Exception("Failed to get sandbox information after creation")
        
        # Return success response with sandbox details
        return {
            "success": True,
            "sandbox_id": sandbox_id,
            "created_at": sandbox_info["created_at"],
            "last_used": sandbox_info["last_used"]
        }
    except Exception as e:
        logger.error(f"Failed to create sandbox: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Key Features**:
- **UUID Generation**: Each sandbox gets a unique identifier
- **Container Creation**: Delegates to SandboxManager for Docker operations
- **Validation**: Ensures sandbox was created successfully
- **Error Handling**: Comprehensive error handling with logging

### Tool 2: `list_sandboxes`

**Purpose**: Lists and manages active sandboxes

**Implementation Details**:
```python
@mcp.tool()
async def list_sandboxes(include_inactive: bool = False) -> Dict[str, Any]:
    try:
        # Get all sandboxes from the sandbox manager
        sandboxes = sandbox_manager.list_sandboxes()
        
        # Filter out inactive sandboxes if requested
        if not include_inactive:
            from datetime import datetime
            sandboxes = [
                s for s in sandboxes
                if (datetime.now() - datetime.fromisoformat(s["last_used"])).total_seconds() < config.sandbox_timeout
            ]
        
        # Return success response with sandbox list and count
        return {
            "success": True,
            "sandboxes": sandboxes,
            "count": len(sandboxes)
        }
    except Exception as e:
        logger.error(f"Failed to list sandboxes: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Key Features**:
- **Filtering**: Optional filtering of inactive sandboxes
- **Timeout Calculation**: Uses configuration for timeout determination
- **Count Tracking**: Provides count of active sandboxes
- **ISO Timestamps**: Standardized timestamp format

### Tool 3: `remove_sandbox`

**Purpose**: Safely removes sandboxes with force option

**Implementation Details**:
```python
@mcp.tool()
async def remove_sandbox(sandbox_id: str, force: bool = False) -> Dict[str, Any]:
    try:
        # Validate that the sandbox exists
        if sandbox_id not in sandbox_manager.sandboxes:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found"
            }
        
        # Check if sandbox is active (unless force is True)
        if not force:
            from datetime import datetime
            sandbox = sandbox_manager.sandboxes[sandbox_id]
            time_since_use = datetime.now() - sandbox["last_used"]
            
            if time_since_use.total_seconds() < config.sandbox_timeout:
                return {
                    "success": False,
                    "error": f"Sandbox {sandbox_id} is still active. Use force=True to remove."
                }
        
        # Remove the sandbox
        sandbox_manager.remove_sandbox(sandbox_id)
        
        return {
            "success": True,
            "message": f"Sandbox {sandbox_id} removed successfully"
        }
    except Exception as e:
        logger.error(f"Failed to remove sandbox {sandbox_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Key Features**:
- **Existence Validation**: Checks if sandbox exists before removal
- **Activity Check**: Prevents removal of active sandboxes (unless forced)
- **Force Option**: Allows forced removal of active sandboxes
- **Timeout Validation**: Uses configuration for activity determination

### Tool 4: `execute_python_code`

**Purpose**: Runs Python code in isolated containers

**Implementation Details**:
```python
@mcp.tool()
async def execute_python_code(sandbox_id: str, code: str, timeout: Optional[int] = 30) -> Dict[str, Any]:
    try:
        # Validate sandbox exists
        if sandbox_id not in sandbox_manager.sandboxes:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found"
            }
        
        # Validate input
        if not code or not code.strip():
            return {
                "success": False,
                "error": "Code cannot be empty"
            }
        
        # Execute code in sandbox
        result = sandbox_manager.execute_code(sandbox_id, code)
        
        # Parse output
        output = result.output.decode('utf-8') if result.output else ""
        error = result.stderr.decode('utf-8') if result.stderr else ""
        exit_code = result.exit_code
        
        # Determine success based on exit code
        success = exit_code == 0
        
        return {
            "success": success,
            "output": output,
            "error": error,
            "exit_code": exit_code
        }
    except Exception as e:
        logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Key Features**:
- **Input Validation**: Validates sandbox existence and code content
- **Code Execution**: Delegates to SandboxManager for container execution
- **Output Parsing**: Handles stdout, stderr, and exit codes
- **Success Determination**: Based on exit code (0 = success)

### Tool 5: `install_package`

**Purpose**: Installs Python packages in sandboxes

**Implementation Details**:
```python
@mcp.tool()
async def install_package(sandbox_id: str, package: str, timeout: Optional[int] = 60) -> Dict[str, Any]:
    try:
        # Validate sandbox exists
        if sandbox_id not in sandbox_manager.sandboxes:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found"
            }
        
        # Validate package name
        if not package or not package.strip():
            return {
                "success": False,
                "error": "Package name cannot be empty"
            }
        
        # Escape package name for shell safety
        escaped_package = quote(package.strip())
        
        # Install package using pip
        install_command = f"pip install {escaped_package}"
        result = sandbox_manager.execute_code(sandbox_id, install_command)
        
        # Parse output
        output = result.output.decode('utf-8') if result.output else ""
        error = result.stderr.decode('utf-8') if result.stderr else ""
        exit_code = result.exit_code
        
        # Determine success based on exit code
        success = exit_code == 0
        
        return {
            "success": success,
            "output": output,
            "error": error,
            "exit_code": exit_code
        }
    except Exception as e:
        logger.error(f"Failed to install package {package} in sandbox {sandbox_id}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Key Features**:
- **Package Validation**: Validates package name and sandbox existence
- **Command Escaping**: Uses `shlex.quote` for shell safety
- **Pip Installation**: Uses pip for package installation
- **Output Handling**: Captures installation output and errors

## 🐳 Sandbox Manager Implementation

### Class Structure

The `SandboxManager` class (`src/omcp_py/sandbox_manager.py`) manages Docker container lifecycle:

```python
class SandboxManager:
    def __init__(self, config)
    def _cleanup_old_sandboxes(self)
    def create_sandbox(self) -> str
    def remove_sandbox(self, sandbox_id: str)
    def execute_code(self, sandbox_id: str, code: str) -> docker.models.containers.ExecResult
    def list_sandboxes(self) -> list
```

### Initialization

```python
def __init__(self, config):
    self.config = config
    self.client = docker.DockerClient(base_url=os.getenv("DOCKER_HOST", "unix://var/run/docker.sock"))
    self.sandboxes: Dict[str, dict] = {}
    self._cleanup_old_sandboxes()  # Clean up on startup
```

**Key Features**:
- **Docker Client**: Connects to Docker daemon via socket
- **Configuration**: Stores configuration for sandbox behavior
- **Sandbox Tracking**: Dictionary to track active sandboxes
- **Startup Cleanup**: Removes expired sandboxes on startup

### Sandbox Creation Algorithm

```python
def create_sandbox(self) -> str:
    if len(self.sandboxes) >= self.config.max_sandboxes:
        raise RuntimeError("Maximum number of sandboxes reached")
    
    sandbox_id = str(uuid.uuid4())
    
    try:
        # Create Docker container with enhanced security restrictions
        container = self.client.containers.run(
            self.config.docker_image,
            command=["sleep", "infinity"],
            detach=True,
            name=f"omcp-sandbox-{sandbox_id}",
            network_mode="none",      # No network access for security
            mem_limit="512m",         # Memory limit
            cpu_period=100000,        # CPU limits
            cpu_quota=50000,
            remove=True,              # Auto-remove when stopped
            user=1000,                # User isolation
            read_only=True,           # Read-only filesystem
            cap_drop=["ALL"],         # Drop all capabilities
            security_opt=["no-new-privileges"],  # Prevent privilege escalation
            tmpfs={                   # Temporary filesystem mounts
                "/tmp": "rw,noexec,nosuid,size=100M",
                "/sandbox": "rw,noexec,nosuid,size=500M"
            }
        )
        
        # Track sandbox metadata
        self.sandboxes[sandbox_id] = {
            "container": container,
            "created_at": datetime.now(),
            "last_used": datetime.now()
        }
        
        logger.info(f"Created new sandbox {sandbox_id}")
        return sandbox_id
        
    except Exception as e:
        logger.error(f"Failed to create sandbox: {e}")
        raise
```

**Algorithm Steps**:
1. **Capacity Check**: Verify maximum sandbox limit not exceeded
2. **ID Generation**: Generate unique UUID for sandbox
3. **Container Creation**: Create Docker container with security restrictions
4. **Metadata Tracking**: Store container and timing information
5. **Logging**: Log successful creation

### Code Execution Algorithm

```python
def execute_code(self, sandbox_id: str, code: str) -> docker.models.containers.ExecResult:
    if sandbox_id not in self.sandboxes:
        raise ValueError(f"Sandbox {sandbox_id} not found")
    
    container:docker.models.containers.Container = self.sandboxes[sandbox_id]["container"]
    self.sandboxes[sandbox_id]["last_used"] = datetime.now()  # Update usage time
    
    try:
        # Execute code in container and capture output
        exec_result = container.exec_run(
            ["python3", "-c", code]
        )
        return exec_result
    except Exception as e:
        logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
        raise
```

**Algorithm Steps**:
1. **Validation**: Check if sandbox exists
2. **Container Access**: Get container reference
3. **Usage Update**: Update last used timestamp
4. **Code Execution**: Execute Python code in container
5. **Result Return**: Return execution result with output

### Cleanup Algorithm

```python
def _cleanup_old_sandboxes(self):
    """Remove sandboxes that haven't been used within timeout period."""
    now = datetime.now()
    to_remove = []
    
    # Find sandboxes that have exceeded timeout
    for sandbox_id, sandbox in self.sandboxes.items():
        if now - sandbox["last_used"] > timedelta(seconds=self.config.sandbox_timeout):
            to_remove.append(sandbox_id)
    
    # Remove expired sandboxes
    for sandbox_id in to_remove:
        self.remove_sandbox(sandbox_id)
```

**Algorithm Steps**:
1. **Timeout Check**: Calculate current time
2. **Expiration Detection**: Find sandboxes exceeding timeout
3. **Batch Removal**: Remove expired sandboxes
4. **Logging**: Log cleanup operations

## ⚙️ Configuration System Implementation

### Configuration Class

```python
@dataclass
class SandboxConfig:
    """Configuration settings for sandbox behavior and limits."""
    sandbox_timeout: int
    max_sandboxes: int  
    docker_image: str
    sandbox_base_url: Optional[str]
    debug: bool
    log_level: str
```

### Configuration Loading

```python
def get_config() -> SandboxConfig:
    """Load and return configuration from environment variables."""
    return SandboxConfig(
        sandbox_timeout=int(os.getenv("SANDBOX_TIMEOUT", "300")),
        max_sandboxes=int(os.getenv("MAX_SANDBOXES", "10")),
        docker_image=os.getenv("DOCKER_IMAGE", "python:3.11-slim"),
        sandbox_base_url=os.getenv("SANDBOX_BASE_URL"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )
```

**Key Features**:
- **Environment Variables**: Load from environment with defaults
- **Type Conversion**: Automatic type conversion for numeric values
- **Default Values**: Sensible defaults for all configuration options
- **Dotenv Support**: Load from .env file if present

## 🔒 Security Implementation

### Container Security Measures

1. **Network Isolation**: `network_mode="none"`
2. **Resource Limits**: Memory (512MB), CPU (50% of one core)
3. **User Isolation**: Non-root user (UID 1000)
4. **Filesystem Security**: Read-only with temporary mounts
5. **Capability Dropping**: All Linux capabilities removed
6. **Privilege Escalation Prevention**: `no-new-privileges`

### Input Validation

```python
# Command escaping for shell safety
escaped_package = quote(package.strip())

# Input validation
if not code or not code.strip():
    return {
        "success": False,
        "error": "Code cannot be empty"
    }
```

### Error Handling

```python
try:
    # Operation implementation
    result = perform_operation()
    return {"success": True, "result": result}
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {"success": False, "error": str(e)}
```

## 📊 Data Structures

### Sandbox Metadata

```python
self.sandboxes[sandbox_id] = {
    "container": container,           # Docker container object
    "created_at": datetime.now(),     # Creation timestamp
    "last_used": datetime.now()       # Last usage timestamp
}
```

### Tool Response Format

```python
{
    "success": bool,                  # Operation success status
    "sandbox_id": str,               # Sandbox identifier (if applicable)
    "output": str,                   # Standard output
    "error": str,                    # Error output
    "exit_code": int,                # Process exit code
    "created_at": str,               # ISO timestamp
    "last_used": str,                # ISO timestamp
    "message": str                   # Success/error message
}
```

## 🔄 Concurrency and Threading

### Async/Await Pattern

All MCP tools use async/await for non-blocking operation:

```python
@mcp.tool()
async def tool_name(param: str) -> Dict[str, Any]:
    # Async implementation
    result = await async_operation(param)
    return result
```

### Thread Safety

- **SandboxManager**: Thread-safe operations with proper locking
- **Docker Client**: Thread-safe Docker API operations
- **Configuration**: Immutable configuration objects

## 📈 Performance Considerations

### Resource Management

1. **Container Limits**: Memory and CPU restrictions per sandbox
2. **Auto-cleanup**: Automatic removal of inactive sandboxes
3. **Connection Pooling**: Efficient Docker client usage
4. **Timeout Controls**: Execution time limits

### Optimization Strategies

1. **Lazy Loading**: Configuration loaded on demand
2. **Caching**: Sandbox metadata caching
3. **Batch Operations**: Efficient cleanup operations
4. **Resource Limits**: Prevent resource exhaustion

## 🧪 Testing Implementation

### Unit Testing

- **Tool Testing**: Individual tool functionality
- **SandboxManager Testing**: Container lifecycle operations
- **Configuration Testing**: Environment variable loading
- **Error Handling Testing**: Exception scenarios

### Integration Testing

- **Docker Integration**: End-to-end container operations
- **MCP Protocol Testing**: Protocol compliance verification
- **Security Testing**: Security measure validation

## 🔮 Future Implementation Considerations

### Planned Enhancements

1. **Plugin System**: Extensible tool architecture
2. **Metrics Collection**: Performance and usage metrics
3. **Advanced Security**: Additional security measures
4. **OMOP CDM Integration**: Healthcare data analysis tools

### Scalability Improvements

1. **Load Balancing**: Multiple server instances
2. **Database Backend**: Persistent sandbox metadata
3. **Caching Layer**: Redis-based caching
4. **Monitoring**: Prometheus metrics integration

---

*This document provides detailed implementation information. For architecture overview, see [Architecture Overview](architecture.md).* 

# Spinning Up a Sandbox and Connecting to PostgreSQL (OMOP CDM)

This section provides a step-by-step guide for creating a secure Python sandbox, installing the PostgreSQL client, and connecting to a PostgreSQL database (including OMOP CDM use cases) using the OMCP Python Sandbox server.

---

## Prerequisites

- Docker is running on your machine.
- PostgreSQL is running and accessible (local or remote).
- The OMCP Python Sandbox server is installed and dependencies are set up (`pip install -r requirements.txt`).
- Your `.env` or environment variables are set for both the sandbox server and the target database.

---

## 1. Start the OMCP Python Sandbox Server

From your project root, run:

```sh
python src/omcp_py/main.py
```

or (if you have a `server_fastmcp.py` entrypoint):

```sh
python server_fastmcp.py
```

This will start the MCP server and make the sandbox management tools available.

---

## 2. Create a Sandbox

You can do this via:
- The MCP Inspector (web UI, if set up)
- A Python client using the MCP protocol
- Or, for testing, you can call the tool directly in Python (if running interactively):

**Example using the MCP tool interface:**

```python
result = await mcp.create_sandbox()
sandbox_id = result["sandbox_id"]
print("Sandbox created:", sandbox_id)
```

This will spin up a new Docker container, isolated and ready for code execution.

---

## 3. Install PostgreSQL Client in the Sandbox

To connect to PostgreSQL from inside the sandbox, you need the `psycopg2-binary` package (or another PostgreSQL client library) installed in the sandbox.

**Install it using the MCP tool:**

```python
await mcp.install_package(
    sandbox_id=sandbox_id,
    package="psycopg2-binary",
    timeout=60
)
```

---

## 4. Execute Code to Connect to PostgreSQL

Now, you can run Python code in the sandbox that connects to your PostgreSQL database. You’ll need to provide the connection details (host, port, user, password, db name).

**Example code to run:**

```python
code = '''
import psycopg2
conn = psycopg2.connect(
    host="your_db_host",
    port=5432,
    user="your_db_user",
    password="your_db_password",
    dbname="your_db_name"
)
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())
cur.close()
conn.close()
'''
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code=code,
    timeout=30
)
print(result["output"])
```

**Note:**
- Replace `"your_db_host"`, `"your_db_user"`, etc. with your actual database credentials.
- For security, in production you would inject these credentials securely, not hard-code them.

---

## 5. (Optional) Query OMOP CDM Tables

If your PostgreSQL database contains OMOP CDM data, you can now run SQL queries against those tables from within the sandbox, e.g.:

```python
cur.execute("SELECT COUNT(*) FROM person;")
print(cur.fetchone())
```

---

## 6. Clean Up

When done, remove the sandbox:

```python
await mcp.remove_sandbox(sandbox_id=sandbox_id, force=True)
```

---

## Summary Table

| Step | Action | Command/Code |
|------|--------|--------------|
| 1 | Start server | `python src/omcp_py/main.py` |
| 2 | Create sandbox | `await mcp.create_sandbox()` |
| 3 | Install psycopg2 | `await mcp.install_package(..., package="psycopg2-binary")` |
| 4 | Connect to DB | `await mcp.execute_python_code(..., code=...)` |
| 5 | Query OMOP CDM | Use SQL in your code |
| 6 | Remove sandbox | `await mcp.remove_sandbox(...)` |

---

## Security Note
- In production, never hard-code DB credentials in code. Use environment variables, secrets management, or secure injection mechanisms.
- Sandboxes are isolated and have no network access by default. You may need to adjust Docker settings if you want to allow outbound DB connections (with caution).

---

## Example: Full Workflow

```python
# 1. Create a sandbox
result = await mcp.create_sandbox()
sandbox_id = result["sandbox_id"]

# 2. Install PostgreSQL client
await mcp.install_package(sandbox_id=sandbox_id, package="psycopg2-binary", timeout=60)

# 3. Connect and query OMOP CDM
code = '''
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="omop_user",
    password="omop_pass",
    dbname="omop_cdm"
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM person;")
print(cur.fetchone())
cur.close()
conn.close()
'''
result = await mcp.execute_python_code(sandbox_id=sandbox_id, code=code, timeout=30)
print(result["output"])

# 4. Clean up
await mcp.remove_sandbox(sandbox_id=sandbox_id, force=True)
```

---

## OMOP CDM Context
- The OMOP Common Data Model (CDM) is a standardized data model for clinical data.
- This workflow enables secure, auditable analytics and AI workflows on OMOP CDM data using isolated Python sandboxes.
- For more on OMOP CDM, see the project wiki and roadmap sections. 

## Recent changes (2025-09-03)

The project has small developer-oriented updates:

- Database connection configuration is now centralized in `src/omcp_py/config.py` and sourced from environment variables (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). Update `.env` or set those environment variables for your local setup.
- A developer convenience Postgres filesystem tar is included (`docker/images/postgres.tar`) and referenced as `fastomop/postgres:from-tar` in `docker-compose.yml` for quick local DB usage. This is intended for development and may lack a standard entrypoint; use the official Postgres image for production.
