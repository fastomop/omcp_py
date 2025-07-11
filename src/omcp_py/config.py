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
        docker_image=os.getenv("DOCKER_IMAGE", "python:3.11-slim"),
        sandbox_base_url=os.getenv("SANDBOX_BASE_URL"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_user=os.getenv("DB_USER", "omcp_user"),
        db_password=os.getenv("DB_PASSWORD", "omcp_pass"),
        db_name=os.getenv("DB_NAME", "omcp_db")
    )
