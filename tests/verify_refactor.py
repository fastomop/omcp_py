
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    print("Testing imports...")
    try:
        import omcp_py.core.globals
        import omcp_py.tools.sandbox_tools
        import omcp_py.tools.omop_tools
        import omcp_py.tools.query_tools
        import omcp_py.security.code_validator
        print("✅ All modules imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

def test_validator():
    print("\nTesting CodeValidator...")
    from omcp_py.security.code_validator import validator
    
    safe_code = "print('Hello')"
    unsafe_code = "import os; os.system('ls')"
    
    valid, _ = validator.validate(safe_code)
    if valid:
        print("✅ Safe code validated correctly")
    else:
        print("❌ Safe code failed validation")
        
    valid, error = validator.validate(unsafe_code)
    if not valid:
        print(f"✅ Unsafe code caught correctly: {error}")
    else:
        print("❌ Unsafe code passed validation (Should fail)")

def test_scripts_exist():
    print("\nChecking scripts...")
    scripts_dir = Path(__file__).parent.parent / "src" / "omcp_py" / "scripts" / "omop"
    scripts = ["create_schema.py", "load_synthea.py", "analyze.py"]
    
    all_exist = True
    for script in scripts:
        if (scripts_dir / script).exists():
            print(f"✅ Script found: {script}")
        else:
            print(f"❌ Script missing: {script}")
            all_exist = False
            
    if not all_exist:
        sys.exit(1)

def main():
    print("🚀 Verifying Refactor...")
    test_imports()
    test_validator()
    test_scripts_exist()
    print("\n✨ Verification Complete!")

if __name__ == "__main__":
    main()
