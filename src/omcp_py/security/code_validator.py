import ast
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class CodeValidator:
    """
    Validates Python code before execution in sandbox.

    Checks for:
    - Dangerous imports
    - Dangerous built-ins and attribute access
    - Syntax errors
    """

    BLOCKED_IMPORTS = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "requests",
        "urllib",
        "http",
        "ftplib",
        "poplib",
        "imaplib",
        "smtplib",
        "telnetlib",
        "ctypes",
        "pickle",
        "marshal",
        "shelve",
        "dbm",
        "sqlite3",
        "importlib",
        "builtins",
        "multiprocessing",
        "threading",
        "inspect",
        "runpy",
        "pkgutil",
        "pkg_resources",
    }

    BLOCKED_BUILTINS = {
        "exec",
        "eval",
        "compile",
        "open",
        "__import__",
        "input",
        "help",
        "dir",
        "vars",
        "globals",
        "locals",
        "exit",
        "quit",
    }

    BLOCKED_ATTRIBUTES = {
        "import_module",
        "run",
        "Popen",
        "system",
        "popen",
        "spawn",
        "connect",
        "bind",
        "listen",
        "accept",
        "fork",
        "execvp",
        "execv",
        "execve",
        "open",
        "load",
        "loads",
        "load_module",
        "find_loader",
        "find_spec",
    }

    MODULE_ATTR_BLOCKLIST = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "ctypes",
        "pickle",
        "importlib",
        "builtins",
        "multiprocessing",
        "threading",
        "inspect",
    }

    def validate(self, code: str) -> Tuple[bool, str]:
        """
        Validate code AST.
        Returns: (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [n.name.split(".")[0] for n in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module.split(".")[0]] if node.module else []
            else:
                names = []

            for name in names:
                if name in self.BLOCKED_IMPORTS:
                    return (
                        False,
                        f"Import of '{name}' is restricted for security reasons.",
                    )

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.BLOCKED_BUILTINS:
                        return False, f"Use of '{node.func.id}' is restricted."
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.BLOCKED_ATTRIBUTES:
                        return False, f"Use of '{node.func.attr}' is restricted."
                    if (
                        isinstance(node.func.value, ast.Name)
                        and node.func.value.id in self.MODULE_ATTR_BLOCKLIST
                    ):
                        return (
                            False,
                            f"Attribute access on '{node.func.value.id}' is restricted.",
                        )

            if isinstance(node, ast.Attribute):
                if (
                    isinstance(node.value, ast.Name)
                    and node.value.id in self.MODULE_ATTR_BLOCKLIST
                ):
                    if node.attr in self.BLOCKED_ATTRIBUTES:
                        return (
                            False,
                            f"Attribute access '{node.value.id}.{node.attr}' is restricted.",
                        )

        return True, ""


# Singleton instance
validator = CodeValidator()
