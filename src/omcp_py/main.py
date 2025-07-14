"""
FastMCP Python Sandbox Server

This module implements a Model Context Protocol (MCP) server using FastMCP for secure,
Docker-based Python code execution. It provides tools for creating isolated Python
environments, executing code safely, and managing sandbox lifecycle.

Architecture:
- FastMCP: Simplified MCP implementation using decorators
- Docker Sandboxing: Each sandbox runs in an isolated container with enhanced security
- Resource Management: Automatic cleanup and resource limits
- Error Handling: Comprehensive error handling and logging

Key Features:
- create_sandbox: Create new isolated Python environments
- list_sandboxes: List and manage active sandboxes
- remove_sandbox: Safely remove sandboxes with force option
- execute_python_code: Run Python code in isolated containers
- install_package: Install Python packages in sandboxes

Security Features:
- Network isolation (containers run with network_mode="none")
- Resource limits (CPU, memory)
- Timeout controls
- Input validation
- Auto-cleanup of inactive sandboxes
- Enhanced Docker security (read-only, dropped capabilities, tmpfs)
- User isolation (sandboxuser)
- Command escaping with shlex.quote

Usage:
    python server_fastmcp.py

Environment Variables:
    SANDBOX_TIMEOUT: Sandbox timeout in seconds (default: 300)
    MAX_SANDBOXES: Maximum number of sandboxes (default: 10)
    DOCKER_IMAGE: Docker image to use (default: python:3.11-slim)
    DEBUG: Enable debug mode (default: false)
    LOG_LEVEL: Logging level (default: INFO)
"""

import asyncio
import logging
import sys
from typing import Optional, Dict, Any
from fastmcp import FastMCP
from omcp_py.sandbox_manager import SandboxManager
from omcp_py.config import get_config
from shlex import quote
import requests

# Load configuration from environment variables
config = get_config()

# Configure logging to stderr (MCP convention) with structured format
logging.basicConfig(
    level=config.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr as per MCP specification
)

logger = logging.getLogger(__name__)

# Create FastMCP instance - this is the main server object
# FastMCP provides a simplified interface for creating MCP tools using decorators
mcp = FastMCP("Python Sandbox")

# Initialize the sandbox manager - handles Docker container lifecycle
# This is a singleton that manages all sandbox containers
sandbox_manager = SandboxManager(config)

