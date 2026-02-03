import os
import pytest


def require_integration() -> None:
    """Skip integration tests unless explicitly enabled."""
    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("Integration tests disabled (set RUN_INTEGRATION_TESTS=1 to enable)")
