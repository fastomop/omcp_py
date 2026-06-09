
import ast
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class CodeValidator:
    """
    Validates Python code before execution in sandbox.
    
    Uses AST analysis to block both static imports and dynamic execution bypasses.
    
    Checks for:
    - Dangerous imports (subprocess, os, sys, etc.)
    - Dangerous built-ins (exec, eval, compile, __import__, etc.)
    - Dynamic execution bypasses (__builtins__, __globals__, getattr/setattr/delattr tricks)
    - Dangerous attribute access (class manipulation, function object access)
    - Syntax errors
    """
    
    # Modules that are generally blocked in a sandbox environment
    BLOCKED_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'requests', 'urllib',
        'http', 'ftplib', 'poplib', 'imaplib', 'smtplib', 'telnetlib',
        'ctypes', 'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3',
        'importlib', 'builtins', '__main__', 'gc', 'signal', 'threading',
        'multiprocessing', 'asyncio', 'concurrent', 'ssl', 'hashlib', 'hmac',
    }
    
    # Dangerous built-in functions that enable code execution or system access
    BLOCKED_BUILTINS = {
        'exec', 'eval', 'compile', 'open', '__import__',
        'input', 'breakpoint', 'help', 'dir', 'vars', 'globals', 'locals',
        'getattr', 'setattr', 'delattr', 'hasattr',
    }
    
    # Dangerous attributes that enable class/function manipulation and escaping
    BLOCKED_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__globals__', '__code__', '__closure__', '__func__',
        '__self__', '__enter__', '__exit__', '__call__',
        '__getattribute__', '__setattr__', '__dict__',
        '__init_subclass__', '__new__', '__del__',
    }
    
    def validate(self, code: str) -> Tuple[bool, str]:
        """
        Validate code AST for security violations.
        Returns: (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
            
        for node in ast.walk(tree):
            # Check for direct imports
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
                        return False, f"Import of '{name}' is restricted for security reasons."

            # Check for function calls (exec, eval, __import__, getattr, etc.)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Direct function calls like exec(...), eval(...), etc.
                    if node.func.id in self.BLOCKED_BUILTINS:
                        return False, f"Use of '{node.func.id}()' is restricted."
                
                # Check attribute calls: obj.eval(), obj.__import__(), etc.
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.BLOCKED_BUILTINS or node.func.attr in self.BLOCKED_ATTRIBUTES:
                        return False, f"Use of '.{node.func.attr}()' is restricted."
            
            # Check for dangerous attribute access: __builtins__, __globals__, __class__, etc.
            if isinstance(node, ast.Attribute):
                if node.attr in self.BLOCKED_ATTRIBUTES:
                    return False, f"Attribute access '.{node.attr}' is restricted."
            
            # Check for direct reference to __builtins__
            if isinstance(node, ast.Name):
                if node.id == '__builtins__':
                    return False, "Direct reference to '__builtins__' is restricted."
            
            # Check for subscript access: obj['__globals__'], data['__builtins__'], etc.
            if isinstance(node, ast.Subscript):
                # Check string literal subscripts like obj['__globals__']
                if isinstance(node.slice, ast.Constant):
                    if isinstance(node.slice.value, str):
                        if node.slice.value in self.BLOCKED_ATTRIBUTES or node.slice.value == '__builtins__':
                            return False, f"Subscript access to '{node.slice.value}' is restricted."
                        
        return True, ""

# Singleton instance
validator = CodeValidator()
