
import ast
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class CodeValidator:
    """
    Validates Python code before execution in sandbox.
    
    Checks for:
    - Dangerous imports (subprocess, os, etc.)
    - Dangerous built-ins (exec, eval, etc.)
    - Syntax errors
    """
    
    # Modules that are generally blocked in a sandbox environment
    BLOCKED_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'requests', 'urllib',
        'http', 'ftplib', 'poplib', 'imaplib', 'smtplib', 'telnetlib',
        'ctypes', 'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3'
    }
    
    # Safe subset of os/sys functionality that might be needed
    # (Not used in static analysis, but conceptually)
    
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
            # Check for imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    names = [n.name.split('.')[0] for n in node.names]
                else:
                    if node.module:
                        names = [node.module.split('.')[0]]
                    else:
                        names = []
                
                for name in names:
                    if name in self.BLOCKED_IMPORTS:
                        # Allow imports if strictly required?
                        # For now, we are strict.
                        # Exception: some libraries might use these internally, but user code shouldn't import them directly
                        # if we want strict sandboxing.
                        # However, for OMOP scripts we WROTE, they import os/sys/subprocess.
                        # WE need to distinguish between USER code and SYSTEM scripts.
                        # CodeValidator should probably default to strict, but allow override.
                        return False, f"Import of '{name}' is restricted for security reasons."

            # Check for dangerous built-ins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ('exec', 'eval', 'compile', 'open'):
                        return False, f"Use of '{node.func.id}' is restricted."
                        
        return True, ""

# Singleton instance
validator = CodeValidator()
