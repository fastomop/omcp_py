# OMCP Python Sandbox Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-1.11.0-green.svg)](https://modelcontextprotocol.io/)

## Overview

A secure, Docker-based Python sandbox server using the Model Context Protocol (MCP) for isolated code execution and advanced healthcare analytics. This project enables secure processing of Synthea synthetic healthcare data with PostgreSQL OMOP CDM integration and LLM-powered analytics.

## 🚀 Key Features

- **🔒 Secure Sandboxing**: Isolated Docker containers with resource limits and user isolation
- **🏥 Healthcare Data Pipeline**: Synthea-to-PostgreSQL with OMOP CDM mapping
- **🤖 LLM Integration**: Natural language queries for healthcare analytics
- **📊 Advanced Analytics**: Structured and LLM-friendly data exploration
- **🔧 MCP Protocol**: Model Context Protocol for AI agent integration
- **🐳 Docker Integration**: Containerized PostgreSQL database with data persistence

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│  FastMCP Server  │───▶│ Docker Sandbox  │
│  (AI Agent)     │    │   (main.py)      │    │  (Isolated)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ PostgreSQL DB    │    │ Synthea CSV     │
                       │ (OMOP CDM)       │    │ (Mounted Data)  │
                       └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.8+** with pip
- **Docker & Docker Compose**
- **Synthea CSV files** (optional, for healthcare data processing)

## Using UV for environment management

This project is configured to use `uv` for environment management. `uv` creates and manages Python virtual environments and can install the dependencies declared in `pyproject.toml` under `tool.uv`.

Quick start using `uv`:

```bash
# Install uv (see https://astral.sh/uv for instructions)
# Then create a uv-managed venv and install dependencies:
scripts/setup_uv.sh
source .venv/bin/activate
```

If you prefer not to use `uv`, you can still create a regular venv and install the packages listed in `pyproject.toml` or `requirements.txt`.


## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py

# Install dependencies
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database

```bash
# Start the OMOP database
docker-compose up -d db

# Verify it's running
docker-compose ps
```

### 3. Prepare Data (Optional)

Place your Synthea CSV files in the `synthetic_data/` directory:

```
synthetic_data/
├── patients.csv      # Patient demographics
├── encounters.csv    # Healthcare encounters  
├── conditions.csv    # Medical conditions
└── ...
```

### 4. Start the MCP Server

```bash
# Set Python path
export PYTHONPATH=src

# Start the server
python src/omcp_py/main.py
```

### 5. Connect with MCP Client

Use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) or your preferred MCP client:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Connect to the server
mcp-inspector python src/omcp_py/main.py
```

Then open http://127.0.0.1:6274 in your browser.

## 🏥 Healthcare Data Workflow

### Complete Synthea-to-PostgreSQL Pipeline

```python
# 1. Create sandbox and install packages
sandbox_id = await mcp.create_sandbox()
await mcp.install_package(sandbox_id, "pandas psycopg2-binary sqlalchemy")

# 2. Create OMOP CDM schema
await mcp.create_omop_schema(sandbox_id)

# 3. Load Synthea data
await mcp.load_synthea_to_postgres(sandbox_id, "/synthetic_data")

