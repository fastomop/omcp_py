# OMCP Python Sandbox Server - WIKI

## 🏗️ Architecture Overview

The OMCP Python Sandbox Server is a secure, scalable platform for isolated Python code execution with advanced healthcare data analytics capabilities. The system uses Docker containers for sandboxing, PostgreSQL for data persistence, and the Model Context Protocol (MCP) for AI agent integration.

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client Layer                        │
│  (AI Agents, Inspector UI, Custom Clients)                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │ JSON-RPC over stdio
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastMCP Server Layer                        │
│  (main.py - Tool Registration & Request Handling)              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Docker API
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Sandbox Manager Layer                        │
│  (sandbox_manager.py - Container Lifecycle Management)         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Docker Containers
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Sandbox Execution Layer                     │
│  (Isolated Python Environments with Security Restrictions)     │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Network Access
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                  │
│  (PostgreSQL OMOP DB + Synthea CSV Files)                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 System Architecture

### 1. **MCP Protocol Layer**
- **FastMCP Framework**: Simplified MCP implementation using decorators
- **Tool Registration**: Automatic tool discovery and registration
- **Request Handling**: JSON-RPC message processing
- **Error Handling**: Comprehensive error reporting and logging

### 2. **Sandbox Management Layer**
- **Container Lifecycle**: Create, manage, and cleanup Docker containers
- **Resource Management**: CPU, memory, and timeout controls
- **Security Enforcement**: User isolation, capability dropping, read-only filesystems
- **Persistence**: Database-backed sandbox metadata storage

### 3. **Execution Layer**
- **Isolated Environments**: Each sandbox runs in a separate Docker container
- **Package Management**: Dynamic package installation within sandboxes
- **Code Execution**: Secure Python code execution with output capture
- **Network Isolation**: Controlled network access for database connectivity

### 4. **Data Layer**
- **PostgreSQL Database**: OMOP CDM schema with healthcare data
- **Synthea Integration**: CSV file processing and mapping
- **Data Analytics**: Structured and LLM-friendly query capabilities

## 🏥 Healthcare Data Integration

### Synthea-to-PostgreSQL Pipeline

The system provides a complete pipeline for processing Synthea synthetic healthcare data:

1. **Data Ingestion**: Load Synthea CSV files into PostgreSQL
2. **Schema Mapping**: Automatic mapping to OMOP CDM tables
3. **Data Validation**: Type checking and constraint enforcement
4. **Analytics**: Structured and natural language query capabilities

### OMOP CDM Schema

The system creates and manages the following OMOP CDM tables:

```sql
-- Person table (demographics)
CREATE TABLE omop_cdm.person (
    person_id BIGINT PRIMARY KEY,
    gender_concept_id INTEGER,
    year_of_birth INTEGER,
    month_of_birth INTEGER,
    day_of_birth INTEGER,
    birth_datetime TIMESTAMP,
    death_datetime TIMESTAMP,
    race_concept_id INTEGER,
    ethnicity_concept_id INTEGER,
    person_source_value VARCHAR(50),
    gender_source_value VARCHAR(50)
);

-- Visit occurrences (encounters)
CREATE TABLE omop_cdm.visit_occurrence (
    visit_occurrence_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    visit_concept_id INTEGER,
    visit_start_datetime TIMESTAMP,
    visit_end_datetime TIMESTAMP,
    visit_type_concept_id INTEGER
);

-- Condition occurrences (diagnoses)
CREATE TABLE omop_cdm.condition_occurrence (
    condition_occurrence_id BIGINT PRIMARY KEY,
    person_id BIGINT,
    condition_concept_id INTEGER,
    condition_start_datetime TIMESTAMP,
    condition_end_datetime TIMESTAMP,
    condition_type_concept_id INTEGER
);
```

### Data Mapping

| Synthea CSV | OMOP Table | Key Mappings |
|-------------|------------|--------------|
| `patients.csv` | `omop_cdm.person` | `Id` → `person_id`, `BIRTHDATE` → `birth_datetime` |
| `encounters.csv` | `omop_cdm.visit_occurrence` | `Id` → `visit_occurrence_id`, `PATIENT` → `person_id` |
| `conditions.csv` | `omop_cdm.condition_occurrence` | `PATIENT` → `person_id`, `CODE` → `condition_concept_id` |

