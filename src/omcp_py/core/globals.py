"""Global singleton instances for the application."""
from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager

# Load configuration
config = get_config()

# Initialize singleton sandbox manager
sandbox_manager = SandboxManager(config)
