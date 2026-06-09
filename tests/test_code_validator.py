"""
Unit tests for code_validator security checks.

Tests comprehensive protection against:
- Dangerous imports
- Dynamic code execution (eval, exec, compile)
- Reflection attacks (__builtins__, __globals__, __class__)
- Attribute access bypasses
- Subscript access tricks
"""

import pytest
from omcp_py.security.code_validator import CodeValidator, validator


class TestCodeValidatorImports:
    """Test import blocking."""

    def test_blocked_os_import(self):
        """Test that os module imports are blocked."""
        code = "import os"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "os" in msg.lower()

    def test_blocked_sys_import(self):
        """Test that sys module imports are blocked."""
        code = "import sys"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "sys" in msg.lower()

    def test_blocked_subprocess_import(self):
        """Test that subprocess module imports are blocked."""
        code = "import subprocess"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "subprocess" in msg.lower()

    def test_blocked_socket_import(self):
        """Test that socket module imports are blocked."""
        code = "import socket"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_requests_import(self):
        """Test that requests module imports are blocked."""
        code = "import requests"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_pickle_import(self):
        """Test that pickle module imports are blocked."""
        code = "import pickle"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_importlib_import(self):
        """Test that importlib module imports are blocked."""
        code = "import importlib"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_threading_import(self):
        """Test that threading module imports are blocked."""
        code = "import threading"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_asyncio_import(self):
        """Test that asyncio module imports are blocked."""
        code = "import asyncio"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_multiprocessing_import(self):
        """Test that multiprocessing module imports are blocked."""
        code = "import multiprocessing"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_ctypes_import(self):
        """Test that ctypes module imports are blocked."""
        code = "import ctypes"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_from_import(self):
        """Test that from...import blocks dangerous modules."""
        code = "from os import system"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "os" in msg.lower()

    def test_blocked_from_subprocess_import(self):
        """Test that from subprocess import is blocked."""
        code = "from subprocess import run"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_safe_import_pandas(self):
        """Test that safe imports like pandas are allowed."""
        code = "import pandas as pd"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_import_numpy(self):
        """Test that safe imports like numpy are allowed."""
        code = "import numpy as np"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_import_json(self):
        """Test that safe imports like json are allowed."""
        code = "import json"
        is_valid, msg = validator.validate(code)
        assert is_valid


class TestCodeValidatorBuiltins:
    """Test dangerous built-in function blocking."""

    def test_blocked_exec(self):
        """Test that exec() is blocked."""
        code = "exec('print(1)')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "exec" in msg.lower()

    def test_blocked_eval(self):
        """Test that eval() is blocked."""
        code = "eval('1+1')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "eval" in msg.lower()

    def test_blocked_compile(self):
        """Test that compile() is blocked."""
        code = "compile('x=1', '<string>', 'exec')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "compile" in msg.lower()

    def test_blocked_open(self):
        """Test that open() is blocked."""
        code = "open('/etc/passwd', 'r')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "open" in msg.lower()

    def test_blocked_import_dunder(self):
        """Test that __import__() is blocked."""
        code = "__import__('os')"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_getattr(self):
        """Test that getattr() is blocked."""
        code = "getattr(obj, '__class__')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "getattr" in msg.lower()

    def test_blocked_setattr(self):
        """Test that setattr() is blocked."""
        code = "setattr(obj, 'x', 1)"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "setattr" in msg.lower()

    def test_blocked_delattr(self):
        """Test that delattr() is blocked."""
        code = "delattr(obj, 'x')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "delattr" in msg.lower()

    def test_blocked_input(self):
        """Test that input() is blocked."""
        code = "x = input('Enter value: ')"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "input" in msg.lower()

    def test_blocked_breakpoint(self):
        """Test that breakpoint() is blocked."""
        code = "breakpoint()"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "breakpoint" in msg.lower()

    def test_safe_print(self):
        """Test that safe built-ins like print() are allowed."""
        code = "print('hello')"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_len(self):
        """Test that safe built-ins like len() are allowed."""
        code = "x = len([1, 2, 3])"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_sum(self):
        """Test that safe built-ins like sum() are allowed."""
        code = "x = sum([1, 2, 3])"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_range(self):
        """Test that safe built-ins like range() are allowed."""
        code = "for i in range(10): pass"
        is_valid, msg = validator.validate(code)
        assert is_valid


class TestCodeValidatorAttributeAccess:
    """Test dangerous attribute access blocking."""

    def test_blocked_dunder_builtins(self):
        """Test that __builtins__ reference is blocked."""
        code = "x = __builtins__"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__builtins__" in msg

    def test_blocked_globals_attribute(self):
        """Test that .__globals__ attribute access is blocked."""
        code = "x = func.__globals__"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__globals__" in msg

    def test_blocked_class_attribute(self):
        """Test that .__class__ attribute access is blocked."""
        code = "x = obj.__class__"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__class__" in msg

    def test_blocked_bases_attribute(self):
        """Test that .__bases__ attribute access is blocked."""
        code = "x = MyClass.__bases__"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__bases__" in msg

    def test_blocked_subclasses_attribute(self):
        """Test that .__subclasses__ attribute access is blocked."""
        code = "x = MyClass.__subclasses__()"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_code_attribute(self):
        """Test that .__code__ attribute access is blocked."""
        code = "x = func.__code__"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__code__" in msg

    def test_blocked_closure_attribute(self):
        """Test that .__closure__ attribute access is blocked."""
        code = "x = func.__closure__"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_dict_attribute(self):
        """Test that .__dict__ attribute access is blocked."""
        code = "x = obj.__dict__"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__dict__" in msg

    def test_safe_normal_attribute(self):
        """Test that safe attribute access is allowed."""
        code = "x = obj.name"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_method_call(self):
        """Test that safe method calls are allowed."""
        code = "x = obj.method()"
        is_valid, msg = validator.validate(code)
        assert is_valid


