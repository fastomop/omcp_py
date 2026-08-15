"""Unit tests for host-enforced sandbox security policy."""

import threading
from types import SimpleNamespace
from unittest.mock import MagicMock

import docker
import pytest

from omcp_py.sandbox_manager import SandboxManager
from omcp_py.tools import sandbox_tools


def _config(**overrides):
    values = {
        "sandbox_timeout": 300,
        "max_sandboxes": 10,
        "docker_image": "fastomop/sandbox@sha256:" + "a" * 64,
        "sandbox_read_only": True,
        "sandbox_network": None,
        "allow_host_gateway": False,
        "require_pinned_image": False,
        "db_host": "db",
        "execution_default_timeout": 1,
        "execution_max_timeout": 5,
        "execution_max_output_bytes": 1024,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _manager(config=None):
    manager = SandboxManager.__new__(SandboxManager)
    manager.config = config or _config()
    manager.client = MagicMock()
    manager._lock = threading.RLock()
    manager._pending_creations = 0
    manager.compose_network = "omcp_py_default"
    manager.sandboxes = {}
    manager.db_available = False
    manager._cleanup_old_sandboxes = MagicMock()
    return manager


def _active_manager(**config_overrides):
    manager = _manager(_config(**config_overrides))
    container = MagicMock()
    container.id = "container-id"
    manager.sandboxes["sandbox-id"] = {
        "container": container,
        "created_at": MagicMock(),
        "last_used": MagicMock(),
        "execution_lock": threading.Lock(),
    }
    return manager, container


def test_network_is_none_even_when_compose_network_is_detected():
    manager = _manager()
    manager.client.containers.run.return_value = MagicMock()

    manager.create_sandbox()

    kwargs = manager.client.containers.run.call_args.kwargs
    assert kwargs["network_mode"] == "none"
    assert "extra_hosts" not in kwargs


@pytest.mark.parametrize("network_mode", ["host", "container:another-container"])
def test_unsafe_network_modes_are_forbidden(network_mode):
    manager = _manager(_config(sandbox_network=network_mode))

    with pytest.raises(RuntimeError, match="network modes are forbidden"):
        manager.create_sandbox()

    manager.client.containers.run.assert_not_called()


def test_missing_image_fails_closed_without_fallback():
    manager = _manager()
    manager.client.containers.run.side_effect = docker.errors.ImageNotFound("missing")

    with pytest.raises(docker.errors.ImageNotFound):
        manager.create_sandbox()

    manager.client.containers.run.assert_called_once()


def test_pinned_image_policy_rejects_mutable_tag():
    manager = _manager(
        _config(
            docker_image="fastomop/sandbox:python-3.11-slim",
            require_pinned_image=True,
        )
    )

    with pytest.raises(RuntimeError, match="pinned by digest"):
        manager.create_sandbox()


def test_pending_creation_counts_towards_capacity():
    manager = _manager(_config(max_sandboxes=1))
    manager._pending_creations = 1

    with pytest.raises(RuntimeError, match="Maximum number"):
        manager.create_sandbox()


def test_concurrent_execution_is_rejected():
    manager, _container = _active_manager()
    execution_lock = manager.sandboxes["sandbox-id"]["execution_lock"]
    execution_lock.acquire()
    try:
        result = manager.execute_code("sandbox-id", "print('second')")
    finally:
        execution_lock.release()

    assert result["exit_code"] == 75
    assert "already executing" in result["error"]


def test_output_limit_destroys_sandbox():
    manager, container = _active_manager(execution_max_output_bytes=10)
    manager.client.api.exec_create.return_value = {"Id": "exec-id"}
    manager.client.api.exec_start.return_value = iter([(b"x" * 11, None)])

    result = manager.execute_code("sandbox-id", "print('x' * 11)")

    assert result["exit_code"] == 137
    assert result["output"] == "x" * 10
    assert result["output_truncated"] is True
    assert result["sandbox_destroyed"] is True
    assert "sandbox-id" not in manager.sandboxes
    container.kill.assert_called_once()


def test_host_timeout_destroys_sandbox_even_if_guest_never_returns():
    manager, container = _active_manager()
    blocked = threading.Event()
    manager.client.api.exec_create.return_value = {"Id": "exec-id"}
    manager.client.api.exec_start.return_value = iter(lambda: blocked.wait(60), True)

    result = manager.execute_code("sandbox-id", "while True: pass", timeout=1)

    assert result["exit_code"] == 124
    assert result["timed_out"] is True
    assert result["sandbox_destroyed"] is True
    assert "sandbox-id" not in manager.sandboxes
    container.kill.assert_called_once()
    blocked.set()


def test_successful_streamed_execution_returns_bounded_metadata():
    manager, _container = _active_manager()
    manager.client.api.exec_create.return_value = {"Id": "exec-id"}
    manager.client.api.exec_start.return_value = iter([(b"ok\n", None)])
    manager.client.api.exec_inspect.return_value = {"ExitCode": 0}

    result = manager.execute_code("sandbox-id", "print('ok')")

    assert result == {
        "output": "ok\n",
        "exit_code": 0,
        "error": None,
        "timed_out": False,
        "output_truncated": False,
        "sandbox_destroyed": False,
    }


@pytest.mark.parametrize(
    "requirement",
    [
        "pandas",
        "pandas>=2",
        "pandas==2.2.0 --index-url https://example.test",
        "https://example.test/package.whl",
        "-r requirements.txt",
    ],
)
def test_package_policy_rejects_unpinned_options_and_sources(monkeypatch, requirement):
    monkeypatch.setattr(sandbox_tools.config, "package_install_enabled", True)
    monkeypatch.setattr(sandbox_tools.config, "sandbox_network", "restricted-egress")
    monkeypatch.setattr(
        sandbox_tools.config, "package_allowlist", frozenset({"pandas"})
    )

    assert sandbox_tools._validate_package_requirement(requirement)


def test_package_policy_accepts_one_exact_allowlisted_requirement(monkeypatch):
    monkeypatch.setattr(sandbox_tools.config, "package_install_enabled", True)
    monkeypatch.setattr(sandbox_tools.config, "sandbox_network", "restricted-egress")
    monkeypatch.setattr(
        sandbox_tools.config, "package_allowlist", frozenset({"pandas"})
    )

    assert sandbox_tools._validate_package_requirement("pandas==2.2.3") is None


def test_package_installation_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(sandbox_tools.config, "package_install_enabled", False)

    assert (
        sandbox_tools._validate_package_requirement("pandas==2.2.3")
        == "Package installation is disabled by policy"
    )