## 🔒 Security Architecture

### Container Security

Each sandbox container is configured with multiple security layers:

```python
# Security configuration in sandbox_manager.py
container = self.client.containers.run(
    self.config.docker_image,
    command=["sleep", "infinity"],
    detach=True,
    name=f"omcp-sandbox-{sandbox_id}",
    mem_limit="512m",                    # Memory limit
    cpu_period=100000,                   # CPU limits
    cpu_quota=50000,
    remove=True,                         # Auto-remove when stopped
    user=1000,                          # User isolation (non-root)
    read_only=True,                     # Read-only filesystem
    cap_drop=["ALL"],                   # Drop all capabilities
    security_opt=["no-new-privileges"], # Prevent privilege escalation
    tmpfs={                             # Temporary filesystem mounts
        "/tmp": "rw,noexec,nosuid,size=100M",
        "/sandbox": "rw,noexec,nosuid,size=500M"
    }
)
```

### Security Features

1. **User Isolation**: Containers run as non-root user (UID 1000)
2. **Capability Dropping**: All dangerous Linux capabilities removed
3. **Read-only Filesystem**: Prevents file system modifications
4. **Network Isolation**: Controlled network access
5. **Resource Limits**: CPU and memory restrictions
6. **Auto-cleanup**: Automatic removal of inactive sandboxes
7. **Command Injection Protection**: Proper command escaping

## 🛠️ Available MCP Tools

### Core Sandbox Management

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `create_sandbox` | Create new isolated Python environment | `timeout` (optional) | `sandbox_id`, `created_at`, `last_used` |
| `list_sandboxes` | List all active sandboxes | `include_inactive` (optional) | List of sandbox metadata |
| `remove_sandbox` | Remove sandbox container | `sandbox_id`, `force` (optional) | Success/error message |
| `execute_python_code` | Run Python code in sandbox | `sandbox_id`, `code`, `timeout` (optional) | Execution output and exit code |
| `install_package` | Install Python packages | `sandbox_id`, `package`, `timeout` (optional) | Installation output |

### Healthcare Data Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `create_omop_schema` | Create OMOP CDM database schema | `sandbox_id` | Schema creation status |
| `load_synthea_to_postgres` | Load Synthea CSV to PostgreSQL | `sandbox_id`, `csv_directory` | Data loading status |
| `analyze_omop_data` | Run structured analytics | `sandbox_id`, `analysis_type` | Analytics results (JSON) |
| `llm_dataframe_operation` | Natural language queries | `sandbox_id`, `operation`, `table_name` | Query results (JSON) |
| `execute_sql_in_sandbox` | Direct SQL execution | `sandbox_id`, `sql` | Query results |

### Legacy Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `query_duckdb` | Query local DuckDB file | `sql` | Query results |
| `ping` | Health check | None | "pong" |

## 📊 Analytics Capabilities

### Structured Analytics

The `analyze_omop_data` tool provides three types of structured analytics:

1. **Basic Counts** (`analysis_type: "basic"`)
   ```json
   {
     "total_patients": 1000,
     "total_visits": 5000,
     "total_conditions": 8000
   }
   ```

2. **Demographics** (`analysis_type: "demographics"`)
   ```json
   [
     {
       "gender_concept_id": 8507,
       "patient_count": 500,
       "avg_age": 45.2
     }
   ]
   ```

3. **Condition Prevalence** (`analysis_type: "conditions"`)
   ```json
   [
     {
       "condition_concept_id": 316139,
       "occurrence_count": 150,
       "patient_count": 120
     }
   ]
   ```

### LLM-Friendly Operations

The `llm_dataframe_operation` tool supports natural language queries:

```python
# Supported operations
operations = [
    "Count total patients",
    "Show age distribution",
    "Count unique conditions", 
    "Show gender distribution",
    "Calculate average age",
    "Get age statistics"
]
```

## 🔧 Configuration Management

### Environment Variables

The system uses a centralized configuration system via `config.py`:

