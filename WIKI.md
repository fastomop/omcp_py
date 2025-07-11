# OMCP Python Sandbox - Complete Wiki

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Security](#security)
9. [Development](#development)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [Contributing](#contributing)
13. [FAQ](#faq)

---

## Overview

The OMCP Python Sandbox is a secure, Model Context Protocol (MCP) compliant Python code execution environment that provides isolated, containerized Python environments for safe code execution. Built with enterprise-grade security features, it enables AI agents and applications to execute Python code without compromising system security.

### Key Benefits
- **🔒 Enterprise Security**: Docker-based isolation with comprehensive security measures
- **🚀 MCP Compliance**: Full Model Context Protocol specification compliance
- **⚡ Fast Execution**: Optimized for performance with resource management
- **🛠️ Developer Friendly**: Multiple server implementations and debugging tools
- **📊 Production Ready**: Robust error handling, logging, and monitoring

### Use Cases
- **AI Agent Code Execution**: Safe Python code execution for AI assistants
- **Educational Platforms**: Isolated coding environments for learning
- **Code Testing**: Secure testing environments for untrusted code
- **API Services**: Python execution as a service
- **Development Tools**: Local development with sandboxed execution

---

## Architecture

### System Overview
```
┌─────────────────┐    JSON-RPC    ┌──────────────────┐    Docker API    ┌─────────────────┐
│   MCP Client    │ ──────────────▶ │  FastMCP Server  │ ────────────────▶ │ Docker Engine   │
│   (Agent/App)   │                │ (server_fastmcp) │                  │                 │
└─────────────────┘                └──────────────────┘                  └─────────────────┘
         │                                   │                                     │
         │                                   │                                     │
         ▼                                   ▼                                     ▼
┌─────────────────┐                ┌──────────────────┐                ┌─────────────────┐
│   MCP Inspector │                │ Sandbox Manager  │                │ Python Sandbox  │
│   (Web UI)      │                │ (src/omcp_py/)   │                │ (Container)     │
└─────────────────┘                └──────────────────┘                └─────────────────┘
```

### Component Details

#### 1. MCP Client Layer
- **Purpose**: External applications or AI agents that need to execute Python code
- **Protocol**: JSON-RPC over stdio (MCP specification)
- **Tools**: create_sandbox, execute_python_code, install_package, list_sandboxes, remove_sandbox

#### 2. FastMCP Server Layer
- **Implementation**: `server_fastmcp.py`
- **Framework**: FastMCP with decorator-based tool definitions
- **Features**: Enhanced security, timeout handling, structured logging
- **Transport**: stdio (MCP standard)

#### 3. Sandbox Manager Layer
- **Location**: `src/omcp_py/core/sandbox.py`
- **Responsibilities**: 
  - Docker container lifecycle management
  - Resource allocation and cleanup
  - Security policy enforcement
  - Error handling and recovery

#### 4. Docker Container Layer
- **Base Image**: `python:3.11-slim`
- **Security**: Enhanced Docker security options
- **Isolation**: Complete network and filesystem isolation
- **Resources**: CPU and memory limits

## Database Integration and OMOP CDM Roadmap

### Current State
- Sandbox metadata is now persisted in a PostgreSQL database using SQLAlchemy, ensuring robust tracking and management of sandboxes across server restarts.

### Future Direction: OMOP CDM Integration
- The project aims to enable sandboxed Python code to securely connect to and query OMOP Common Data Model (CDM) data stored in PostgreSQL.
- This will support clinical data science, analytics, and AI agents running code against OMOP CDM in a secure, auditable environment.
- Planned features include:
  - Secure credential injection for sandboxes to access OMOP CDM tables
  - Example tools and code snippets for querying OMOP CDM (e.g., patient counts, cohort definitions)
  - Fine-grained access controls and auditing for database queries
  - Documentation and best practices for OMOP CDM analytics in the sandbox

For more details and to contribute to this direction, see the Contributing section below.

---

## Features

### Core Functionality

#### Sandbox Management
- **Create Sandboxes**: Instantiate isolated Python environments
- **List Sandboxes**: Monitor active sandboxes with status information
- **Remove Sandboxes**: Clean up sandboxes with force options
- **Auto-cleanup**: Automatic removal of inactive sandboxes

#### Code Execution
- **Python Code Execution**: Run arbitrary Python code in isolated containers
- **Package Installation**: Install Python packages using pip
- **Output Capture**: Capture stdout, stderr, and exit codes
- **JSON Output**: Automatic JSON parsing for structured data return

#### Security Features
- **Container Isolation**: Each sandbox runs in a separate Docker container
- **User Isolation**: Containers run as non-root user (`sandboxuser`)
- **Read-only Filesystem**: Prevents file system modifications
- **Dropped Capabilities**: Removes all Linux capabilities
- **No Privilege Escalation**: Prevents privilege escalation attacks
- **Command Injection Protection**: Proper command escaping with `shlex.quote`
- **Resource Limits**: CPU, memory, and execution time limits
- **Network Isolation**: Complete network isolation (`network_mode="none"`)
- **Timeout Controls**: Configurable execution timeouts
- **Input Validation**: Comprehensive input sanitization

### Development Tools

#### MCP Inspector Integration
- **Web-based Interface**: Interactive tool testing at `http://127.0.0.1:6274`
- **Real-time Testing**: Test all MCP tools with live feedback
- **Request/Response Inspection**: View JSON-RPC messages
- **Error Debugging**: Detailed error messages and stack traces
- **Performance Monitoring**: Track execution times and resource usage
- **Session Persistence**: Save and load test scenarios

#### Multiple Server Implementations
- **Standard MCP Server**: Full MCP specification compliance (`server.py`)
- **FastMCP Server**: Enhanced implementation with decorators (`server_fastmcp.py`)

---

## Installation

### Prerequisites

#### System Requirements
- **Operating System**: Linux, macOS, or Windows (with Docker support)
- **Python**: 3.10 or higher
- **Docker**: Latest stable version with sudo access
- **Node.js**: 18.0.0 or higher (for MCP Inspector)

#### Package Managers
- **uv**: Modern Python package manager (recommended)
- **pip**: Traditional Python package manager (alternative)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py
```

#### 2. Install Python Dependencies
```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

#### 3. Install Node.js (for MCP Inspector)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# macOS
brew install node

# Windows
# Download from https://nodejs.org/
```

#### 4. Verify Installation
```bash
# Check Python dependencies
python -c "import mcp, docker, flask; print('Dependencies OK')"

# Check Node.js
node --version  # Should be 18.0.0 or higher

# Check Docker
sudo docker ps  # Should show Docker is running
```

### Environment Configuration

#### Optional Environment Variables
Create a `.env` file in the project root:
```env
# Sandbox Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=10
DOCKER_IMAGE=python:3.11-slim

# Logging
DEBUG=false
LOG_LEVEL=INFO

# Security
SANDBOX_USER=sandboxuser
SANDBOX_MEMORY_LIMIT=512m
SANDBOX_CPU_LIMIT=0.5
```

---

## Quick Start

### 1. Start the Server
```bash
cd /path/to/omcp_py
source .venv/bin/activate  # If using virtual environment
uv run server_fastmcp.py
```

### 2. Launch MCP Inspector (Optional)
In a new terminal:
```bash
cd /path/to/omcp_py
npx @modelcontextprotocol/inspector uv run server_fastmcp.py
```

### 3. Access Web Interface
Open your browser to: `http://127.0.0.1:6274`

### 4. Test Basic Functionality
In the MCP Inspector:
1. **Create a sandbox**: Use `create_sandbox` tool
2. **Execute code**: Use `execute_python_code` with `print("Hello World!")`
3. **Install package**: Use `install_package` with `requests`
4. **List sandboxes**: Use `list_sandboxes` to see active sandboxes
5. **Clean up**: Use `remove_sandbox` when done

---

## Usage Guide

### Basic Usage Patterns

#### 1. Creating and Using a Sandbox
```python
# Create a new sandbox
result = await mcp.create_sandbox(timeout=300)
sandbox_id = result["sandbox_id"]

# Execute Python code
code_result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="print('Hello from sandbox!')",
    timeout=30
)

# Clean up
await mcp.remove_sandbox(sandbox_id=sandbox_id, force=True)
```

#### 2. Installing and Using Packages
```python
# Install a package
await mcp.install_package(
    sandbox_id=sandbox_id,
    package="numpy==1.24.0",
    timeout=60
)

# Use the installed package
code_result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="""
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print({"sum": arr.sum(), "mean": arr.mean()})
""",
    timeout=30
)
```

#### 3. Working with Multiple Sandboxes
```python
# Create multiple sandboxes
sandbox1 = await mcp.create_sandbox()
sandbox2 = await mcp.create_sandbox()

# List all sandboxes
sandboxes = await mcp.list_sandboxes(include_inactive=False)

# Execute code in different sandboxes
await mcp.execute_python_code(sandbox_id=sandbox1["sandbox_id"], code="print('Sandbox 1')")
await mcp.execute_python_code(sandbox_id=sandbox2["sandbox_id"], code="print('Sandbox 2')")
```

### Advanced Usage

#### 1. Error Handling
```python
try:
    result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code="import nonexistent_module",
        timeout=30
    )
    if not result["success"]:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Exception: {e}")
```

#### 2. Timeout Management
```python
# Set appropriate timeouts for different operations
await mcp.create_sandbox(timeout=300)  # 5 minutes for creation
await mcp.install_package(sandbox_id=sandbox_id, package="large_package", timeout=120)  # 2 minutes for installation
await mcp.execute_python_code(sandbox_id=sandbox_id, code="complex_calculation()", timeout=60)  # 1 minute for execution
```

#### 3. Resource Monitoring
```python
# Monitor sandbox usage
sandboxes = await mcp.list_sandboxes(include_inactive=True)
for sandbox in sandboxes["sandboxes"]:
    print(f"Sandbox {sandbox['id']}: Created {sandbox['created_at']}, Last used {sandbox['last_used']}")
```

---

## API Reference

### Tool Specifications

#### `create_sandbox`
Creates a new isolated Python environment.

**Parameters:**
- `timeout` (optional, int): Sandbox timeout in seconds (default: 300)

**Returns:**
```json
{
  "success": true,
  "sandbox_id": "sandbox_abc123",
  "created_at": "2024-01-01T12:00:00",
  "last_used": "2024-01-01T12:00:00"
}
```

#### `execute_python_code`
Executes Python code in a sandbox.

**Parameters:**
- `sandbox_id` (required, string): The sandbox identifier
- `code` (required, string): Python code to execute
- `timeout` (optional, int): Execution timeout in seconds (default: 30)

**Returns:**
```json
{
  "success": true,
  "output": "Hello from sandbox!",
  "error": null,
  "exit_code": 0
}
```

#### `install_package`
Installs a Python package in a sandbox.

**Parameters:**
- `sandbox_id` (required, string): The sandbox identifier
- `package` (required, string): Package name and version (e.g., "numpy==1.24.0")
- `timeout` (optional, int): Installation timeout in seconds (default: 60)

**Returns:**
```json
{
  "success": true,
  "output": {"status": "success", "message": "Package installed successfully"},
  "error": null,
  "exit_code": 0
}
```

#### `list_sandboxes`
Lists all active sandboxes.

**Parameters:**
- `include_inactive` (optional, boolean): Include inactive sandboxes (default: false)

**Returns:**
```json
{
  "success": true,
  "sandboxes": [
    {
      "id": "sandbox_abc123",
      "created_at": "2024-01-01T12:00:00",
      "last_used": "2024-01-01T12:00:00"
    }
  ],
  "count": 1
}
```

#### `remove_sandbox`
Removes a sandbox.

**Parameters:**
- `sandbox_id` (required, string): The sandbox identifier
- `force` (optional, boolean): Force removal of active sandboxes (default: false)

**Returns:**
```json
{
  "success": true,
  "message": "Sandbox sandbox_abc123 removed successfully"
}
```

### Error Responses

All tools return error responses in the following format:
```json
{
  "success": false,
  "error": "Error description"
}
```

Common error types:
- **Sandbox not found**: The specified sandbox ID doesn't exist
- **Timeout**: Operation exceeded the specified timeout
- **Invalid input**: Malformed or invalid input parameters
- **Resource limits**: Exceeded CPU or memory limits
- **Docker errors**: Container creation or management failures

---

## Security

### Security Architecture

#### Container Security
Each sandbox runs in a Docker container with enhanced security options:

```python
# Docker run options for maximum security
container_config = {
    "image": "python:3.11-slim",
    "user": "sandboxuser",  # Non-root user
    "read_only": True,  # Read-only filesystem
    "tmpfs": {  # Temporary writable areas
        "/tmp": "size=100m",
        "/sandbox": "size=100m"
    },
    "cap_drop": ["ALL"],  # Drop all capabilities
    "security_opt": ["no-new-privileges"],  # No privilege escalation
    "network_mode": "none",  # No network access
    "mem_limit": "512m",  # Memory limit
    "cpus": "0.5",  # CPU limit
    "auto_remove": True  # Auto-cleanup
}
```

#### Code Execution Security
- **Command Injection Protection**: Uses `shlex.quote` for proper escaping
- **List-form Commands**: Prevents shell injection attacks
- **Input Validation**: Comprehensive input sanitization
- **Error Isolation**: Errors don't affect other sandboxes

#### Resource Management
- **Maximum Sandboxes**: Configurable limit prevents resource exhaustion
- **Timeout Controls**: Automatic cleanup of long-running operations
- **Memory Limits**: 512MB per sandbox (configurable)
- **CPU Limits**: Restricted CPU usage (configurable)

### Security Best Practices

#### 1. Regular Updates
- Keep Docker images updated
- Monitor security advisories
- Update dependencies regularly

#### 2. Access Control
- Use non-root users in containers
- Implement proper authentication for MCP clients
- Monitor and log all operations

#### 3. Network Security
- Use network isolation for sandboxes
- Implement firewall rules
- Monitor network traffic

#### 4. Resource Monitoring
- Monitor container resource usage
- Set appropriate limits
- Implement alerting for resource exhaustion

---

## Development

### Project Structure
```
omcp_py/
├── src/
│   └── omcp_py/
│       ├── core/
│       │   └── sandbox.py          # Sandbox management
│       ├── tools/
│       │   ├── execution_tools.py  # Code execution tools
│       │   └── sandbox_tools.py    # Sandbox management tools
│       └── utils/
│           └── config.py           # Configuration management
├── server.py                       # Standard MCP server
├── server_fastmcp.py               # FastMCP server (enhanced)
├── sandbox_server.py               # Flask sandbox server
├── Dockerfile                      # Docker image definition
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project configuration
└── README.md                       # Project documentation
```

### Development Setup

#### 1. Clone and Setup
```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py
uv pip install -r requirements.txt
```

#### 2. Install Development Dependencies
```bash
uv pip install -r requirements.txt[dev]
```

#### 3. Run Tests
```bash
pytest
```

#### 4. Code Formatting
```bash
black .
ruff check .
```

### Development Workflow

#### 1. Feature Development
1. Create a feature branch
2. Implement changes
3. Add tests
4. Run linting and formatting
5. Submit pull request

#### 2. Testing
- **Unit Tests**: Test individual components
- **Integration Tests**: Test MCP protocol compliance
- **Security Tests**: Test security features
- **Performance Tests**: Test resource usage

#### 3. Debugging
- **MCP Inspector**: Use for interactive debugging
- **Logs**: Check server logs for errors
- **Docker**: Inspect containers for issues

### Code Style

#### Python
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings

#### Example
```python
from typing import Dict, Any, Optional

async def create_sandbox(timeout: Optional[int] = 300) -> Dict[str, Any]:
    """Create a new Python sandbox environment.
    
    Args:
        timeout: Optional timeout for the sandbox in seconds (default: 300)
    
    Returns:
        Dict containing sandbox information
        
    Raises:
        SandboxError: If sandbox creation fails
    """
    # Implementation here
    pass
```

---

## Deployment

### Production Deployment

#### 1. Docker Deployment
```dockerfile
# Use the provided Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "server_fastmcp.py"]
```

#### 2. Systemd Service
Create `/etc/systemd/system/omcp-sandbox.service`:
```ini
[Unit]
Description=OMCP Python Sandbox Server
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=omcp
WorkingDirectory=/opt/omcp_py
Environment=PATH=/opt/omcp_py/.venv/bin
ExecStart=/opt/omcp_py/.venv/bin/python server_fastmcp.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Environment Configuration
```bash
# Production environment variables
export SANDBOX_TIMEOUT=600
export MAX_SANDBOXES=50
export LOG_LEVEL=WARNING
export DEBUG=false
```

### Monitoring and Logging

#### 1. Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/omcp-sandbox.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Health Checks
```python
# Health check endpoint
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "sandboxes": len(sandbox_manager.sandboxes),
        "docker_status": docker_client.ping()
    }
```

#### 3. Metrics Collection
- **Sandbox Count**: Number of active sandboxes
- **Execution Time**: Average execution times
- **Error Rates**: Error frequency and types
- **Resource Usage**: CPU and memory usage

### Scaling Considerations

#### 1. Horizontal Scaling
- Deploy multiple server instances
- Use load balancer for distribution
- Implement shared state management

#### 2. Resource Management
- Monitor Docker daemon resources
- Implement sandbox limits per instance
- Use resource quotas

#### 3. High Availability
- Deploy across multiple nodes
- Implement health checks
- Use container orchestration (Kubernetes)

---

## Troubleshooting

### Common Issues

#### 1. Docker Issues
**Problem**: Docker permission errors
```bash
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Problem**: Docker daemon not running
```bash
# Solution: Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### 2. MCP Inspector Issues
**Problem**: Inspector not starting
```bash
# Check Node.js version
node --version  # Should be 18.0.0+

# Reinstall inspector
npm uninstall -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector --version
```

**Problem**: Port already in use
```bash
# Check what's using the port
ss -tlnp | grep 6274

# Kill the process if needed
sudo kill -9 <PID>
```

#### 3. Sandbox Issues
**Problem**: Sandbox creation fails
```bash
# Check Docker resources
sudo docker system df
sudo docker system prune

# Check logs
docker logs <container_id>
```

**Problem**: Code execution timeout
```bash
# Increase timeout values
export SANDBOX_TIMEOUT=600
export EXECUTION_TIMEOUT=120
```

#### 4. Performance Issues
**Problem**: Slow sandbox creation
```bash
# Optimize Docker
sudo docker system prune -a
sudo docker builder prune

# Use faster base image
export DOCKER_IMAGE=python:3.11-alpine
```

### Debugging Tools

#### 1. MCP Inspector
- Use for interactive debugging
- View request/response data
- Test individual tools

#### 2. Docker Commands
```bash
# List containers
sudo docker ps -a

# Inspect container
sudo docker inspect <container_id>

# View container logs
sudo docker logs <container_id>

# Execute in container
sudo docker exec -it <container_id> /bin/bash
```

#### 3. System Monitoring
```bash
# Monitor resource usage
htop
iotop

# Monitor Docker
sudo docker stats

# Monitor logs
tail -f /var/log/omcp-sandbox.log
```

### Performance Optimization

#### 1. Container Optimization
- Use Alpine Linux base images
- Implement container reuse
- Optimize layer caching

#### 2. Resource Optimization
- Tune memory limits
- Optimize CPU allocation
- Implement connection pooling

#### 3. Network Optimization
- Use local Docker registry
- Optimize image pulls
- Implement caching

---

## Contributing

### Getting Started

#### 1. Fork the Repository
1. Go to https://github.com/fastomop/omcp_py
2. Click "Fork" to create your copy

#### 2. Clone Your Fork
```bash
git clone https://github.com/yourusername/omcp_py.git
cd omcp_py
```

#### 3. Set Up Development Environment
```bash
# Install dependencies
uv pip install -r requirements.txt[dev]

# Set up pre-commit hooks
pre-commit install
```

### Development Guidelines

#### 1. Code Standards
- Follow PEP 8 style guide
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features

#### 2. Commit Guidelines
- Use conventional commit messages
- Keep commits focused and atomic
- Include tests with new features
- Update documentation as needed

#### 3. Pull Request Process
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request
6. Address review feedback

### Testing

#### 1. Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_sandbox.py

# Run with coverage
pytest --cov=omcp_py
```

#### 2. Writing Tests
```python
import pytest
from omcp_py.core.sandbox import SandboxManager

@pytest.fixture
def sandbox_manager():
    return SandboxManager()

def test_create_sandbox(sandbox_manager):
    sandbox_id = sandbox_manager.create_sandbox()
    assert sandbox_id is not None
    assert sandbox_id in sandbox_manager.sandboxes
```

### Documentation

#### 1. Code Documentation
- Use Google-style docstrings
- Include type hints
- Document exceptions
- Provide usage examples

#### 2. API Documentation
- Document all MCP tools
- Include request/response examples
- Document error codes
- Provide troubleshooting guides

---

## FAQ

### General Questions

#### Q: What is MCP?
**A**: Model Context Protocol (MCP) is a specification for AI agents to interact with external tools and data sources. It provides a standardized way for AI assistants to execute code, access databases, and interact with external services.

#### Q: Why use Docker for sandboxing?
**A**: Docker provides strong isolation between sandboxes, preventing code from accessing the host system or other sandboxes. It also offers resource limits, security options, and easy cleanup.

#### Q: Is this production-ready?
**A**: Yes, the OMCP Python Sandbox includes enterprise-grade security features, comprehensive error handling, and production deployment configurations. However, always test thoroughly in your specific environment.

### Security Questions

#### Q: How secure is the sandboxing?
**A**: The sandboxing uses multiple layers of security:
- Docker container isolation
- Non-root user execution
- Read-only filesystem
- Dropped Linux capabilities
- Network isolation
- Resource limits

#### Q: Can malicious code escape the sandbox?
**A**: While no security system is 100% perfect, the multiple layers of security make it extremely difficult for malicious code to escape. The system is designed to prevent privilege escalation and system access.

#### Q: What happens if a sandbox crashes?
**A**: Sandbox crashes are isolated and don't affect other sandboxes or the host system. The system automatically cleans up crashed containers and can restart new ones as needed.

### Performance Questions

#### Q: How fast is sandbox creation?
**A**: Sandbox creation typically takes 1-3 seconds, depending on system resources and Docker image caching. Subsequent operations within the same sandbox are very fast.

#### Q: How many sandboxes can I run simultaneously?
**A**: The number depends on your system resources. Each sandbox uses ~512MB of memory and limited CPU. The default limit is 10 sandboxes, but this is configurable.

#### Q: How do I optimize performance?
**A**: Performance can be optimized by:
- Using Alpine Linux base images
- Implementing container reuse
- Optimizing resource limits
- Using local Docker registry

### Integration Questions

#### Q: How do I integrate with my AI agent?
**A**: The OMCP Python Sandbox follows the MCP specification, so it can be integrated with any MCP-compliant AI agent. Simply configure the agent to use the server's stdio transport.

#### Q: Can I use this with other programming languages?
**A**: The current implementation is Python-specific, but the architecture could be extended to support other languages by creating additional sandbox images and tools.

#### Q: How do I monitor sandbox usage?
**A**: Use the `list_sandboxes` tool to monitor active sandboxes, and implement logging and metrics collection for production monitoring.

### Troubleshooting Questions

#### Q: Why does sandbox creation fail?
**A**: Common causes include:
- Docker not running
- Insufficient system resources
- Docker daemon issues
- Permission problems

#### Q: How do I debug code execution issues?
**A**: Use the MCP Inspector to test tools interactively, check Docker logs for container issues, and review server logs for detailed error information.

#### Q: What if the MCP Inspector doesn't work?
**A**: Ensure Node.js 18+ is installed, check that the server is running, verify the correct port is being used, and check for any firewall or network issues.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation
- Use the MCP Inspector for debugging

---

**Last Updated**: June 2024  
**Version**: 0.2.1  
**Maintainer**: FastMOP Team 