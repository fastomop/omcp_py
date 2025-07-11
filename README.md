# OMCP Python Sandbox Server

> **IMPORTANT: After cloning, you must install the package in editable mode before running any server scripts:**
>
> ```sh
> uv pip install -e .
> # or
> pip install -e .
> ```
>
> Or, run the provided install script:
> ```sh
> ./install.sh
> ```
>
> This ensures the `omcp_py` package is available for all server scripts and tools.

A secure, MCP-compliant Python code execution environment with Docker-based sandboxing. This server implements the Model Context Protocol (MCP) specification for safe, isolated Python code execution with enterprise-grade security features.

## Features

- **MCP-Compliant Tools**:
  - `create_sandbox`: Create isolated Python environments
  - `list_sandboxes`: List active sandboxes with status
  - `remove_sandbox`: Safely remove sandboxes
  - `execute_python_code`: Run Python code in sandbox
  - `install_package`: Install Python packages in sandbox

- **Security Features**:
  - Docker-based isolation with enhanced security options
  - User isolation (sandboxuser instead of root)
  - Read-only filesystem with temporary writable areas
  - Dropped Linux capabilities (cap_drop=["ALL"])
  - No privilege escalation (no-new-privileges)
  - Command injection protection (shlex.quote)
  - Resource limits (CPU, memory, execution timeouts)
  - Network isolation (network_mode="none")
  - Input validation and sanitisation
  - Auto-cleanup of inactive sandboxes

- **MCP Integration**:
  - Standard MCP tool interface
  - Proper error handling with timeout support
  - Structured logging
  - Type-safe responses
  - JSON output support
  - FastMCP implementation available

## Prerequisites

- **Python 3.10+** (for MCP server)
- **Docker** (for sandbox isolation)
- **uv** (for dependency management)
- **Node.js 18+** (for MCP Inspector - optional)

## Installation

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/fastomop/omcp_py.git
   cd omcp_py
   ```

2. **Install Dependencies**:
   ```sh
   uv pip install -r requirements.txt
   ```

3. **Install Package in Editable Mode** (REQUIRED):
   ```sh
   uv pip install -e .
   ```
   
   Or use the provided install script:
   ```sh
   ./install.sh
   ```

4. **Environment Setup** (optional):
   Create a `.env` file:
   ```env
   SANDBOX_TIMEOUT=300
   MAX_SANDBOXES=10
   DOCKER_IMAGE=python:3.11-slim
   DEBUG=false
   LOG_LEVEL=INFO
   ```

## Usage

### Starting the Server

**FastMCP Server (Recommended):**
```sh
python server_fastmcp.py
```

The server will start and expose the following MCP tools:

### Using MCP Inspector for Development and Testing

The MCP Inspector provides a web-based interface to test and debug your MCP server tools in real-time.

#### Installation
```sh
# Install Node.js if not already installed
sudo apt install nodejs npm  # Ubuntu/Debian
# or
brew install node  # macOS
```

#### Launching the Inspector
```sh
# Start your MCP server in one terminal
python server_fastmcp.py

