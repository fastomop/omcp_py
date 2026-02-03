import os
import sys
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_synthea_file_structure():
    required_files = [
        "src/omcp_py/main.py",
        "docker-compose.yml",
        "requirements.txt",
        "scripts/synthea_workflow.py"
    ]

    required_dirs = [
        "synthetic_data"
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing required file: {file_path}"

    for dir_path in required_dirs:
        assert os.path.exists(dir_path), f"Missing required directory: {dir_path}"


def test_docker_compose_config():
    try:
        import yaml
    except Exception:
        pytest.skip("PyYAML not installed; skipping docker-compose validation")

    with open("docker-compose.yml", "r") as f:
        config = yaml.safe_load(f)

    assert "services" in config and "db" in config["services"]
    env = config["services"]["db"].get("environment", {})
    assert env.get("POSTGRES_DB") is not None
    assert env.get("POSTGRES_USER") is not None