# 4. Run analytics
await mcp.analyze_omop_data(sandbox_id, "basic")
await mcp.llm_dataframe_operation(sandbox_id, "Count total patients")
```

### Available MCP Tools

| Tool | Description | Example |
|------|-------------|---------|
| `create_sandbox` | Create isolated Python environment | `create_sandbox()` |
| `install_package` | Install Python packages | `install_package(sandbox_id, "pandas")` |
| `create_omop_schema` | Create OMOP CDM database schema | `create_omop_schema(sandbox_id)` |
| `load_synthea_to_postgres` | Load Synthea CSV to PostgreSQL | `load_synthea_to_postgres(sandbox_id, "/synthetic_data")` |
| `analyze_omop_data` | Run structured analytics | `analyze_omop_data(sandbox_id, "basic")` |
| `llm_dataframe_operation` | Natural language queries | `llm_dataframe_operation(sandbox_id, "Count patients")` |
| `execute_sql_in_sandbox` | Direct SQL execution | `execute_sql_in_sandbox(sandbox_id, "SELECT COUNT(*) FROM person")` |
| `remove_sandbox` | Clean up sandbox | `remove_sandbox(sandbox_id, force=True)` |

## 📊 Analytics Examples

### Basic Counts
```json
{
  "total_patients": 1000,
  "total_visits": 5000,
  "total_conditions": 8000
}
```

### Demographics Analysis
```json
[
  {
    "gender_concept_id": 8507,
    "patient_count": 500,
    "avg_age": 45.2
  }
]
```

### LLM Natural Language Queries
```python
# These work with natural language
await mcp.llm_dataframe_operation(sandbox_id, "Count total patients")
await mcp.llm_dataframe_operation(sandbox_id, "Show age distribution")
await mcp.llm_dataframe_operation(sandbox_id, "Count unique conditions")
await mcp.llm_dataframe_operation(sandbox_id, "Show gender distribution")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Sandbox Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=10
DOCKER_IMAGE=python:3.11-slim
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=omop_user
DB_PASSWORD=omop_pass
DB_NAME=omop
```

### Docker Compose

The `docker-compose.yml` provides:
- PostgreSQL 15 with OMOP database
- Persistent data storage
- Synthea data directory mounting

## 🧪 Testing

### Run Integration Tests
```bash
python tests/test_synthea_integration.py
```

### Run Workflow Demo
```bash
python scripts/synthea_workflow.py
```

### Test Individual Components
```bash
# Test file structure
python -c "import src.omcp_py.main; print('✅ Main module loads successfully')"

# Test Docker Compose
docker-compose config
```

## 🔒 Security Features

- **Container Isolation**: Each sandbox runs in isolated Docker containers
- **Resource Limits**: CPU and memory restrictions per sandbox
- **User Isolation**: Non-root user execution
- **Network Security**: Controlled network access
- **File System**: Read-only filesystem with temporary mounts
- **Capability Dropping**: Removed dangerous Linux capabilities
- **Auto-cleanup**: Automatic removal of inactive sandboxes

## 📚 Documentation

- **[Synthea Usage Guide](docs/synthea_usage_guide.md)** - Detailed workflow documentation
- **[API Reference](docs/api-reference.md)** - Complete tool documentation
- **[Configuration Guide](docs/configuration.md)** - Environment and deployment setup
- **[Architecture Overview](docs/architecture.md)** - System design and components

## 🚀 Advanced Usage

### Custom Data Mapping

Extend the Synthea-to-OMOP mapping in `load_synthea_to_postgres`:

```python
synthea_mappings = {
    'custom_data.csv': {
        'table': 'omop_cdm.custom_table',
        'columns': {
            'custom_id': 'person_id',
            'custom_date': 'birth_datetime'
        }
    }
}
```

### Additional OMOP Tables

Extend the schema to include more OMOP CDM tables:
- `drug_exposure`
- `procedure_occurrence`
- `measurement`
- `observation`

### Custom Analytics

Create domain-specific analytics:

```python
# Custom Python code in sandbox
code = '''
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://omcp:postgres@db:5432/omcp')
df = pd.read_sql("SELECT * FROM omop_cdm.person", engine)

# Your custom analysis here
result = df.groupby('gender_concept_id').agg({
    'person_id': 'count',
    'birth_datetime': lambda x: pd.Timestamp.now().year - pd.to_datetime(x).dt.year.mean()
}).to_dict()

print(result)
'''

await mcp.execute_python_code(sandbox_id, code)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [FastMCP](https://gofastmcp.com/) for the Python MCP implementation
- [Synthea](https://github.com/synthetichealth/synthea) for synthetic healthcare data
- [OMOP CDM](https://ohdsi.github.io/CommonDataModel/) for healthcare data standards

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/fastomop/omcp_py/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fastomop/omcp_py/discussions)
- **Documentation**: [Wiki](https://github.com/fastomop/omcp_py/wiki)

---

Built by Zhangshu and the wider FastOMCP team  