# Launch MCP Inspector in another terminal
npx @modelcontextprotocol/inspector python server_fastmcp.py
```

#### Accessing the Web Interface
After launching the inspector, open your browser and navigate to:
```
http://127.0.0.1:6274 #local host address may be different for your machine
```

#### Inspector Features
- **Interactive Tool Testing**: Test all MCP tools with a web interface
- **Request/Response Inspection**: View JSON-RPC messages in real-time
- **Code Execution Testing**: Run Python code in sandboxes
- **Package Installation Testing**: Install packages in sandboxes
- **Sandbox Management**: Create, list, and remove sandboxes
- **Error Debugging**: View detailed error messages and stack traces
- **Performance Monitoring**: Track execution times and resource usage

#### Inspector Workflow
1. **Create a Sandbox**: Use the `create_sandbox` tool to create a new isolated environment
2. **Execute Code**: Use `execute_python_code` to run Python code in the sandbox
3. **Install Packages**: Use `install_package` to add dependencies to the sandbox
4. **Monitor Sandboxes**: Use `list_sandboxes` to see all active sandboxes
5. **Cleanup**: Use `remove_sandbox` to clean up when done

#### Troubleshooting Inspector
- **Port Already in Use**: The inspector typically uses port 6274. If busy, it will automatically find another port
- **Connection Issues**: Ensure your MCP server is running before launching the inspector
- **Node.js Version**: Ensure you have Node.js 18+ installed for compatibility

### Tool Examples

1. **Create a Sandbox**:
   ```python
   result = await mcp.create_sandbox()
   sandbox_id = result["sandbox_id"]
   ```

2. **Install a Package**:
   ```python
   await mcp.install_package(
       sandbox_id=sandbox_id,
       package="numpy==1.24.0",
       timeout=60
   )
   ```

3. **Execute Code**:
   ```python
   result = await mcp.execute_python_code(
       sandbox_id=sandbox_id,
       code="""
       import numpy as np
       arr = np.array([1, 2, 3, 4, 5])
       print({"sum": arr.sum()})
       """,
       timeout=30
   )
   ```

4. **List Sandboxes**:
   ```python
   sandboxes = await mcp.list_sandboxes(include_inactive=False)
   ```

5. **Remove a Sandbox**:
   ```python
   await mcp.remove_sandbox(
       sandbox_id=sandbox_id,
       force=False
   )
   ```

### Tool Specifications

#### `create_sandbox`
- **Input**: Optional timeout (default: 300s)
- **Output**: `{sandbox_id, created_at, last_used}`

#### `execute_python_code`
- **Input**: 
  - `sandbox_id` (required)
  - `code` (required)
  - `timeout` (optional, default: 30s)
- **Output**: `{success, output, error, exit_code}`

#### `install_package`
- **Input**:
  - `sandbox_id` (required)
  - `package` (required, e.g., "numpy==1.24.0")
  - `timeout` (optional, default: 60s)
- **Output**: `{success, output, error, exit_code}`

#### `list_sandboxes`
- **Input**: `include_inactive` (optional, default: false)
- **Output**: `{sandboxes: [...], count: N}`

#### `remove_sandbox`
- **Input**:
  - `sandbox_id` (required)
  - `force` (optional, default: false)
- **Output**: `{success, message}`

## Security

### Container Security
Each sandbox runs in a Docker container with:
- **User isolation**: Runs as `sandboxuser` instead of root
- **Read-only filesystem**: Prevents file system modifications
- **Dropped capabilities**: Removes all Linux capabilities
- **No privilege escalation**: Prevents privilege escalation attacks
- **Temporary filesystems**: Secure tmpfs mounts for `/tmp` and `/sandbox`
- **No network access**: Complete network isolation
- **Resource limits**: CPU, memory, and execution time limits

### Code Execution Security
- **Command injection protection**: Uses `shlex.quote` for proper escaping
- **List-form commands**: Prevents shell injection attacks
- **Timeout handling**: Configurable execution timeouts
- **Input validation**: Comprehensive input sanitisation
- **Error isolation**: Errors don't affect other sandboxes

### Resource Management
- **Maximum sandboxes limit**: Prevents resource exhaustion
- **Timeout-based cleanup**: Automatic removal of inactive sandboxes
- **Force removal option**: Manual cleanup when needed
- **Memory limits**: 512MB per sandbox
- **CPU limits**: Restricted CPU usage

## Implementation

### FastMCP Server (`server_fastmcp.py`)
- **Enhanced Implementation**: Uses FastMCP framework with decorators
- **Better Security**: Enhanced security features and timeout handling
- **Simplified Development**: Faster development workflow
- **Production Ready**: Robust error handling and logging

## Development

### Project Structure
```
omcp_py/
├── src/
│   └── omcp_py/
│       ├── core/
│       │   └── sandbox.py      # Enhanced sandbox management
│       ├── tools/
│       │   ├── execution_tools.py
│       │   └── sandbox_tools.py
│       └── utils/
│           └── config.py       # Configuration
├── server_fastmcp.py           # FastMCP server (main)
├── Dockerfile                  # UV-based Docker build
├── requirements.txt
└── pyproject.toml
```

### Testing
```sh
uv pip install -r requirements.txt[dev]
pytest
```

### Logging
- Logs to stderr (MCP convention)
- Configurable levels (INFO, DEBUG, etc.)
- Structured format with security events

## Recent Updates

### v0.2.1 - MCP Inspector Integration
- **MCP Inspector Support**: Added web-based tool testing interface
- **Development Tools**: Enhanced debugging and testing capabilities
- **Interactive Testing**: Real-time tool testing with request/response inspection
- **Performance Monitoring**: Track execution times and resource usage

### v0.2.0 - Enhanced Security & FastMCP
- **Enhanced Docker Security**: User isolation, read-only filesystem, dropped capabilities
- **FastMCP Implementation**: Alternative server with simplified syntax
- **Command Injection Protection**: shlex.quote for proper command escaping
- **Timeout Handling**: Specific timeout error handling
- **UV Package Manager**: Faster package management in Docker
- **Improved Error Handling**: Better timeout and security error handling

### v0.1.0 - Initial Release
- Basic MCP server implementation
- Docker-based sandboxing
- Core tool functionality
- Resource management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License
MIT

## Database Configuration

Set the following environment variables (or add to your .env file) to configure PostgreSQL connection:

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=omcp_user
DB_PASSWORD=omcp_pass
DB_NAME=omcp_db
```

## Database Integration and OMOP CDM Roadmap

### Current State
- Sandbox metadata (creation, usage, removal) is now persisted in a PostgreSQL database using SQLAlchemy.
- This enables robust tracking and management of sandboxes, even across server restarts.

### Next Steps: OMOP CDM Integration
- The long-term goal is to enable sandboxed Python code to securely connect to and query OMOP Common Data Model (CDM) data stored in PostgreSQL.
- This will allow data science, analytics, and AI agents to run code against real clinical data in a controlled, auditable, and secure environment.
- Future features will include:
  - Secure credential injection for sandboxes to access OMOP CDM tables
  - Example tools and code snippets for querying OMOP CDM (e.g., patient counts, cohort definitions)
  - Fine-grained access controls and auditing for database queries
  - Documentation and best practices for OMOP CDM analytics in the sandbox

### How to Contribute
- If you are interested in OMOP CDM or clinical data science, contributions and feedback are welcome!
- See the WIKI for more details on OMOP CDM and planned features.