```python
@dataclass
class SandboxConfig:
    # Sandbox settings
    sandbox_timeout: int = 300
    max_sandboxes: int = 10
    docker_image: str = "python:3.11-slim"
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "omop_user"
    db_password: str = "omop_pass"
    db_name: str = "omop"
    
    # Logging settings
    debug: bool = False
    log_level: str = "INFO"
```

### Docker Compose Configuration

The `docker-compose.yml` provides:

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: omop
      POSTGRES_USER: omop_user
      POSTGRES_PASSWORD: omop_pass
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./synthetic_data:/synthetic_data:ro  # Synthea data mount

volumes:
  pgdata:
```

## 🧪 Testing and Validation

### Integration Testing

The project includes comprehensive testing:

1. **File Structure Tests**: Verify all required files exist
2. **Docker Compose Tests**: Validate configuration
3. **Workflow Tests**: Test complete Synthea pipeline
4. **Syntax Validation**: Ensure code compiles correctly

### Test Commands

```bash
# Run all integration tests
python tests/test_synthea_integration.py

# Test individual components
python -m py_compile src/omcp_py/main.py
docker-compose config

# Test workflow
python scripts/synthea_workflow.py
```

## 🚀 Deployment and Scaling

### Production Considerations

1. **Database Scaling**: Use external PostgreSQL cluster
2. **Load Balancing**: Multiple MCP server instances
3. **Monitoring**: Add Prometheus metrics and logging
4. **Security**: Implement read-only database users
5. **Backup**: Regular database backups and snapshots

### Performance Optimization

1. **Connection Pooling**: Reuse database connections
2. **Batch Processing**: Process large datasets in chunks
3. **Caching**: Cache frequently accessed data
4. **Indexing**: Add database indexes for common queries

## 🔄 Workflow Examples

### Complete Healthcare Analytics Workflow

```python
# 1. Setup environment
sandbox_id = await mcp.create_sandbox()
await mcp.install_package(sandbox_id, "pandas psycopg2-binary sqlalchemy")

# 2. Initialize database
await mcp.create_omop_schema(sandbox_id)
await mcp.load_synthea_to_postgres(sandbox_id, "/synthetic_data")

# 3. Run analytics
basic_results = await mcp.analyze_omop_data(sandbox_id, "basic")
demo_results = await mcp.analyze_omop_data(sandbox_id, "demographics")

# 4. LLM queries
llm_results = await mcp.llm_dataframe_operation(sandbox_id, "Count total patients")

# 5. Cleanup
await mcp.remove_sandbox(sandbox_id, force=True)
```

### Custom Analytics Workflow

```python
# Custom Python analytics in sandbox
code = '''
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://omop_user:omop_pass@db:5432/omop')

# Load data
person_df = pd.read_sql("SELECT * FROM omop_cdm.person", engine)
condition_df = pd.read_sql("SELECT * FROM omop_cdm.condition_occurrence", engine)

# Custom analysis
diabetes_patients = condition_df[
    condition_df['condition_concept_id'] == 201820
]['person_id'].nunique()

print({"diabetes_patients": diabetes_patients})
'''

result = await mcp.execute_python_code(sandbox_id, code)
```

## 📚 Additional Resources

- **[Synthea Usage Guide](docs/synthea_usage_guide.md)**: Detailed workflow documentation
- **[API Reference](docs/api-reference.md)**: Complete tool documentation  
- **[Configuration Guide](docs/configuration.md)**: Environment setup
- **[Architecture Overview](docs/architecture.md)**: System design details

## 🔮 Future Enhancements

1. **Additional OMOP Tables**: drug_exposure, procedure_occurrence, measurement
2. **Advanced Analytics**: Machine learning model training
3. **Real-time Processing**: Stream processing capabilities
4. **Multi-tenant Support**: User isolation and quotas
5. **Plugin System**: Extensible tool architecture
6. **Monitoring Dashboard**: Real-time system metrics

---

*This WIKI provides comprehensive documentation for the OMCP Python Sandbox Server. For specific usage examples, see the [Synthea Usage Guide](docs/synthea_usage_guide.md).* 