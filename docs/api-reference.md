# API Reference - OMCP Python Sandbox Server

## Overview

This document provides a complete reference for all MCP tools available in the OMCP Python Sandbox Server. Each tool is documented with its parameters, return values, examples, and error handling.

## Tool Categories

- [Core Sandbox Management](#core-sandbox-management)
- [Healthcare Data Tools](#healthcare-data-tools)
- [Legacy Tools](#legacy-tools)

---

## Core Sandbox Management

### `create_sandbox`

Creates a new isolated Python sandbox environment.

**Parameters:**
- `timeout` (optional, int): Sandbox timeout in seconds (default: 300)

**Returns:**
```json
{
  "success": true,
  "sandbox_id": "uuid-string",
  "created_at": "2024-01-01T12:00:00",
  "last_used": "2024-01-01T12:00:00"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Maximum number of sandboxes reached"
}
```

**Example:**
```python
# Create sandbox with default timeout
result = await mcp.create_sandbox()

# Create sandbox with custom timeout
result = await mcp.create_sandbox(timeout=600)
```

---

### `list_sandboxes`

Lists all active Python sandboxes.

**Parameters:**
- `include_inactive` (optional, bool): Include inactive sandboxes (default: false)

**Returns:**
```json
{
  "success": true,
  "sandboxes": [
    {
      "id": "uuid-string",
      "created_at": "2024-01-01T12:00:00",
      "last_used": "2024-01-01T12:00:00"
    }
  ],
  "count": 1
}
```

**Example:**
```python
# List active sandboxes only
result = await mcp.list_sandboxes()

# List all sandboxes including inactive
result = await mcp.list_sandboxes(include_inactive=true)
```

---

### `remove_sandbox`

Removes a Python sandbox container.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `force` (optional, bool): Force removal of active sandboxes (default: false)

**Returns:**
```json
{
  "success": true,
  "message": "Sandbox uuid-string removed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Sandbox uuid-string is still active. Use force=true to remove it."
}
```

**Example:**
```python
# Remove inactive sandbox
result = await mcp.remove_sandbox(sandbox_id="uuid-string")

# Force remove active sandbox
result = await mcp.remove_sandbox(sandbox_id="uuid-string", force=true)
```

---

### `execute_python_code`

Executes Python code in a secure sandbox environment.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `code` (required, string): The Python code to execute
- `timeout` (optional, int): Execution timeout in seconds (default: 30)

**Returns:**
```json
{
  "output": "Hello from sandbox!",
  "exit_code": 0
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Code execution timed out"
}
```

**Example:**
```python
code = '''
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'score': [85, 92, 78]
})

print(data.to_dict('records'))
'''

result = await mcp.execute_python_code(
    sandbox_id="uuid-string",
    code=code,
    timeout=60
)
```

---

### `install_package`

Installs Python packages in a sandbox.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `package` (required, string): Package name(s) to install
- `timeout` (optional, int): Installation timeout in seconds (default: 60)

**Returns:**
```json
{
  "output": "Package(s) installed successfully",
  "exit_code": 0
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Package installation failed"
}
```

**Example:**
```python
# Install single package
result = await mcp.install_package(
    sandbox_id="uuid-string",
    package="pandas"
)

# Install multiple packages
result = await mcp.install_package(
    sandbox_id="uuid-string",
    package="pandas numpy matplotlib"
)

# Install specific version
result = await mcp.install_package(
    sandbox_id="uuid-string",
    package="pandas==1.5.0"
)
```

---

## Healthcare Data Tools

### `create_omop_schema`

Creates OMOP CDM schema in PostgreSQL database.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox

**Returns:**
```json
{
  "output": "OMOP schema created successfully!",
  "exit_code": 0
}
```

**Error Response:**
```json
{
  "output": "ERROR: connection to server failed",
  "exit_code": 1
}
```

**Example:**
```python
result = await mcp.create_omop_schema(sandbox_id="uuid-string")
```

**Creates Tables:**
- `omop_cdm.person` - Patient demographics
- `omop_cdm.visit_occurrence` - Healthcare encounters
- `omop_cdm.condition_occurrence` - Medical conditions

---

### `load_synthea_to_postgres`

Loads Synthea CSV files into PostgreSQL OMOP database.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `csv_directory` (optional, string): Directory containing CSV files (default: "synthetic_data")

**Returns:**
```json
{
  "output": "Synthea data loading completed successfully!",
  "exit_code": 0
}
```

**Error Response:**
```json
{
  "output": "ERROR: File not found: /synthetic_data/patients.csv",
  "exit_code": 1
}
```

**Example:**
```python
# Load from default directory
result = await mcp.load_synthea_to_postgres(sandbox_id="uuid-string")

# Load from custom directory
result = await mcp.load_synthea_to_postgres(
    sandbox_id="uuid-string",
    csv_directory="/custom/data/path"
)
```

**Supported CSV Files:**
- `patients.csv` - Patient demographics
- `encounters.csv` - Healthcare encounters
- `conditions.csv` - Medical conditions

---

### `analyze_omop_data`

Performs structured analytics on OMOP data.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `analysis_type` (required, string): Type of analysis ("basic", "demographics", "conditions")

**Returns:**

**Basic Analysis:**
```json
{
  "output": "{\"total_patients\": 1000, \"total_visits\": 5000, \"total_conditions\": 8000}",
  "exit_code": 0
}
```

**Demographics Analysis:**
```json
{
  "output": "[{\"gender_concept_id\": 8507, \"patient_count\": 500, \"avg_age\": 45.2}]",
  "exit_code": 0
}
```

**Conditions Analysis:**
```json
{
  "output": "[{\"condition_concept_id\": 316139, \"occurrence_count\": 150, \"patient_count\": 120}]",
  "exit_code": 0
}
```

**Example:**
```python
# Basic counts
result = await mcp.analyze_omop_data(
    sandbox_id="uuid-string",
    analysis_type="basic"
)

# Demographics analysis
result = await mcp.analyze_omop_data(
    sandbox_id="uuid-string",
    analysis_type="demographics"
)

# Condition prevalence
result = await mcp.analyze_omop_data(
    sandbox_id="uuid-string",
    analysis_type="conditions"
)
```

---

### `llm_dataframe_operation`

Performs LLM-friendly dataframe operations on OMOP data.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `operation` (required, string): Natural language description of the operation
- `table_name` (optional, string): Target OMOP table (default: "person")

**Returns:**

**Count Operations:**
```json
{
  "output": "{\"total_count\": 1000}",
  "exit_code": 0
}
```

**Age Analysis:**
```json
{
  "output": "{\"average_age\": 45.2}",
  "exit_code": 0
}
```

**Gender Distribution:**
```json
{
  "output": "{\"gender_distribution\": {\"8507\": 500, \"8532\": 500}}",
  "exit_code": 0
}
```

**Example:**
```python
# Count operations
result = await mcp.llm_dataframe_operation(
    sandbox_id="uuid-string",
    operation="Count total patients"
)

result = await mcp.llm_dataframe_operation(
    sandbox_id="uuid-string",
    operation="Count unique conditions"
)

# Age analysis
result = await mcp.llm_dataframe_operation(
    sandbox_id="uuid-string",
    operation="Show age distribution"
)

result = await mcp.llm_dataframe_operation(
    sandbox_id="uuid-string",
    operation="Calculate average age"
)

# Gender analysis
result = await mcp.llm_dataframe_operation(
    sandbox_id="uuid-string",
    operation="Show gender distribution"
)

# Table-specific operations
result = await mcp.llm_dataframe_operation(
    sandbox_id="uuid-string",
    operation="Count total visits",
    table_name="visit_occurrence"
)
```

---

### `execute_sql_in_sandbox`

Executes SQL queries against the OMOP Postgres database from within the sandbox.

**Parameters:**
- `sandbox_id` (required, string): The unique identifier of the sandbox
- `sql` (required, string): The SQL query to execute

**Returns:**
```json
{
  "output": "[(1000,), (500,), (8000,)]",
  "exit_code": 0
}
```

**Error Response:**
```json
{
  "output": "ERROR: relation \"omop_cdm.person\" does not exist",
  "exit_code": 1
}
```

**Example:**
```python
# Basic count query
result = await mcp.execute_sql_in_sandbox(
    sandbox_id="uuid-string",
    sql="SELECT COUNT(*) FROM omop_cdm.person"
)

# Complex analytics query
result = await mcp.execute_sql_in_sandbox(
    sandbox_id="uuid-string",
    sql="""
    SELECT 
        gender_concept_id,
        COUNT(*) as patient_count,
        AVG(EXTRACT(YEAR FROM AGE(birth_datetime))) as avg_age
    FROM omop_cdm.person 
    WHERE birth_datetime IS NOT NULL
    GROUP BY gender_concept_id
    """
)
```

---

## Legacy Tools

### `query_duckdb`

Runs SQL queries against the local DuckDB file.

**Parameters:**
- `sql` (required, string): The SQL query to execute

**Returns:**
```json
{
  "success": true,
  "columns": ["count"],
  "result": [[1000]]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Table 'person' not found"
}
```

**Example:**
```python
result = await mcp.query_duckdb("SELECT COUNT(*) FROM person")
```

---

### `ping`

Health check endpoint.

**Parameters:** None

**Returns:**
```json
"pong"
```

**Example:**
```python
result = await mcp.ping()
```

---

## Error Handling

### Common Error Types

1. **Sandbox Not Found**
   ```json
   {
     "success": false,
     "error": "Sandbox uuid-string not found"
   }
   ```

2. **Database Connection Failed**
   ```json
   {
     "output": "ERROR: connection to server at \"db\" (172.18.0.2), port 5432 failed",
     "exit_code": 1
   }
   ```

3. **Package Installation Failed**
   ```json
   {
     "success": false,
     "error": "Package installation failed"
   }
   ```

4. **Timeout Errors**
   ```json
   {
     "success": false,
     "error": "Code execution timed out"
   }
   ```

5. **Resource Limits**
   ```json
   {
     "success": false,
     "error": "Maximum number of sandboxes reached"
   }
   ```

### Error Response Format

All tools follow a consistent error response format:

- **Success**: Tool-specific response format
- **Failure**: `{"success": false, "error": "error message"}`

### HTTP Status Codes

When used over HTTP transport:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Sandbox not found
- `500`: Internal Server Error
- `503`: Service Unavailable (database connection issues)

---

## Usage Patterns

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

# 5. Custom SQL
sql_results = await mcp.execute_sql_in_sandbox(
    sandbox_id,
    "SELECT COUNT(*) FROM omop_cdm.person WHERE gender_concept_id = 8507"
)

# 6. Cleanup
await mcp.remove_sandbox(sandbox_id, force=true)
```

### Error Handling Pattern

```python
try:
    result = await mcp.create_sandbox()
    if not result.get("success"):
        print(f"Failed to create sandbox: {result.get('error')}")
        return
    
    sandbox_id = result["sandbox_id"]
    
    # Continue with workflow...
    
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Always cleanup
    if sandbox_id:
        await mcp.remove_sandbox(sandbox_id, force=true)
```

---

## Performance Considerations

### Timeouts

- **Sandbox Creation**: 30 seconds
- **Package Installation**: 60 seconds
- **Code Execution**: 30 seconds (configurable)
- **Database Operations**: 60 seconds

### Resource Limits

- **Memory per Sandbox**: 512MB
- **CPU per Sandbox**: 50% of one core
- **Maximum Sandboxes**: 10 (configurable)
- **Sandbox Timeout**: 300 seconds (configurable)

### Best Practices

1. **Reuse Sandboxes**: Create one sandbox and reuse it for multiple operations
2. **Batch Operations**: Install multiple packages in one call
3. **Cleanup**: Always remove sandboxes when done
4. **Error Handling**: Implement proper error handling and cleanup
5. **Monitoring**: Monitor sandbox usage and resource consumption

---

*This API reference covers all available MCP tools. For implementation details, see the [Implementation Guide](implementation.md).* 