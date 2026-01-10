# Changelog

All notable changes to the OMCP Python Sandbox project will be documented in this file.

## [0.2.0] - 2026-01-10

### 🏗️ Architecture Refactor
- **Modular Tool Design**: Split the monolithic `main.py` into focused modules:
  - `src/omcp_py/tools/sandbox_tools.py`: Core sandbox lifecycle management
  - `src/omcp_py/tools/omop_tools.py`: Specialized OMOP healthcare data tools
  - `src/omcp_py/tools/query_tools.py`: New "Fast Path" for direct database queries
- **Standalone Script Library**: Extracted embedded Python/SQL code strings into a dedicated script library at `src/omcp_py/scripts/omop/`.
- **Global State Management**: Introduced `src/omcp_py/core/globals.py` for cleanly managing singleton instances (`config`, `sandbox_manager`).

### 🔒 Security Improvements
- **Static Code Analysis**: implemented `CodeValidator` in `src/omcp_py/security/code_validator.py` to scan user code for dangerous imports (e.g., `os`, `subprocess`) before execution.
- **Robust Timeout Enforcement**: Updated `SandboxManager` to use the system `timeout` command, ensuring that runaway processes are strictly terminated even if they ignore signals.
- **Secure Credentials**: Database credentials are now injected into containers via environment variables at runtime, preventing them from being hardcoded or visible in execution strings.

### ⚡ Performance Optimizations
- **Direct Query Path**: Introduced `query_omop_table` tool which allows read-only OMOP queries to run directly against the database, bypassing the 2-3 second container startup overhead for simple retrievals.
- **Connection Efficiency**: Improved database connection handling in the new script library.

### 🐛 Bug Fixes
- Fixed return value handling in healthcare tools (incorrectly expecting objects instead of dicts).
- Fixed database session initialization to be lazy, preventing module import failures when DB is offline.
- Fixed dependency configurations in `pyproject.toml`.

## [0.1.0] - 2024-03-20
- Initial release of OMCP Python Sandbox.
