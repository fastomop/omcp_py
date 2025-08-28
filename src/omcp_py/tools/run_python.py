from mcp import Tool, ToolInput, ToolOutput
from omcp_py.utils.omcp_py import execute_python_code
import logging

logger = logging.getLogger(__name__)

class RunPythonTool(Tool):
    """
    Tool for running Python code in a sandboxed environment.
    Expects 'python_code' as input (keeps backward compatibility with 'code').
    """
    def __init__(self):
        super().__init__(
            name="run_python_code",
            description="Run Python code in a sandbox environment",
            input_schema={
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "Python code to execute"
                    },
                    "code": {
                        "type": "string",
                        "description": "(legacy) Python code to execute"
                    }
                },
                "required": ["python_code"],
                "additionalProperties": False
            }
        )

    async def execute(self, params: ToolInput) -> ToolOutput:
        # Accept either new 'python_code' key or legacy 'code'
        code = params.get("python_code") if params.get("python_code") is not None else params.get("code")
        logger.info("RunPythonTool: executing code in sandbox")
        # If this tool is used locally (no sandbox_id), execute directly
        sandbox_id = params.get("sandbox_id")
        timeout = params.get("timeout")

        if sandbox_id:
            # Delegates to sandbox manager path via mcp server tools (expected to be proxied)
            # Here we just return a placeholder; the server's execute_python_code handles sandbox execution
            return ToolOutput({"status": "delegated"})

        result = execute_python_code(code)
        return ToolOutput({
            "result": result.get("return_value"),
            "output": result.get("output"),
            "error": result.get("error")
        })
