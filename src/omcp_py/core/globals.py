"""Application-wide configuration and lazily initialized services."""

from __future__ import annotations

import threading
from typing import Optional

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager

config = get_config()


class LazySandboxManager:
    """Create the Docker-backed manager only when a sandbox tool needs it.

    Query-only MCP deployments and imports must not require a running Docker
    daemon. Attribute access preserves the previous ``sandbox_manager`` API.
    """

    def __init__(self) -> None:
        self._instance: Optional[SandboxManager] = None
        self._lock = threading.Lock()

    @property
    def initialized(self) -> bool:
        """Return whether the Docker-backed manager has been constructed."""
        return self._instance is not None

    def get(self) -> SandboxManager:
        """Return the manager, constructing it exactly once on first use."""
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = SandboxManager(config)
        return self._instance

    def __getattr__(self, name: str):
        return getattr(self.get(), name)


sandbox_manager = LazySandboxManager()
