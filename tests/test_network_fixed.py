import sys
import uuid
sys.path.insert(0, "src")

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager
import docker

config = get_config()
manager = SandboxManager(config)

# Create sandbox with network access
sandbox_id = str(uuid.uuid4())
client = docker.DockerClient(base_url="unix:///var/run/docker.sock")

try:
    # Create container with network access
    container = client.containers.run(
        "python:3.11-slim",
        command=["sleep", "infinity"],
        detach=True,
        name=f"omcp-sandbox-{sandbox_id}",
        network="omcp_py_default",  # Connect to the same network as the database
        mem_limit="512m",
        cpu_period=100000,
        cpu_quota=50000,
        remove=True,
        user=1000,
        read_only=True,
        cap_drop=["ALL"],
        security_opt=["no-new-privileges"],
        tmpfs={
            "/tmp": "rw,noexec,nosuid,size=100M",
            "/sandbox": "rw,noexec,nosuid,size=500M"
        }
    )
    
    print(f"Sandbox created: {sandbox_id}")
    
    # Test network connectivity
    db_code = """
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(("db", 5432))
    if result == 0:
        print("Network connectivity to database: SUCCESS")
    else:
        print(f"Network connectivity failed: {result}")
    sock.close()
except Exception as e:
    print(f"Network test failed: {e}")
"""
    
    result = container.exec_run(["python3", "-c", db_code])
    print("Network test result:", result.output.decode())
    
    # Clean up
    container.stop(timeout=1)
    container.remove()
    print("Test completed")
    
except Exception as e:
    print(f"Error: {e}")
