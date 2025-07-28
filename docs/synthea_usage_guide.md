# Synthea-to-PostgreSQL Usage Guide

## Overview

This guide walks you through using the OMCP Python Sandbox Server to process Synthea synthetic healthcare data and load it into a PostgreSQL database with OMOP CDM schema, then perform analytics using LLM-friendly tools.

## Prerequisites

1. **Docker and Docker Compose** installed and running
2. **Python 3.8+** with pip
3. **Synthea CSV files** in the `synthetic_data/` directory
4. **MCP client** (Inspector UI, Cursor, or custom client)

## Step-by-Step Workflow

### 1. Start the Infrastructure

```bash
# Start PostgreSQL database
docker-compose up -d db

# Verify database is running
docker-compose ps
```

### 2. Start the MCP Server

```bash
# Set Python path
export PYTHONPATH=src

# Start the server
python src/omcp_py/main.py
```

### 3. Connect with MCP Client

Use MCP Inspector UI or your preferred MCP client to connect to the server.

### 4. Create and Configure Sandbox

```python
# Create a new sandbox
sandbox_response = await client.call_tool("create_sandbox", {})
sandbox_id = sandbox_response["sandbox_id"]

# Install required packages
packages = ["pandas", "psycopg2-binary", "sqlalchemy"]
for package in packages:
    await client.call_tool("install_package", {
        "sandbox_id": sandbox_id,
        "package": package
    })
```

### 5. Set Up OMOP Schema

```python
# Create OMOP CDM schema and tables
await client.call_tool("create_omop_schema", {
    "sandbox_id": sandbox_id
})
```

This creates:
- `omop_cdm` schema
- `person` table
- `visit_occurrence` table  
- `condition_occurrence` table

### 6. Load Synthea Data

```python
# Load CSV files into PostgreSQL
await client.call_tool("load_synthea_to_postgres", {
    "sandbox_id": sandbox_id,
    "csv_directory": "/synthetic_data"
})
```

This automatically:
- Maps Synthea CSV columns to OMOP CDM fields
- Loads data into the appropriate tables
- Handles data type conversions

### 7. Run Analytics

#### Basic Analytics

```python
# Get basic counts
basic_results = await client.call_tool("analyze_omop_data", {
    "sandbox_id": sandbox_id,
    "analysis_type": "basic"
})

# Get demographics
demo_results = await client.call_tool("analyze_omop_data", {
    "sandbox_id": sandbox_id,
    "analysis_type": "demographics"
})

# Get condition prevalence
condition_results = await client.call_tool("analyze_omop_data", {
    "sandbox_id": sandbox_id,
    "analysis_type": "conditions"
})
```

#### LLM-Friendly Operations

```python
# Natural language queries
queries = [
    "Count total patients",
    "Show age distribution", 
    "Count unique conditions",
    "Show gender distribution"
]

for query in queries:
    result = await client.call_tool("llm_dataframe_operation", {
        "sandbox_id": sandbox_id,
        "operation": query
    })
    print(f"{query}: {result['output']}")
```

### 8. Clean Up

```python
# Remove the sandbox
await client.call_tool("remove_sandbox", {
    "sandbox_id": sandbox_id,
    "force": True
})
```

## Data Mapping

### Synthea to OMOP CDM Mapping

| Synthea CSV | OMOP Table | Key Mappings |
|-------------|------------|--------------|
| `patients.csv` | `omop_cdm.person` | `Id` → `person_id`, `BIRTHDATE` → `birth_datetime` |
| `encounters.csv` | `omop_cdm.visit_occurrence` | `Id` → `visit_occurrence_id`, `PATIENT` → `person_id` |
| `conditions.csv` | `omop_cdm.condition_occurrence` | `PATIENT` → `person_id`, `CODE` → `condition_concept_id` |

### Required CSV Files

Place these files in `synthetic_data/`:
- `patients.csv` - Patient demographics
- `encounters.csv` - Healthcare encounters
- `conditions.csv` - Medical conditions

## Analytics Examples

### Basic Counts
```json
{
  "total_patients": 1000,
  "total_visits": 5000,
  "total_conditions": 8000
}
```

### Demographics
```json
[
  {
    "gender_concept_id": 8507,
    "patient_count": 500,
    "avg_age": 45.2
  },
  {
    "gender_concept_id": 8532,
    "patient_count": 500,
    "avg_age": 43.8
  }
]
```

### LLM Operations
```json
{
  "total_count": 1000,
  "age_distribution": {
    "25": 150,
    "30": 200,
    "35": 180
  },
  "gender_distribution": {
    "8507": 500,
    "8532": 500
  }
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure PostgreSQL container is running: `docker-compose ps`
   - Check database credentials in `docker-compose.yml`

2. **CSV Files Not Found**
   - Verify files exist in `synthetic_data/` directory
   - Check file permissions and naming

3. **Package Installation Failed**
   - Retry with individual packages
   - Check network connectivity in sandbox

4. **Schema Creation Failed**
   - Ensure database is accessible
   - Check for existing schema conflicts

### Debug Commands

```python
# Test database connection
await client.call_tool("execute_sql_in_sandbox", {
    "sandbox_id": sandbox_id,
    "sql": "SELECT version();"
})

# List available tables
await client.call_tool("execute_sql_in_sandbox", {
    "sandbox_id": sandbox_id,
    "sql": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'omop_cdm';"
})
```

## Advanced Usage

### Custom Data Mapping

Modify the `synthea_mappings` dictionary in the `load_synthea_to_postgres` tool to customize column mappings.

### Additional OMOP Tables

Extend the schema creation to include more OMOP CDM tables like:
- `drug_exposure`
- `procedure_occurrence`
- `measurement`
- `observation`

### Custom Analytics

Create custom analytics by modifying the `analyze_omop_data` tool or using `execute_python_code` for complex queries.

## Performance Tips

1. **Batch Processing**: For large datasets, process in smaller chunks
2. **Indexing**: Add database indexes for frequently queried columns
3. **Memory Management**: Monitor sandbox memory usage during large operations
4. **Connection Pooling**: Use connection pooling for multiple operations

## Security Considerations

1. **Network Isolation**: Sandboxes are isolated from external networks
2. **Data Access**: Database access is restricted to sandbox containers
3. **Resource Limits**: CPU and memory limits prevent resource exhaustion
4. **User Isolation**: Sandboxes run as non-root users

## Next Steps

1. **Extend OMOP Schema**: Add more tables and relationships
2. **Custom Analytics**: Implement domain-specific healthcare analytics
3. **Integration**: Connect with external healthcare systems
4. **Monitoring**: Add comprehensive logging and monitoring
5. **Testing**: Implement automated testing for data quality and pipeline integrity 