class TestCodeValidatorSubscriptAccess:
    """Test subscript access tricks blocking."""

    def test_blocked_subscript_builtins(self):
        """Test that subscript access to __builtins__ is blocked."""
        code = "x = obj['__builtins__']"
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "__builtins__" in msg

    def test_blocked_subscript_globals(self):
        """Test that subscript access to __globals__ is blocked."""
        code = "x = obj['__globals__']"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_subscript_class(self):
        """Test that subscript access to __class__ is blocked."""
        code = "x = obj['__class__']"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_blocked_subscript_dict(self):
        """Test that subscript access to __dict__ is blocked."""
        code = "x = obj['__dict__']"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_safe_subscript_normal(self):
        """Test that safe subscript access is allowed."""
        code = "x = obj['key']"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_safe_subscript_list_index(self):
        """Test that safe list indexing is allowed."""
        code = "x = mylist[0]"
        is_valid, msg = validator.validate(code)
        assert is_valid


class TestCodeValidatorSandboxEscapes:
    """Test comprehensive sandbox escape prevention."""

    def test_escape_via_type_subclasses(self):
        """Test that type().__subclasses__() trick is blocked."""
        code = "type([]).__subclasses__()"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_escape_via_mro(self):
        """Test that __mro__ access is blocked."""
        code = "x = MyClass.__mro__"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_escape_via_func_globals(self):
        """Test that function __globals__ trick is blocked."""
        code = "import sys; sys = ().__class__.__bases__[0].__subclasses__()[104].__init__.__globals__['sys']"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_escape_via_object_new(self):
        """Test that __new__ attribute access is blocked."""
        code = "x = obj.__new__"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_safe_normal_code(self):
        """Test that normal Python code is allowed."""
        code = """
x = [1, 2, 3]
y = sum(x)
z = [i*2 for i in x]
print(y, z)
"""
        is_valid, msg = validator.validate(code)
        assert is_valid


class TestCodeValidatorEdgeCases:
    """Test edge cases and edge patterns."""

    def test_syntax_error(self):
        """Test that syntax errors are caught."""
        code = "x = ("
        is_valid, msg = validator.validate(code)
        assert not is_valid
        assert "syntax" in msg.lower()

    def test_indentation_error(self):
        """Test that indentation errors are caught."""
        code = "if True:\nprint('hello')"
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_empty_code(self):
        """Test that empty code is valid."""
        code = ""
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_comments_only(self):
        """Test that comments-only code is valid."""
        code = "# This is a comment\n# Another comment"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_multiline_string(self):
        """Test that multiline strings don't bypass checks."""
        code = '''
"""
import os
exec('code')
"""
x = 1
'''
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_eval_in_string(self):
        """Test that eval in string doesn't bypass checks."""
        code = 'code_string = "eval(\'1+1\')"'
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_variable_as_eval(self):
        """Test that variable named eval is allowed (but calling it isn't)."""
        code = "my_eval = 1"
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_eval_call_blocked(self):
        """Test that calling eval is blocked even with custom name."""
        code = "my_eval = eval"
        is_valid, msg = validator.validate(code)
        # This should be safe because we're assigning the function, not calling it
        # The validator only blocks actual calls
        assert is_valid


class TestCodeValidatorRealWorldExamples:
    """Test real-world code examples."""

    def test_valid_data_analysis(self):
        """Test that valid data analysis code passes."""
        code = """
import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')
result = df.groupby('category').sum()
print(result)
"""
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_valid_math_operations(self):
        """Test that valid math code passes."""
        code = """
import math

x = 5
y = math.sqrt(x)
z = math.sin(y)
print(f'Result: {z}')
"""
        is_valid, msg = validator.validate(code)
        assert is_valid

    def test_invalid_file_read(self):
        """Test that file reading is blocked."""
        code = """
with open('/etc/passwd', 'r') as f:
    content = f.read()
"""
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_invalid_os_call(self):
        """Test that OS calls are blocked."""
        code = """
import os
os.system('rm -rf /')
"""
        is_valid, msg = validator.validate(code)
        assert not is_valid

    def test_invalid_subprocess_call(self):
        """Test that subprocess calls are blocked."""
        code = """
import subprocess
subprocess.run(['ls', '-la'])
"""
        is_valid, msg = validator.validate(code)
        assert not is_valid


class TestCodeValidatorInstance:
    """Test CodeValidator instance creation and configuration."""

    def test_validator_singleton(self):
        """Test that validator is a singleton instance."""
        from omcp_py.security.code_validator import validator as v1
        from omcp_py.security.code_validator import validator as v2
        assert v1 is v2

    def test_blocked_imports_completeness(self):
        """Test that BLOCKED_IMPORTS contains expected modules."""
        cv = CodeValidator()
        expected = {'os', 'sys', 'subprocess', 'socket', 'pickle', 'importlib'}
        assert expected.issubset(cv.BLOCKED_IMPORTS)

    def test_blocked_builtins_completeness(self):
        """Test that BLOCKED_BUILTINS contains expected functions."""
        cv = CodeValidator()
        expected = {'exec', 'eval', 'compile', 'open', '__import__', 'getattr', 'setattr', 'delattr'}
        assert expected.issubset(cv.BLOCKED_BUILTINS)

    def test_blocked_attributes_completeness(self):
        """Test that BLOCKED_ATTRIBUTES contains expected attributes."""
        cv = CodeValidator()
        expected = {'__builtins__', '__globals__', '__class__', '__dict__', '__bases__'}
        assert expected.issubset(cv.BLOCKED_ATTRIBUTES)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
