# Codebase Structure

## Directory Layout

The project follows a modular Python package structure with clearly separated concerns.

```
omcp_py/
├── src/
│   └── omcp_py/
│       ├── core/               # Core infrastructure components
│       │   ├── globals.py      # App-wide singletons (config, manager)
│       │   ├── db.py           # Database connection & pooling
│       │   └── __init__.py
│       │
│       ├── security/           # Security logic
│       │   ├── code_validator.py # Static AST analyzer
│       │   └── __init__.py
│       │
│       ├── tools/              # MCP Tool Implementations
│       │   ├── sandbox_tools.py # Lifecycle & Execution tools
│       │   ├── omop_tools.py    # Healthcare/OMOP tools
│       │   ├── query_tools.py   # Direct query optimizations
│       │   └── __init__.py
│       │
│       ├── scripts/            # Standalone Script Library
│       │   └── omop/
│       │       ├── create_schema.py
│       │       ├── load_synthea.py
│       │       └── analyze.py
│       │
│       ├── config.py           # Configuration management
│       ├── main.py             # Application entry point
│       └── sandbox_manager.py  # Docker orchestration logic
│
├── docs/                       # Project documentation
│   ├── architecture.md
│   ├── codebase-structure.md
│   └── security.md
│
├── tests/                      # Validation scripts
├── Dockerfile                  # Sandbox image definition
├── pyproject.toml              # Dependencies & build config
└── README.md                   # Project overview
```

## Key Files & Modules

### `src/omcp_py/main.py`
The glue code. It sets up the `FastMCP` server, configures logging, and registers the tools imported from the `tools/` directory.

### `src/omcp_py/core/globals.py`
Holds the singleton instances of `Config` and `SandboxManager`. This ensures that all modules share the same state without circular dependency issues.

### `src/omcp_py/sandbox_manager.py`
The heart of the sandbox system. It wraps the `docker-py` client and provides high-level methods to `create_sandbox`, `execute_code`, and `remove_sandbox`. It handles all the Docker-specific complexity (mounting, networking, limits).

### `src/omcp_py/security/code_validator.py`
Contains the `CodeValidator` class which uses Python's `ast` module to inspect code before execution. It defines a blocklist of dangerous modules.

### `src/omcp_py/tools/*.py`
- **`sandbox_tools.py`**: Generic sandbox operations.
- **`omop_tools.py`**: Specialized logic for interacting with the OMOP Common Data Model. It reads scripts from `src/omcp_py/scripts/omop/`.
- **`query_tools.py`**: Optimized tools for direct database access when container isolation is not required (e.g. reading public reference data).

### `src/omcp_py/scripts/`
A libraries of standalone Python scripts. These are essentially "stored procedures" written in Python that perform complex tasks inside the sandbox. Keeping them as separate files allows for better developer experience (testing, linting) compared to storing code in string literals.