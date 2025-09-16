"""
Configuration management for the MCP sandbox server.

Loads configuration from environment variables with sensible defaults
for sandbox timeouts, limits, and logging settings.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

@dataclass
class SandboxConfig:
    """Configuration settings for sandbox behavior and limits."""
    sandbox_timeout: int
    max_sandboxes: int  
    docker_image: str
    sandbox_base_url: Optional[str]
    debug: bool
    log_level: str
    # Sandbox runtime options
    allow_host_gateway: bool
    sandbox_read_only: bool
    sandbox_network: Optional[str]
    # Database config
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

def get_config() -> SandboxConfig:
    """Load and return configuration from environment variables."""
    return SandboxConfig(
        sandbox_timeout=int(os.getenv("SANDBOX_TIMEOUT", "300")),
        max_sandboxes=int(os.getenv("MAX_SANDBOXES", "10")),
    docker_image=os.getenv("DOCKER_IMAGE", "fastomop/sandbox:python-3.11-slim"),
        sandbox_base_url=os.getenv("SANDBOX_BASE_URL"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    # Sandbox runtime options (use host-gateway to allow containers to reach host)
    allow_host_gateway=os.getenv("SANDBOX_ALLOW_HOST_GATEWAY", "true").lower() == "true",
    sandbox_read_only=os.getenv("SANDBOX_READ_ONLY", "false").lower() == "true",
    sandbox_network=os.getenv("SANDBOX_NETWORK", None),
    # Defaults chosen to match the included docker image/service configuration
    db_host=os.getenv("DB_HOST", "db"),
    db_port=int(os.getenv("DB_PORT", "5432")),
    db_user=os.getenv("DB_USER", "omcp"),
    db_password=os.getenv("DB_PASSWORD", "postgres"),
    db_name=os.getenv("DB_NAME", "omcp")
    )
