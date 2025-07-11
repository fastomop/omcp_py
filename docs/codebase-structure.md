# Codebase Structure

This document provides a comprehensive overview of the OMCP Python Sandbox codebase structure, file organization, and module relationships.

## 📁 Project Root Structure

```
omcp_py/
├── src/omcp_py/           # Main package source code
├── docs/                  # Technical documentation (this folder)
├── tests/                 # Test suite
├── .venv/                 # Virtual environment (local)
├── node_modules/          # Node.js dependencies (for MCP Inspector)
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Dependency lock file
├── README.md             # Project overview and quick start
├── WIKI.md               # Comprehensive project wiki
├── install.sh            # Installation script
├── sample.env            # Environment variables template
├── .gitignore            # Git ignore rules
├── .python-version       # Python version specification
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker Compose configuration
├── mkdocs.yml           # Documentation site configuration
├── package.json         # Node.js package configuration
├── pyodide_server.js    # Pyodide server (legacy)
└── deno_pyodide_server.ts # Deno server (legacy)
```

## 🏗️ Source Code Structure (`src/omcp_py/`)

The main package is organized in the `src/omcp_py/` directory following Python packaging best practices:

```
src/omcp_py/
├── __init__.py           # Package initialization
├── main.py              # FastMCP server implementation (main entry point)
├── config.py            # Configuration management
├── sandbox_manager.py   # Docker container lifecycle management
├── core/                # Core functionality modules
│   └── __pycache__/     # Python cache (auto-generated)
├── tools/               # MCP tool implementations
│   └── __pycache__/     # Python cache (auto-generated)
└── utils/               # Utility functions
    └── __pycache__/     # Python cache (auto-generated)
```

## 📄 Core Module Details

### `src/omcp_py/__init__.py`
**Purpose**: Package initialization and version information
**Size**: 3 lines
**Key Features**:
- Defines package version
- Exports main components for external access

### `src/omcp_py/main.py` (14KB, 378 lines)
**Purpose**: Main FastMCP server implementation
**Key Components**:

#### Imports and Dependencies
```python
import asyncio
import logging
import sys
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from omcp_py.sandbox_manager import SandboxManager
from omcp_py.config import get_config
from shlex import quote
import requests
```

#### Core Server Setup
- **FastMCP Instance**: Main server object using decorator-based tool definitions
- **Sandbox Manager**: Singleton for Docker container lifecycle management
- **Configuration**: Environment-based configuration loading
- **Logging**: Structured logging to stderr (MCP convention)

#### MCP Tool Implementations
1. **`create_sandbox()`** - Creates new isolated Python environments
2. **`list_sandboxes()`** - Lists and manages active sandboxes
3. **`remove_sandbox()`** - Safely removes sandboxes with force option
4. **`execute_python_code()`** - Runs Python code in isolated containers
5. **`install_package()`** - Installs Python packages in sandboxes

#### Key Features
- **Error Handling**: Comprehensive try-catch blocks with detailed error messages
- **Input Validation**: Parameter validation and sanitization
- **Resource Management**: Automatic cleanup and timeout handling
- **Security**: Command escaping with `shlex.quote`

### `src/omcp_py/sandbox_manager.py` (5.1KB, 132 lines)
**Purpose**: Docker container lifecycle management
**Key Components**:

#### Class Structure
```python
class SandboxManager:
    def __init__(self, config)
    def _cleanup_old_sandboxes(self)
    def create_sandbox(self) -> str
    def remove_sandbox(self, sandbox_id: str)
    def execute_code(self, sandbox_id: str, code: str) -> docker.models.containers.ExecResult
    def list_sandboxes(self) -> list
```

#### Docker Integration
- **Docker Client**: Connection to Docker daemon via socket
- **Container Creation**: Enhanced security with multiple restrictions
- **Resource Limits**: Memory (512MB), CPU (50% of one core)
- **Security Options**: Network isolation, read-only filesystem, dropped capabilities

#### Security Features
```python
container = self.client.containers.run(
    self.config.docker_image,
    command=["sleep", "infinity"],
    detach=True,
    name=f"omcp-sandbox-{sandbox_id}",
    network_mode="none",      # No network access
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
```

### `src/omcp_py/config.py` (1.1KB, 36 lines)
**Purpose**: Configuration management using environment variables
**Key Components**:

#### Configuration Class
```python
@dataclass
class SandboxConfig:
    sandbox_timeout: int
    max_sandboxes: int  
    docker_image: str
    sandbox_base_url: Optional[str]
    debug: bool
    log_level: str
```

#### Environment Variables
- **`SANDBOX_TIMEOUT`** (default: 300) - Sandbox timeout in seconds
- **`MAX_SANDBOXES`** (default: 10) - Maximum number of concurrent sandboxes
- **`DOCKER_IMAGE`** (default: python:3.11-slim) - Base Docker image
- **`SANDBOX_BASE_URL`** (optional) - Base URL for sandbox services
- **`DEBUG`** (default: false) - Enable debug mode
- **`LOG_LEVEL`** (default: INFO) - Logging level

