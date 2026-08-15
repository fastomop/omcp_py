import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    pass


def test_validator():
    from omcp_py.security.code_validator import validator

    safe_code = "print('Hello')"
    unsafe_code = "import os; os.system('ls')"

    valid, _ = validator.validate(safe_code)
    assert valid

    valid, error = validator.validate(unsafe_code)
    assert not valid, f"Unsafe code passed validation: {error}"


def test_scripts_exist():
    scripts_dir = Path(__file__).parent.parent / "src" / "omcp_py" / "scripts" / "omop"
    scripts = ["create_schema.py", "load_synthea.py", "analyze.py"]

    for script in scripts:
        assert (scripts_dir / script).exists(), f"Missing script: {script}"
