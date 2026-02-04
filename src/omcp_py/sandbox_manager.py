"""
Sandbox Manager - Core Docker container management for Python sandboxes.

Handles creation, execution, and cleanup of isolated Python environments
using Docker containers with security restrictions and resource limits.
"""

import uuid
import docker
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import docker.models
import docker.models.containers
import os
import threading
from dotenv import load_dotenv, find_dotenv
from omcp_py.core.db import get_session, Sandbox as DBSandbox, create_tables

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

class SandboxManager:
    """Manages Docker-based Python sandboxes with automatic cleanup and enhanced security."""
    
    def __init__(self, config):
        self.config = config
        self.client = docker.DockerClient(base_url=os.getenv("DOCKER_HOST", "unix://var/run/docker.sock"))
        self._lock = threading.RLock()
        # Try to detect a docker-compose project network to attach sandboxes to.
        # This allows the sandbox to resolve compose service names like 'db'.
        self.compose_network = None
        try:
            # Try to find a docker network that contains a DB/container for this project.
            nets = list(self.client.networks.list())
            for n in nets:
                try:
                    attrs = n.attrs
                    containers = attrs.get('Containers') or {}
                    for cid in containers.keys():
                        try:
                            c = self.client.containers.get(cid)
                            # Check for common DB indicators: service label or container name or image
                            labels = c.labels or {}
                            name = (c.name or '').lower()
                            img = (getattr(c, 'image', None) and getattr(c.image, 'tags', [])) or []
                            if labels.get('com.docker.compose.service') == 'db' or 'db' == name or any('postgres' in t for t in img):
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
                    "last_used": db_sandbox.last_used
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
                db_sandbox = DBSandbox(id=sandbox_id, created_at=created_at, last_used=last_used)
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
                if now - sandbox["last_used"] > timedelta(seconds=self.config.sandbox_timeout):
                    to_remove.append(sandbox_id)
        for sandbox_id in to_remove:
            self.remove_sandbox(sandbox_id)

    def create_sandbox(self) -> str:
        """Create a new isolated Python sandbox container with enhanced security."""
        self._cleanup_old_sandboxes()
        with self._lock:
            if len(self.sandboxes) >= self.config.max_sandboxes:
                raise RuntimeError("Maximum number of sandboxes reached")
        
        sandbox_id = str(uuid.uuid4())
        
        try:
            # Create Docker container with enhanced security restrictions
            run_kwargs = dict(
                image=self.config.docker_image,
                command=["sleep", "infinity"],  # Safer than string command
                detach=True,
                name=f"omcp-sandbox-{sandbox_id}",
                mem_limit="512m",         # Memory limit
                cpu_period=100000,        # CPU limits
                cpu_quota=50000,
                remove=True,              # Auto-remove when stopped
                user=1000,       # User isolation
                cap_drop=["ALL"],         # Drop all capabilities
                security_opt=["no-new-privileges"],  # Prevent privilege escalation
                tmpfs={                   # Temporary filesystem mounts
                    "/tmp": "rw,noexec,nosuid,size=100M",
                    "/sandbox": "rw,noexec,nosuid,size=500M"
                }
            )

            # Respect config-driven read-only flag
            if getattr(self.config, "sandbox_read_only", False):
                run_kwargs["read_only"] = True

            # Network controls: default to no network unless explicitly enabled
            explicit_net = getattr(self.config, "sandbox_network", None)
            allow_host_gateway = getattr(self.config, "allow_host_gateway", False)
            if explicit_net:
                if explicit_net == "auto":
                    if self.compose_network:
                        run_kwargs["network_mode"] = self.compose_network
                    else:
                        logger.warning("SANDBOX_NETWORK=auto set but no compose network detected; using no network")
                        run_kwargs["network_mode"] = "none"
                else:
                    run_kwargs["network_mode"] = explicit_net
            else:
                # If a compose network is detected and DB_HOST is not localhost,
                # attach to the compose network to allow DB access by service name.
                db_host = (getattr(self.config, "db_host", "") or "").lower()
                if self.compose_network and db_host not in ("localhost", "127.0.0.1"):
                    run_kwargs["network_mode"] = self.compose_network
                    logger.info(
                        "No SANDBOX_NETWORK set; attaching sandbox to compose network '%s' for DB access",
                        self.compose_network,
                    )
                else:
                    run_kwargs["network_mode"] = "bridge" if allow_host_gateway else "none"

            # Allow containers to reach the host via host-gateway if requested and network is enabled
            if allow_host_gateway and run_kwargs.get("network_mode") != "none":
                run_kwargs.setdefault("extra_hosts", {})["host.docker.internal"] = "host-gateway"

            # Warn if sandbox has no network but DB host isn't localhost
            db_host = (getattr(self.config, "db_host", "") or "").lower()
            if run_kwargs.get("network_mode") == "none" and db_host not in ("localhost", "127.0.0.1"):
                logger.warning(
                    "Sandbox network is disabled; DB access to host '%s' will fail. "
                    "Set SANDBOX_NETWORK=auto or a Docker network name to enable DB access.",
                    db_host,
                )

            try:
                container = self.client.containers.run(**run_kwargs)
            except docker.errors.ImageNotFound:
                # Fallback: try official python slim if custom image not available
                run_kwargs['image'] = 'python:3.11-slim'
                container = self.client.containers.run(**run_kwargs)

            # Track sandbox metadata
            with self._lock:
                self.sandboxes[sandbox_id] = {
                    "container": container,
                    "created_at": datetime.now(),
                    "last_used": datetime.now()
                }
                self._save_sandbox_to_db(sandbox_id, self.sandboxes[sandbox_id]["created_at"], self.sandboxes[sandbox_id]["last_used"])
            
            logger.info(f"Created new sandbox {sandbox_id}")
            return sandbox_id
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise
    
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
            timeout: Execution timeout in seconds (default: None)
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
        
        # Validation
        if validate:
            from omcp_py.security.code_validator import validator
            is_valid, error_msg = validator.validate(code)
            if not is_valid:
                return {
                    "output": "",
                    "exit_code": 1,
                    "error": f"Security Violation: {error_msg}"
                }
        
        with self._lock:
            self.sandboxes[sandbox_id]["last_used"] = datetime.now()
            self._save_sandbox_to_db(sandbox_id, self.sandboxes[sandbox_id]["created_at"], self.sandboxes[sandbox_id]["last_used"])
        
        try:
            # Construct command with timeout enforcement
            cmd = ["python3", "-c", code]
            
            if timeout:
                # Use 'timeout' command to kill process if it runs too long
                # timeout -k <kill_timeout> <duration> <command>
                # We add a small kill buffer
                cmd = ["timeout", "-k", "5", str(timeout)] + cmd

            # Execute code
            exec_result = container.exec_run(cmd, demux=True, environment=self._merge_env(env))

            # Parse result (docker-py returned tuple or object depending on version/mock)
            if isinstance(exec_result, tuple) and len(exec_result) == 2:
                exit_code, streams = exec_result
                stdout_b, stderr_b = streams
            else:
                exit_code = getattr(exec_result, "exit_code", 0)
                output_obj = getattr(exec_result, "output", b"")
                if isinstance(output_obj, tuple) and len(output_obj) == 2:
                    stdout_b, stderr_b = output_obj
                else:
                    stdout_b = output_obj
                    stderr_b = b""

            output = stdout_b or b""
            stderr = stderr_b or b""

            # Normalize output
            try:
                output_text = output.decode(errors="replace") if isinstance(output, (bytes, bytearray)) else str(output)
            except Exception:
                output_text = str(output)
            try:
                stderr_text = stderr.decode(errors="replace") if isinstance(stderr, (bytes, bytearray)) else str(stderr)
            except Exception:
                stderr_text = str(stderr)

            error_text = None
            if exit_code != 0:
                if exit_code == 124: # timeout command exit code
                    error_text = f"Execution timed out after {timeout} seconds"
                else:
                    error_text = stderr_text.strip() or f"Exit code {exit_code}"

            return {"output": output_text, "exit_code": exit_code, "error": error_text}
        except Exception as e:
            logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
            return {"output": "", "exit_code": 1, "error": str(e)}

    def list_sandboxes(self) -> list:
        """Return list of all active sandboxes with metadata."""
        self._cleanup_old_sandboxes()
        with self._lock:
            return [
                {
                    "id": sandbox_id,
                    "created_at": sandbox["created_at"].isoformat(),
                    "last_used": sandbox["last_used"].isoformat()
                }
                for sandbox_id, sandbox in self.sandboxes.items()
            ]
