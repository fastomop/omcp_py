"""
Sandbox Manager - Core Docker container management for Python sandboxes.

Handles creation, execution, and cleanup of isolated Python environments
using Docker containers with security restrictions and resource limits.
"""

import uuid
import docker
from docker.types import Ulimit
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import os
import queue
import threading
from omcp_py.core.db import get_session, Sandbox as DBSandbox, create_tables

logger = logging.getLogger(__name__)


class SandboxManager:
    """Manages Docker-based Python sandboxes with automatic cleanup and enhanced security."""

    def __init__(self, config):
        self.config = config
        self.client = docker.DockerClient(
            base_url=os.getenv("DOCKER_HOST", "unix://var/run/docker.sock")
        )
        try:
            self.client.ping()
        except docker.errors.DockerException as e:
            logger.error("Docker daemon is unavailable: %s", e)
            raise
        self._lock = threading.RLock()
        self._pending_creations = 0
        # Try to detect a docker-compose project network to attach sandboxes to.
        # This allows the sandbox to resolve compose service names like 'db'.
        self.compose_network = None
        try:
            # Try to find a docker network that contains a DB/container for this project.
            nets = list(self.client.networks.list())
            for n in nets:
                try:
                    attrs = n.attrs
                    containers = attrs.get("Containers") or {}
                    for cid in containers.keys():
                        try:
                            c = self.client.containers.get(cid)
                            # Check for common DB indicators: service label or container name or image
                            labels = c.labels or {}
                            name = (c.name or "").lower()
                            img = (
                                getattr(c, "image", None)
                                and getattr(c.image, "tags", [])
                            ) or []
                            if (
                                labels.get("com.docker.compose.service") == "db"
                                or "db" == name
                                or any("postgres" in t for t in img)
                            ):
                                self.compose_network = n.name
                                raise StopIteration
                        except Exception:
                            continue
                except StopIteration:
                    break
                except Exception:
                    continue
        except Exception:
            self.compose_network = None
        self.sandboxes: Dict[str, dict] = {}
        self.db_available = True
        try:
            create_tables()
            self._load_sandboxes_from_db()
        except Exception as e:
            logger.warning(f"Database unavailable, running without persistence: {e}")
            self.db_available = False
        self._cleanup_old_sandboxes()  # Clean up on startup

    def _load_sandboxes_from_db(self):
        if not self.db_available:
            return
        session = get_session()
        try:
            db_sandboxes = session.query(DBSandbox).all()
            for db_sandbox in db_sandboxes:
                self.sandboxes[db_sandbox.id] = {
                    "container": None,  # Not restoring running containers
                    "created_at": db_sandbox.created_at,
                    "last_used": db_sandbox.last_used,
                    "execution_lock": threading.Lock(),
                }
        finally:
            session.close()

    def _save_sandbox_to_db(self, sandbox_id, created_at, last_used):
        if not self.db_available:
            return
        session = get_session()
        try:
            db_sandbox = session.query(DBSandbox).filter_by(id=sandbox_id).first()
            if not db_sandbox:
                db_sandbox = DBSandbox(
                    id=sandbox_id, created_at=created_at, last_used=last_used
                )
                session.add(db_sandbox)
            else:
                db_sandbox.last_used = last_used
            session.commit()
        finally:
            session.close()

    def _remove_sandbox_from_db(self, sandbox_id):
        if not self.db_available:
            return
        session = get_session()
        try:
            db_sandbox = session.query(DBSandbox).filter_by(id=sandbox_id).first()
            if db_sandbox:
                session.delete(db_sandbox)
                session.commit()
        finally:
            session.close()

    def _cleanup_old_sandboxes(self):
        # Remove sandboxes that haven't been used within timeout period
        now = datetime.now()
        to_remove = []
        with self._lock:
            for sandbox_id, sandbox in self.sandboxes.items():
                if now - sandbox["last_used"] > timedelta(
                    seconds=self.config.sandbox_timeout
                ):
                    to_remove.append(sandbox_id)
        for sandbox_id in to_remove:
            self.remove_sandbox(sandbox_id)

    def create_sandbox(self) -> str:
        """Create a new isolated Python sandbox container with enhanced security."""
        self._cleanup_old_sandboxes()
        with self._lock:
            if (
                len(self.sandboxes) + self._pending_creations
                >= self.config.max_sandboxes
            ):
                raise RuntimeError("Maximum number of sandboxes reached")
            self._pending_creations += 1

        sandbox_id = str(uuid.uuid4())
        container = None

        try:
            if (
                getattr(self.config, "require_pinned_image", False)
                and "@sha256:" not in self.config.docker_image
            ):
                raise RuntimeError(
                    "DOCKER_IMAGE must be pinned by digest when "
                    "SANDBOX_REQUIRE_PINNED_IMAGE=true"
                )

            # Create Docker container with enhanced security restrictions
            run_kwargs = dict(
                image=self.config.docker_image,
                command=["sleep", "infinity"],  # Safer than string command
                detach=True,
                name=f"omcp-sandbox-{sandbox_id}",
                mem_limit="512m",  # Memory limit
                cpu_period=100000,  # CPU limits
                cpu_quota=50000,
                remove=True,  # Auto-remove when stopped
                user=1000,  # User isolation; image should provide a non-root UID
                cap_drop=["ALL"],  # Drop all capabilities
                security_opt=["no-new-privileges"],  # Prevent privilege escalation
                pids_limit=50,
                ulimits=[Ulimit(name="nproc", soft=50, hard=100)],
                tmpfs={  # Temporary filesystem mounts
                    "/tmp": "rw,noexec,nosuid,size=100M",
                    "/sandbox": "rw,noexec,nosuid,size=500M",
                },
            )

            # Respect config-driven read-only flag
            if getattr(self.config, "sandbox_read_only", False):
                run_kwargs["read_only"] = True

            # Network controls: default to no network unless explicitly enabled
            explicit_net = getattr(self.config, "sandbox_network", None)
            allow_host_gateway = getattr(self.config, "allow_host_gateway", False)
            if explicit_net:
                if explicit_net == "host" or explicit_net.startswith("container:"):
                    raise RuntimeError(
                        "Host and container-shared network modes are forbidden"
                    )
                if explicit_net == "auto":
                    if self.compose_network:
                        run_kwargs["network_mode"] = self.compose_network
                    else:
                        logger.warning(
                            "SANDBOX_NETWORK=auto set but no compose network detected; using no network"
                        )
                        run_kwargs["network_mode"] = "none"
                else:
                    run_kwargs["network_mode"] = explicit_net
            else:
                # Never infer network access from nearby services. A sandbox is
                # networkless unless the operator explicitly opts in.
                run_kwargs["network_mode"] = "none"

            # Allow containers to reach the host via host-gateway if requested and network is enabled
            if allow_host_gateway and run_kwargs.get("network_mode") != "none":
                run_kwargs.setdefault("extra_hosts", {})[
                    "host.docker.internal"
                ] = "host-gateway"

            # Warn if sandbox has no network but DB host isn't localhost
            db_host = (getattr(self.config, "db_host", "") or "").lower()
            if run_kwargs.get("network_mode") == "none" and db_host not in (
                "localhost",
                "127.0.0.1",
            ):
                logger.warning(
                    "Sandbox network is disabled; DB access to host '%s' will fail. "
                    "Set SANDBOX_NETWORK explicitly to enable DB access.",
                    db_host,
                )

            # Fail closed if the configured image is unavailable. Falling back
            # to a mutable, unreviewed image would silently change the boundary.
            container = self.client.containers.run(**run_kwargs)

            # Track sandbox metadata
            with self._lock:
                self.sandboxes[sandbox_id] = {
                    "container": container,
                    "created_at": datetime.now(),
                    "last_used": datetime.now(),
                    "execution_lock": threading.Lock(),
                }
                self._save_sandbox_to_db(
                    sandbox_id,
                    self.sandboxes[sandbox_id]["created_at"],
                    self.sandboxes[sandbox_id]["last_used"],
                )

            logger.info(f"Created new sandbox {sandbox_id}")
            return sandbox_id

        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            if container is not None:
                self._invalidate_sandbox(sandbox_id, container, "creation failure")
            raise
        finally:
            with self._lock:
                self._pending_creations -= 1

    def remove_sandbox(self, sandbox_id: str):
        """Remove a sandbox container and clean up resources."""
        with self._lock:
            sandbox = self.sandboxes.get(sandbox_id)
            if not sandbox:
                return
            container = sandbox.get("container")

        try:
            # Stop and remove the Docker container
            if container:
                container.stop(timeout=1)
                container.remove()
            with self._lock:
                del self.sandboxes[sandbox_id]
            self._remove_sandbox_from_db(sandbox_id)
            logger.info(f"Removed sandbox {sandbox_id}")
        except Exception as e:
            logger.error(f"Failed to remove sandbox {sandbox_id}: {e}")

    def _merge_env(self, env: Optional[Dict[str, str]]) -> Dict[str, str]:
        merged: Dict[str, str] = {}
        if env:
            merged.update({str(k): str(v) for k, v in env.items()})

        packages_path = "/sandbox/packages"
        current_py_path = merged.get("PYTHONPATH")
        if current_py_path:
            if packages_path not in current_py_path.split(":"):
                merged["PYTHONPATH"] = f"{packages_path}:{current_py_path}"
        else:
            merged["PYTHONPATH"] = packages_path

        return merged

    def _invalidate_sandbox(self, sandbox_id: str, container, reason: str) -> None:
        """Kill and forget a sandbox after a policy-enforcement event."""
        try:
            if container:
                container.kill()
        except docker.errors.DockerException:
            logger.warning("Failed to kill sandbox %s after %s", sandbox_id, reason)
        finally:
            with self._lock:
                self.sandboxes.pop(sandbox_id, None)
            self._remove_sandbox_from_db(sandbox_id)

    def _stream_exec(
        self,
        container,
        cmd: list,
        exec_env: Dict[str, str],
        max_output_bytes: int,
        result_queue: queue.Queue,
    ) -> None:
        """Stream a Docker exec while retaining no more than the output cap."""
        stdout_parts = []
        stderr_parts = []
        retained = 0
        truncated = False

        try:
            exec_id = self.client.api.exec_create(
                container.id, cmd, environment=exec_env
            )["Id"]
            stream = self.client.api.exec_start(exec_id, stream=True, demux=True)
            for item in stream:
                if isinstance(item, tuple):
                    stdout_chunk, stderr_chunk = item
                else:
                    stdout_chunk, stderr_chunk = item, None

                for chunk, target in (
                    (stdout_chunk, stdout_parts),
                    (stderr_chunk, stderr_parts),
                ):
                    if not chunk:
                        continue
                    if not isinstance(chunk, bytes):
                        chunk = str(chunk).encode()
                    remaining = max_output_bytes - retained
                    if remaining <= 0:
                        truncated = True
                        break
                    target.append(chunk[:remaining])
                    retained += min(len(chunk), remaining)
                    if len(chunk) > remaining:
                        truncated = True
                        break
                if truncated:
                    break

            exit_code = None
            if not truncated:
                exit_code = self.client.api.exec_inspect(exec_id).get("ExitCode")
            result_queue.put(
                {
                    "exit_code": exit_code,
                    "stdout": b"".join(stdout_parts),
                    "stderr": b"".join(stderr_parts),
                    "output_truncated": truncated,
                }
            )
        except Exception as error:
            result_queue.put({"exception": error})

    def execute_code(
        self,
        sandbox_id: str,
        code: str,
        timeout: Optional[int] = None,
        validate: bool = False,
        env: Optional[Dict[str, str]] = None,
    ) -> dict:
        """Execute Python code in the specified sandbox container and return a structured dict.

        Args:
            sandbox_id: The ID of the sandbox
            code: The Python code to execute
            timeout: Execution timeout in seconds (clamped to configured policy)
            validate: Whether to validate code for dangerous patterns (default: False)
            env: Optional environment variables for the execution

        Returns:
            Dict with keys: output (str), exit_code (int), error (str|None)
        """
        with self._lock:
            sandbox = self.sandboxes.get(sandbox_id)
            if not sandbox:
                raise ValueError(f"Sandbox {sandbox_id} not found")
            container = sandbox.get("container")
            execution_lock = sandbox["execution_lock"]

        if container is None:
            raise ValueError(f"Sandbox {sandbox_id} has no active container")
        if not execution_lock.acquire(blocking=False):
            return {
                "output": "",
                "exit_code": 75,
                "error": "Sandbox is already executing another request",
                "timed_out": False,
                "output_truncated": False,
                "sandbox_destroyed": False,
            }

        try:
            # Validation is defence in depth; Docker remains the security boundary.
            if validate:
                from omcp_py.security.code_validator import validator

                is_valid, error_msg = validator.validate(code)
                if not is_valid:
                    return {
                        "output": "",
                        "exit_code": 1,
                        "error": f"Security Violation: {error_msg}",
                        "timed_out": False,
                        "output_truncated": False,
                        "sandbox_destroyed": False,
                    }

            with self._lock:
                self.sandboxes[sandbox_id]["last_used"] = datetime.now()
                self._save_sandbox_to_db(
                    sandbox_id,
                    self.sandboxes[sandbox_id]["created_at"],
                    self.sandboxes[sandbox_id]["last_used"],
                )

            exec_env = self._merge_env(env)
            exec_env["SANDBOX_USER_CODE"] = code
            requested_timeout = (
                self.config.execution_default_timeout
                if timeout is None
                else int(timeout)
            )
            effective_timeout = min(
                max(1, requested_timeout), self.config.execution_max_timeout
            )

            wrapper = (
                "import os, sys, traceback\n"
                'code = os.environ.get("SANDBOX_USER_CODE", "")\n'
                "try:\n"
                '    compiled = compile(code, "<sandbox>", "exec")\n'
                '    exec(compiled, {"__name__": "__main__", "__package__": None})\n'
                "except Exception:\n"
                "    traceback.print_exc(file=sys.stderr)\n"
                "    sys.exit(1)\n"
            )

            cmd = ["python3", "-u", "-c", wrapper]
            result_queue: queue.Queue = queue.Queue(maxsize=1)
            worker = threading.Thread(
                target=self._stream_exec,
                args=(
                    container,
                    cmd,
                    exec_env,
                    self.config.execution_max_output_bytes,
                    result_queue,
                ),
                daemon=True,
            )
            worker.start()
            worker.join(effective_timeout)

            if worker.is_alive():
                self._invalidate_sandbox(sandbox_id, container, "execution timeout")
                return {
                    "output": "",
                    "exit_code": 124,
                    "error": (
                        f"Execution exceeded the host-enforced "
                        f"{effective_timeout}-second deadline"
                    ),
                    "timed_out": True,
                    "output_truncated": False,
                    "sandbox_destroyed": True,
                }

            exec_result = result_queue.get_nowait()
            if "exception" in exec_result:
                raise exec_result["exception"]

            output_text = exec_result["stdout"].decode(errors="replace")
            stderr_text = exec_result["stderr"].decode(errors="replace")
            output_truncated = exec_result["output_truncated"]
            if output_truncated:
                self._invalidate_sandbox(sandbox_id, container, "output limit")
                return {
                    "output": output_text,
                    "exit_code": 137,
                    "error": (
                        "Execution exceeded the configured output limit of "
                        f"{self.config.execution_max_output_bytes} bytes"
                    ),
                    "timed_out": False,
                    "output_truncated": True,
                    "sandbox_destroyed": True,
                }

            exit_code = exec_result["exit_code"]
            error_text = None
            if exit_code != 0:
                error_text = stderr_text.strip() or f"Exit code {exit_code}"

            return {
                "output": output_text,
                "exit_code": exit_code,
                "error": error_text,
                "timed_out": False,
                "output_truncated": False,
                "sandbox_destroyed": False,
            }
        except Exception as e:
            logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
            return {
                "output": "",
                "exit_code": 1,
                "error": str(e),
                "timed_out": False,
                "output_truncated": False,
                "sandbox_destroyed": False,
            }
        finally:
            execution_lock.release()

    def list_sandboxes(self) -> list:
        """Return list of all active sandboxes with metadata."""
        self._cleanup_old_sandboxes()
        with self._lock:
            return [
                {
                    "id": sandbox_id,
                    "created_at": sandbox["created_at"].isoformat(),
                    "last_used": sandbox["last_used"].isoformat(),
                }
                for sandbox_id, sandbox in self.sandboxes.items()
            ]
