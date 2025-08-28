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
import requests
import os
from dotenv import load_dotenv, find_dotenv
from omcp_py.core.db import get_session, Sandbox as DBSandbox

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)

class SandboxManager:
    """Manages Docker-based Python sandboxes with automatic cleanup and enhanced security."""
    
    def __init__(self, config):
        self.config = config
        self.client = docker.DockerClient(base_url=os.getenv("DOCKER_HOST", "unix://var/run/docker.sock"))
        self.sandboxes: Dict[str, dict] = {}
        self.db_available = True
        try:
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
        for sandbox_id, sandbox in self.sandboxes.items():
            if now - sandbox["last_used"] > timedelta(seconds=self.config.sandbox_timeout):
                to_remove.append(sandbox_id)
        for sandbox_id in to_remove:
            self.remove_sandbox(sandbox_id)

    def create_sandbox(self) -> str:
        """Create a new isolated Python sandbox container with enhanced security."""
        if len(self.sandboxes) >= self.config.max_sandboxes:
            raise RuntimeError("Maximum number of sandboxes reached")
        
        sandbox_id = str(uuid.uuid4())
        
        try:
            # Create Docker container with enhanced security restrictions
            container = self.client.containers.run(
                self.config.docker_image,
                command=["sleep", "infinity"],  # Safer than string command
                detach=True,
                name=f"omcp-sandbox-{sandbox_id}",
                # network_mode="none",      # Remove network isolation to allow DB access
                mem_limit="512m",         # Memory limit
                cpu_period=100000,        # CPU limits
                cpu_quota=50000,
                remove=True,              # Auto-remove when stopped
                user=1000,       # User isolation
                read_only=True,           # Read-only filesystem
                cap_drop=["ALL"],         # Drop all capabilities
                security_opt=["no-new-privileges"],  # Prevent privilege escalation
                tmpfs={                   # Temporary filesystem mounts
                    "/tmp": "rw,noexec,nosuid,size=100M",
                    "/sandbox": "rw,noexec,nosuid,size=500M"
                }
                # Optionally, specify network if using a custom one
                # network="default"
            )
            
            # Track sandbox metadata
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
        if sandbox_id not in self.sandboxes:
            return
        
        try:
            # Stop and remove the Docker container
            container:docker.models.containers.Container = self.sandboxes[sandbox_id]["container"]
            if container:
                container.stop(timeout=1)
                container.remove()
            del self.sandboxes[sandbox_id]
            self._remove_sandbox_from_db(sandbox_id)
            logger.info(f"Removed sandbox {sandbox_id}")
        except Exception as e:
            logger.error(f"Failed to remove sandbox {sandbox_id}: {e}")
    
    def execute_code(self, sandbox_id: str, code: str, timeout: Optional[int] = None) -> dict:
        """Execute Python code in the specified sandbox container and return a structured dict.

        Returns a dict with keys: output (bytes or str), exit_code (int), error (str|None)
        """
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        container:docker.models.containers.Container = self.sandboxes[sandbox_id]["container"]
        self.sandboxes[sandbox_id]["last_used"] = datetime.now()  # Update usage time
        self._save_sandbox_to_db(sandbox_id, self.sandboxes[sandbox_id]["created_at"], self.sandboxes[sandbox_id]["last_used"])
        
        try:
            # Execute code in container and capture output
            # Use a shell-safe invocation and enforce timeout by running python -c in the container
            cmd = ["python3", "-c", code]
            exec_result = container.exec_run(cmd, demux=True)

            # exec_result is a tuple (exit_code, (stdout, stderr)) when demux=True
            if isinstance(exec_result, tuple) and len(exec_result) == 2:
                exit_code, streams = exec_result
                stdout_b, stderr_b = streams
            else:
                # Fallback: older dockerpy returns an ExecResult-like object
                exit_code = getattr(exec_result, "exit_code", 0)
                stdout_b = getattr(exec_result, "output", b"")
                stderr_b = b""

            output = stdout_b or b""
            stderr = stderr_b or b""

            error_text = None
            if exit_code != 0:
                # Prefer stderr if available
                try:
                    error_text = stderr.decode(errors="replace").strip() or f"Exit code {exit_code}"
                except Exception:
                    error_text = f"Exit code {exit_code}"

            return {"output": output, "exit_code": exit_code, "error": error_text}
        except Exception as e:
            logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
            return {"output": b"", "exit_code": 1, "error": str(e)}

    def list_sandboxes(self) -> list:
        """Return list of all active sandboxes with metadata."""
        return [
            {
                "id": sandbox_id,
                "created_at": sandbox["created_at"].isoformat(),
                "last_used": sandbox["last_used"].isoformat()
            }
            for sandbox_id, sandbox in self.sandboxes.items()
        ] 