"""
FastMCP Python Sandbox Server

This module implements a Model Context Protocol (MCP) server using FastMCP for secure,
Docker-based Python code execution. It provides tools for creating isolated Python
environments, executing code safely, and managing sandbox lifecycle.

Architecture:
- FastMCP: Simplified MCP implementation using decorators
- Modular Tools: Tools are organized in src/omcp_py/tools/
- Docker Sandboxing: Each sandbox runs in an isolated container
"""

import logging
import sys
from fastmcp import FastMCP
from omcp_py.core.globals import config
import omcp_py.tools.sandbox_tools as sandbox_tools
import omcp_py.tools.omop_tools as omop_tools
import omcp_py.tools.query_tools as query_tools

# Configure logging to stderr (MCP convention) with structured format
logging.basicConfig(
    level=config.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("Python Sandbox")

# Log startup info
logger.info(
    "Sandbox network config: SANDBOX_NETWORK=%s, ALLOW_HOST_GATEWAY=%s; "
    "Docker discovery is deferred until first sandbox use",
    config.sandbox_network,
    config.allow_host_gateway,
)

# Register tools from modules
sandbox_tools.register(mcp)
omop_tools.register(mcp)
query_tools.register(mcp)


def main() -> None:
    """Main entry point for the FastMCP server."""
    logger.info("Starting FastMCP sandbox server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
