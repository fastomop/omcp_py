# OMCP Python Sandbox Server - WIKI

## 🏗️ Architecture Overview

The OMCP Python Sandbox Server is a secure, scalable platform for isolated Python code execution with advanced healthcare data analytics capabilities. The system uses Docker containers for sandboxing, PostgreSQL for data persistence, and the Model Context Protocol (MCP) for AI agent integration.

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client Layer                        │
│  (AI Agents, Inspector UI, Custom Clients)                    │
13: └─────────────────────┬───────────────────────────────────────────┘
                      │ JSON-RPC over stdio
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastMCP Server Layer                        │
│  (main.py - Tool Registration via Modular Components)          │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Docker API
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Sandbox Manager Layer                        │
│  (sandbox_manager.py - Container Lifecycle & Security)         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Docker Containers
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Sandbox Execution Layer                     │
│  (Isolated Python Environments + Script Injection)             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Network Access (None) / Validated Query
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                  │
│  (PostgreSQL OMOP DB + Synthea CSV Files)                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 System Architecture

### 1. **MCP Protocol Layer**
- **FastMCP Framework**: Simplified MCP implementation using decorators.
- **Modular Tool Registration**: Tools are imported from `src/omcp_py/tools/*.py`.
- **Request Handling**: JSON-RPC message processing.

### 2. **Sandbox Management Layer**
- **Container Lifecycle**: Create, manage, and cleanup Docker containers.
- **Resource Management**: CPU, memory, and timeout controls.
- **Security Enforcement**: User isolation, capability dropping, read-only filesystems.
- **Code Validation**: Pre-execution AST analysis blocks dangerous imports.

### 3. **Execution Layer**
- **Isolated Environments**: Each sandbox runs in a separate Docker container.
- **Script Library**: Complex logic resides in `src/omcp_py/scripts/omop/` and is injected at runtime.
- **Code Execution**: Secure Python code execution with output capture.

### 4. **Data Layer**
- **PostgreSQL Database**: OMOP CDM schema with healthcare data.
- **Synthea Integration**: CSV file processing and mapping.

## 🏥 Healthcare Data Integration

### Synthea-to-PostgreSQL Pipeline
The system provides a complete pipeline for processing Synthea synthetic healthcare data:
1. **Data Ingestion**: Load Synthea CSV files into PostgreSQL.
2. **Schema Mapping**: Automatic mapping to OMOP CDM tables.
3. **Data Validation**: Type checking and constraint enforcement.
4. **Analytics**: Structured and natural language query capabilities.

## 🔒 Security Architecture

### Static Analysis (New)
Before execution, the `CodeValidator` scans user code for:
- Dangerous imports (`os`, `subprocess`)
- Dangerous built-ins (`exec`, `eval`)

### Container Security
Each sandbox container is configured with multiple security layers:

```python
# Security configuration in sandbox_manager.py
container = self.client.containers.run(
    ...,
    network_mode="none",                # No internet
    read_only=True,                     # Read-only filesystem
    cap_drop=["ALL"],                   # Drop all capabilities
    security_opt=["no-new-privileges"], # Prevent privilege escalation
    user=1000                           # Non-root user
)
```

## 🛠️ Available MCP Tools

### Core Sandbox Management (`src/omcp_py/tools/sandbox_tools.py`)
| Tool | Description |
|------|-------------|
| `create_sandbox` | Create new isolated Python environment |
| `list_sandboxes` | List all active sandboxes |
| `remove_sandbox` | Remove sandbox container |
| `execute_python_code` | Run Python code in sandbox (Validated) |
| `install_package` | Install Python packages |

### Healthcare Data Tools (`src/omcp_py/tools/omop_tools.py`)
| Tool | Description |
|------|-------------|
| `create_omop_schema` | Create OMOP CDM database schema |
| `load_synthea_to_postgres` | Load Synthea CSV to PostgreSQL |
| `analyze_omop_data` | Run structured analytics |
| `llm_dataframe_operation` | Natural language queries |

### Query Tools (`src/omcp_py/tools/query_tools.py`)
| Tool | Description |
|------|-------------|
| `query_omop_table` | **Fast Path** direct database read (No container overhead) |
| `query_duckdb` | Query local DuckDB file |

## 📊 Analytics Capabilities

### Structured Analytics
The `analyze_omop_data` tool provides three types of structured analytics:
1. **Basic Counts** (`analysis_type: "basic"`)
2. **Demographics** (`analysis_type: "demographics"`)
3. **Condition Prevalence** (`analysis_type: "conditions"`)

### LLM-Friendly Operations
The `llm_dataframe_operation` tool supports natural language queries like "Count total patients" or "Show age distribution".

## 🔧 Configuration Management

### Environment Variables
The system uses a centralized configuration system via `config.py`.

- `SANDBOX_TIMEOUT`: Seconds before an inactive sandbox is reaped.
- `OMOP_DB_HOST`, `OMOP_DB_USER`, `OMOP_DB_PASSWORD`: Database credentials (injected into containers).
- `DOCKER_IMAGE`: The image to use for sandboxes (default: `python:3.11-slim`).

---

*This WIKI provides comprehensive documentation for the OMCP Python Sandbox Server.*