## 🔧 Configuration Files

### `pyproject.toml` (777B, 44 lines)
**Purpose**: Project configuration, dependencies, and build settings

#### Project Metadata
```toml
[project]
name = "omcp_py"
version = "0.1.0"
description = "A secure Python code execution sandbox for MCP"
requires-python = ">=3.10"
```

#### Dependencies
- **`mcp[cli]>=1.6.0`** - Model Context Protocol implementation
- **`httpx>=0.27.0`** - HTTP client library
- **`flask>=3.0.0`** - Web framework
- **`pydantic>=2.0.0`** - Data validation
- **`docker>=7.0.0`** - Docker API client
- **`python-dotenv>=1.0.0`** - Environment variable management

#### Development Dependencies
- **`pytest>=8.0.0`** - Testing framework
- **`pytest-asyncio>=0.24.0`** - Async testing support
- **`black>=24.0.0`** - Code formatting
- **`ruff>=0.6.0`** - Linting and formatting

#### Build Configuration
- **`hatchling`** - Build backend
- **`uv`** - Package management
- **`black`** - Code formatting configuration
- **`ruff`** - Linting configuration

### `uv.lock` (104KB, 882 lines)
**Purpose**: Dependency lock file for reproducible builds
**Content**: Exact versions of all dependencies and their sub-dependencies

## 🧪 Test Structure

### `tests/` Directory
**Purpose**: Test suite and test utilities
**Structure**: Organized by module and functionality
**Coverage**: Unit tests, integration tests, and security tests

## 📚 Documentation Structure

### `docs/` Directory
**Purpose**: Technical documentation
**Files**:
- **`README.md`** - Documentation overview and navigation
- **`codebase-structure.md`** - This file
- **`architecture.md`** - System architecture
- **`implementation.md`** - Implementation details
- **`security.md`** - Security model
- **`api-reference.md`** - API documentation
- **`configuration.md`** - Configuration guide
- **`deployment.md`** - Deployment guide
- **`development.md`** - Development setup
- **`testing.md`** - Testing guide
- **`contributing.md`** - Contributing guidelines

## 🔄 Module Relationships

### Dependency Flow
```
main.py
├── imports sandbox_manager.py
├── imports config.py
└── uses FastMCP framework

sandbox_manager.py
├── imports config.py
├── uses docker library
└── manages container lifecycle

config.py
├── uses python-dotenv
└── provides configuration to other modules
```

### Data Flow
1. **Configuration Loading**: `config.py` loads environment variables
2. **Server Initialization**: `main.py` creates FastMCP server and SandboxManager
3. **Tool Execution**: MCP tools in `main.py` delegate to SandboxManager
4. **Container Management**: SandboxManager handles Docker operations
5. **Result Return**: Results flow back through the chain to MCP client

## 🏗️ Architecture Patterns

### Singleton Pattern
- **SandboxManager**: Single instance manages all sandbox containers
- **Configuration**: Single configuration object shared across modules

### Decorator Pattern
- **FastMCP Tools**: Uses `@mcp.tool()` decorators for MCP tool definitions
- **Error Handling**: Consistent error handling patterns across tools

### Factory Pattern
- **Sandbox Creation**: SandboxManager creates containers with consistent configuration
- **Configuration**: `get_config()` factory function creates configuration objects

### Observer Pattern
- **Logging**: Structured logging throughout the system
- **Cleanup**: Automatic cleanup of expired sandboxes

## 🔒 Security Architecture

### Container Security
- **Network Isolation**: `network_mode="none"`
- **Resource Limits**: Memory and CPU restrictions
- **User Isolation**: Non-root user (UID 1000)
- **Filesystem Security**: Read-only with temporary mounts
- **Capability Dropping**: All Linux capabilities removed
- **Privilege Escalation Prevention**: `no-new-privileges` security option

### Input Validation
- **Command Escaping**: `shlex.quote` for command injection prevention
- **Parameter Validation**: Type checking and validation
- **Timeout Controls**: Execution time limits

## 🚀 Deployment Structure

### Docker Support
- **`Dockerfile`**: Container definition for the application
- **`docker-compose.yml`**: Multi-container deployment configuration

### Environment Configuration
- **`sample.env`**: Template for environment variables
- **`install.sh`**: Automated installation script

## 📈 Future Structure Considerations

### Planned Extensions
- **`src/omcp_py/core/`**: Core functionality modules (currently empty)
- **`src/omcp_py/tools/`**: Additional MCP tool implementations (currently empty)
- **`src/omcp_py/utils/`**: Utility functions (currently empty)

### Modular Design Benefits
- **Extensibility**: Easy to add new tools and functionality
- **Maintainability**: Clear separation of concerns
- **Testability**: Isolated components for focused testing
- **Security**: Layered security approach

---

*This document provides a comprehensive overview of the current codebase structure. For implementation details, see [Implementation Details](implementation.md).* 