@mcp.tool()
async def create_sandbox(timeout: Optional[int] = 300) -> Dict[str, Any]:
    """
    Create a new Python sandbox environment.
    
    This tool creates a new Docker container that will serve as an isolated
    Python execution environment. The container is configured with:
    - No network access (security)
    - Memory and CPU limits
    - Auto-removal when stopped
    - Enhanced security options (read-only, dropped capabilities)
    - User isolation (sandboxuser)
    - Temporary filesystem mounts
    
    Args:
        timeout: Optional timeout for the sandbox in seconds (default: 300)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if creation was successful
        - sandbox_id: Unique identifier for the created sandbox
        - created_at: ISO timestamp of creation
        - last_used: ISO timestamp of last usage
        - error: Error message if creation failed
    """
    try:
        # Create a new sandbox container using the sandbox manager
        sandbox_id = sandbox_manager.create_sandbox()
        
        # Retrieve the sandbox information to return creation details
        # We need to find the newly created sandbox in the list
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
        # Log the error for debugging
        logger.error(f"Failed to create sandbox: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def list_sandboxes(include_inactive: bool = False) -> Dict[str, Any]:
    """
    List all active Python sandboxes.
    
    This tool provides information about all sandbox containers, including
    their creation time and last usage time. Optionally filters out
    inactive sandboxes based on timeout configuration.
    
    Args:
        include_inactive: Whether to include inactive sandboxes (default: False)
                         Inactive sandboxes are those that haven't been used
                         within the configured timeout period.
    
    Returns:
        Dict containing:
        - success: Boolean indicating if listing was successful
        - sandboxes: List of sandbox information dictionaries
        - count: Number of sandboxes in the list
        - error: Error message if listing failed
    """
    try:
        # Get all sandboxes from the sandbox manager
        sandboxes = sandbox_manager.list_sandboxes()
        
        # Filter out inactive sandboxes if requested
        if not include_inactive:
            # Import datetime here to avoid circular imports
            from datetime import datetime
            # Filter sandboxes based on last usage time
            # Only include sandboxes that have been used recently
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
        # Log the error for debugging
        logger.error(f"Failed to list sandboxes: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def remove_sandbox(sandbox_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Remove a Python sandbox.
    
    This tool safely removes a sandbox container. By default, it only removes
    inactive sandboxes (those that haven't been used recently). The force
    parameter can be used to remove active sandboxes.
    
    Args:
        sandbox_id: The unique identifier of the sandbox to remove
        force: Whether to force removal of active sandboxes (default: False)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if removal was successful
        - message: Success message or error description
        - error: Error message if removal failed
    """
    try:
        # Validate that the sandbox exists
        if sandbox_id not in sandbox_manager.sandboxes:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found"
            }
        
        # Check if sandbox is active (unless force is True)
        if not force:
            # Import datetime here to avoid circular imports
            from datetime import datetime
            # Get the sandbox information
            sandbox = sandbox_manager.sandboxes[sandbox_id]
            # Check if sandbox has been used recently
            if (datetime.now() - sandbox["last_used"]).total_seconds() < config.sandbox_timeout:
                return {
                    "success": False,
                    "error": f"Sandbox {sandbox_id} is still active. Use force=True to remove it."
                }
        
        # Remove the sandbox using the sandbox manager
        # This will stop and remove the Docker container
        sandbox_manager.remove_sandbox(sandbox_id)
        
        # Return success response
        return {
            "success": True,
            "message": f"Sandbox {sandbox_id} removed successfully"
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to remove sandbox {sandbox_id}: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def execute_python_code(sandbox_id: str, code: str, timeout: Optional[int] = 30) -> Dict[str, Any]:
    """
    Execute Python code in a secure sandbox environment.
    
    This tool runs Python code inside an isolated Docker container. The code
    is executed with restricted permissions and resource limits. The output
    is captured and returned, with automatic JSON parsing for structured data.
    
    Args:
        sandbox_id: The unique identifier of the sandbox to execute code in
        code: The Python code to execute (must be non-empty string)
        timeout: Optional execution timeout in seconds (default: 30)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if execution was successful
        - output: The stdout output from code execution (parsed as JSON if possible)
        - error: The stderr output or error message
        - exit_code: The exit code from the Python process
    """
    try:
        # Validate that the code input is valid
        if not isinstance(code, str) or not code.strip():
            return {
                "success": False,
                "error": "Code must be a non-empty string"
            }
        

        
        # Execute the code in the specified sandbox with enhanced security
        result = sandbox_manager.execute_code(sandbox_id, code)
        print(result)
        # Return the execution results
        return {
            "output": result.output.decode(),
            "exit_code": result.exit_code
        }
    except requests.exceptions.ReadTimeout:
        # Handle timeout specifically
        logger.error(f"Code execution timed out in sandbox {sandbox_id}")
        return {
            "success": False,
            "error": "Code execution timed out"
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def install_package(sandbox_id: str, package: str, timeout: Optional[int] = 60) -> Dict[str, Any]:
    """
    Install a Python package in a sandbox.
    
    This tool installs Python packages inside a sandbox container using pip.
    It provides detailed error handling for installation failures and timeouts.
    The installation is done in a controlled manner with proper error reporting.
    
    Args:
        sandbox_id: The unique identifier of the sandbox to install the package in
        package: The package name and version (e.g., "numpy==1.24.0" or "pandas numpy")
        timeout: Optional installation timeout in seconds (default: 60)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if installation was successful
        - output: Installation output (parsed as JSON if possible)
        - error: Installation error or stderr output
        - exit_code: The exit code from the pip installation process
    """
    try:
        # Validate that the package input is valid
        if not isinstance(package, str) or not package.strip():
            return {
                "success": False,
                "error": "Package must be a non-empty string"
            }
        
        # Create Python code that will install the package using pip
        # This code runs inside the sandbox container
        code = f"""
import subprocess
import sys
try:
    # Install the package(s) using pip with timeout and output capture
    result = subprocess.run([sys.executable, '-m', 'pip', 'install'] + '''{package}'''.split(), 
                           timeout={timeout},
                           capture_output=True,
                           text=True)
    if result.returncode == 0:
        print({{"status": "success", "message": "Package(s) installed successfully", "stdout": result.stdout}})
    else:
        print({{"status": "error", "message": "Package installation failed", "stderr": result.stderr}})
        sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print({{"status": "error", "message": "Package installation timed out"}})
    sys.exit(1)
except Exception as e:
    print({{"status": "error", "message": f"Unexpected error: {{str(e)}}"}})
    sys.exit(1)
"""
        # Execute the installation code in the sandbox with enhanced security
        result = sandbox_manager.execute_code(sandbox_id, code)
        
        # Return the installation results
        return {
            "output": result.output,
            "exit_code": result.exit_code
        }
    except requests.exceptions.ReadTimeout:
        # Handle timeout specifically
        logger.error(f"Package installation timed out in sandbox {sandbox_id}")
        return {
            "success": False,
            "error": "Package installation timed out"
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to install package {package} in sandbox {sandbox_id}: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

# Main entry point for the FastMCP server
if __name__ == "__main__":
    # Log that the server is starting
    logger.info("Starting FastMCP sandbox server...")
    
    # Start the FastMCP server using stdio transport
    # This allows the server to communicate via stdin/stdout as per MCP specification
    mcp.run(transport="stdio") 