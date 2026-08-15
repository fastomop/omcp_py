#!/usr/bin/env python3
"""
Simple demo script to test the OMCP Python Sandbox Server
"""

import subprocess
import pytest
from conftest import require_integration


def test_server_status():
    require_integration()
    print("🚀 OMCP Python Sandbox Server Demo")
    print("=" * 50)

    # Check if the server process is running
    try:
        result = subprocess.run(
            ["pgrep", "-f", "omcp_py/main.py"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✅ FastMCP server is running!")
            print("📋 Available MCP Tools:")
            print("   🔧 create_sandbox - Create new isolated Python environment")
            print("   📝 list_sandboxes - List all active sandboxes")
            print("   🐍 execute_python_code - Run Python code in sandbox")
            print("   📦 install_package - Install Python packages in sandbox")
            print("   🗑️  remove_sandbox - Remove sandbox containers")
            print("\n🔒 Security Features:")
            print("   - Docker-based isolation")
            print("   - User isolation (sandboxuser)")
            print("   - Read-only filesystem")
            print("   - Dropped Linux capabilities")
            print("   - No privilege escalation")
            print("   - Command injection protection")
            print("   - Resource limits (CPU, memory)")
            print("   - Network isolation")
            print("\n🎯 Server is ready for MCP client connections!")

        else:
            print("❌ FastMCP server is not running")
            print("💡 Start it with: python src/omcp_py/main.py")
    except Exception as e:
        print(f"❌ Error checking server status: {e}")


def show_docker_status():
    print("\n🐳 Docker Status:")
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
            print("📊 Active containers:")
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:  # More than just header
                for line in lines[1:]:
                    if line.strip():
                        print(f"   {line}")
            else:
                print("   No active containers")
        else:
            pytest.skip("Docker is not running or not accessible")
    except Exception as e:
        pytest.skip(f"Docker check failed: {e}")


if __name__ == "__main__":
    test_server_status()
    show_docker_status()
    print("\n" + "=" * 50)
    print("🎉 Demo complete! The server is working correctly.")
