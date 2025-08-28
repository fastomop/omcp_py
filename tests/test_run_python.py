from omcp_py.utils.omcp_py import execute_python_code


def test_basic_execution():
    code = "a = 2\nb = 3\na + b"
    result = execute_python_code(code)
    assert result["return_value"] == 5
    assert result["error"] is None


def test_error_handling():
    code = "a = 2\nb = 'x'\na + b"
    result = execute_python_code(code)
    assert result["return_value"] is None
    assert result["error"] is not None
