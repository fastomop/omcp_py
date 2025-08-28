import sys
import io
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Executes Python code in a restricted namespace and captures output, errors, and return value.
    Returns a dict with keys: 'output', 'error', 'return_value'.
    """
    if code is None:
        return {"output": "", "error": "No code provided", "return_value": None}

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    namespace = {}
    error_msg = None
    return_value = None
    try:
        lines = code.strip().split('\n')
        if not lines:
            return_value = None
        else:
            # Execute all but the last line
            if len(lines) > 1:
                exec('\n'.join(lines[:-1]), namespace)
            last_line = lines[-1]
            try:
                # Try to eval the last line for return value
                return_value = eval(last_line, namespace)
            except Exception:
                # If eval fails, execute it as a statement
                exec(last_line, namespace)
                return_value = namespace.get('_', None)
    except Exception as e:
        error_msg = f"{e.__class__.__name__}: {e}"
        logger.exception("Error executing code")
        return_value = None
    output = sys.stdout.getvalue()
    stderr_output = sys.stderr.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    # Combine error sources
    error_combined = '; '.join(filter(None, [error_msg, stderr_output.strip()]))
    return {"output": output, "error": error_combined if error_combined else None, "return_value": return_value}
