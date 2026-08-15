import logging
from typing import Optional, Dict, Any
from omcp_py.core.globals import sandbox_manager, config

logger = logging.getLogger(__name__)


async def ping() -> str:
    return "pong"


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
        sandbox_info = next(
            (s for s in sandbox_manager.list_sandboxes() if s["id"] == sandbox_id), None
        )

        # Validate that we can retrieve the sandbox info
        if not sandbox_info:
            raise Exception("Failed to get sandbox information after creation")

        # Return success response with sandbox details
        return {
            "success": True,
            "sandbox_id": sandbox_id,
            "created_at": sandbox_info["created_at"],
            "last_used": sandbox_info["last_used"],
        }
    except Exception as e:
        logger.error(f"Failed to create sandbox: {e}")
        return {"success": False, "error": str(e)}


async def list_sandboxes(include_inactive: bool = False) -> Dict[str, Any]:
    """
    List all active Python sandboxes.

    Args:
        include_inactive: Whether to include inactive sandboxes (default: False)

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
            from datetime import datetime

            sandboxes = [
                s
                for s in sandboxes
                if (
                    datetime.now() - datetime.fromisoformat(s["last_used"])
                ).total_seconds()
                < config.sandbox_timeout
            ]

        return {"success": True, "sandboxes": sandboxes, "count": len(sandboxes)}
    except Exception as e:
        logger.error(f"Failed to list sandboxes: {e}")
        return {"success": False, "error": str(e)}


async def remove_sandbox(sandbox_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Remove a Python sandbox.

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
        if sandbox_id not in sandbox_manager.sandboxes:
            return {"success": False, "error": f"Sandbox {sandbox_id} not found"}

        if not force:
            from datetime import datetime

            sandbox = sandbox_manager.sandboxes[sandbox_id]
            if (
                datetime.now() - sandbox["last_used"]
            ).total_seconds() < config.sandbox_timeout:
                return {
                    "success": False,
                    "error": f"Sandbox {sandbox_id} is still active. Use force=True to remove it.",
                }

        sandbox_manager.remove_sandbox(sandbox_id)

        return {
            "success": True,
            "message": f"Sandbox {sandbox_id} removed successfully",
        }
    except Exception as e:
        logger.error(f"Failed to remove sandbox {sandbox_id}: {e}")
        return {"success": False, "error": str(e)}


async def execute_python_code(
    sandbox_id: str,
    python_code: Optional[str] = None,
    code: Optional[str] = None,
    timeout: Optional[int] = 30,
) -> Dict[str, Any]:
    """
    Execute Python code in a secure sandbox environment.

    Args:
        sandbox_id: The unique identifier of the sandbox to execute code in
        code: The Python code to execute (must be non-empty string)
        timeout: Optional execution timeout in seconds (default: 30)

    Returns:
        Dict containing:
        - success: Boolean indicating if execution was successful
        - output: The stdout output from code execution
        - error: The stderr output or error message
        - exit_code: The exit code from the Python process
    """
    try:
        code_text = python_code if python_code is not None else code
        if not isinstance(code_text, str) or not code_text.strip():
            return {
                "success": False,
                "error": "Python code must be a non-empty string",
                "exit_code": 1,
            }

        # Execute the code in the specified sandbox with enhanced security
        # Enable code validation for user-provided code
        exec_result = sandbox_manager.execute_code(
            sandbox_id, code_text, timeout=timeout, validate=True
        )

        # exec_result is expected to be a dict with keys: output (bytes or str), exit_code (int), error (str|None)
        output_raw = exec_result.get("output")
        exit_code = exec_result.get("exit_code")
        error = exec_result.get("error")

        if isinstance(output_raw, (bytes, bytearray)):
            try:
                output_text = output_raw.decode(errors="replace")
            except Exception:
                output_text = str(output_raw)
        else:
            output_text = "" if output_raw is None else str(output_raw)

        return {
            "success": (exit_code == 0),
            "output": output_text,
            "error": error,
            "exit_code": exit_code,
        }
    except Exception as e:
        logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
        return {"success": False, "error": str(e)}


async def install_package(
    sandbox_id: str, package: str, timeout: Optional[int] = 60
) -> Dict[str, Any]:
    """
    Install a Python package in a sandbox.

    Args:
        sandbox_id: The unique identifier of the sandbox to install the package in
        package: The package name and version
        timeout: Optional installation timeout in seconds (default: 60)

    Returns:
        Dict containing:
        - success: Boolean indicating if installation was successful
        - output: Installation output
        - error: Installation error or stderr output
        - exit_code: The exit code
    """
    try:
        if not isinstance(package, str) or not package.strip():
            return {"success": False, "error": "Package must be a non-empty string"}

        code = f"""
import os
import subprocess
import sys
try:
    os.makedirs("/sandbox/packages", exist_ok=True)
    cmd = [sys.executable, "-m", "pip", "install", "--no-input", "--disable-pip-version-check", "--target", "/sandbox/packages"]
    cmd += {package!r}.split()
    result = subprocess.run(cmd, timeout={timeout}, capture_output=True, text=True)
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
        result = sandbox_manager.execute_code(sandbox_id, code)

        return {
            "success": result.get("exit_code") == 0,
            "output": result.get("output"),
            "exit_code": result.get("exit_code"),
            "error": result.get("error"),
        }
    except Exception as e:
        logger.error(
            f"Failed to install package {package} in sandbox {sandbox_id}: {e}"
        )
        return {"success": False, "error": str(e)}


def register(mcp):
    """Register all sandbox tools with the MCP instance."""
    mcp.tool()(ping)
    mcp.tool()(create_sandbox)
    mcp.tool()(list_sandboxes)
    mcp.tool()(remove_sandbox)
    mcp.tool()(execute_python_code)
    mcp.tool()(install_package)
