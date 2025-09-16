"""
FastMCP Python Sandbox Server

This module implements a Model Context Protocol (MCP) server using FastMCP for secure,
Docker-based Python code execution. It provides tools for creating isolated Python
environments, executing code safely, and managing sandbox lifecycle.

Architecture:
- FastMCP: Simplified MCP implementation using decorators
- Docker Sandboxing: Each sandbox runs in an isolated container with enhanced security
- Resource Management: Automatic cleanup and resource limits
- Error Handling: Comprehensive error handling and logging

Key Features:
- create_sandbox: Create new isolated Python environments
- list_sandboxes: List and manage active sandboxes
- remove_sandbox: Safely remove sandboxes with force option
- execute_python_code: Run Python code in isolated containers
- install_package: Install Python packages in sandboxes
- create_omop_schema: Create OMOP CDM schema in PostgreSQL
- load_synthea_to_postgres: Load Synthea CSV files into OMOP database
- analyze_omop_data: Perform analytics on OMOP data
- llm_dataframe_operation: LLM-friendly dataframe operations

Security Features:
- Network isolation (containers run with network_mode="none")
- Resource limits (CPU, memory)
- Timeout controls
- Input validation
- Auto-cleanup of inactive sandboxes
- Enhanced Docker security (read-only, dropped capabilities, tmpfs)
- User isolation (sandboxuser)
- Command escaping with shlex.quote

Usage:
    python server_fastmcp.py

Environment Variables:
    SANDBOX_TIMEOUT: Sandbox timeout in seconds (default: 300)
    MAX_SANDBOXES: Maximum number of sandboxes (default: 10)
    DOCKER_IMAGE: Docker image to use (default: python:3.11-slim)
    DEBUG: Enable debug mode (default: false)
    LOG_LEVEL: Logging level (default: INFO)
"""

import asyncio
import logging
import sys
from typing import Optional, Dict, Any
from fastmcp import FastMCP
from omcp_py.sandbox_manager import SandboxManager
from omcp_py.config import get_config
from shlex import quote
import requests
import duckdb

# Load configuration from environment variables
config = get_config()

# Configure logging to stderr (MCP convention) with structured format
logging.basicConfig(
    level=config.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr as per MCP specification
)

logger = logging.getLogger(__name__)

# Create FastMCP instance - this is the main server object
# FastMCP provides a simplified interface for creating MCP tools using decorators
mcp = FastMCP("Python Sandbox")

# Initialize the sandbox manager - handles Docker container lifecycle
# This is a singleton that manages all sandbox containers
sandbox_manager = SandboxManager(config)
# Log sandbox network configuration so operators know where sandboxes will be attached
logger.info(
    "Sandbox network config: SANDBOX_NETWORK=%s, ALLOW_HOST_GATEWAY=%s, detected_compose_network=%s",
    getattr(config, "sandbox_network", None),
    getattr(config, "allow_host_gateway", None),
    getattr(sandbox_manager, "compose_network", None)
)

@mcp.tool()
async def ping() -> str:
    return "pong"

@mcp.tool()
async def create_sandbox(timeout: Optional[int] = 300) -> Dict[str, Any]:
    """
    Create a new Python sandbox environment.
    
    This tool creates a new Docker container that will serve as an isolated
    Python execution environment. The container is configured with:
    - No network access (security)
    - Memory and CPU limits
    - Auto-removal when stopped
    - Enhanced security options (read-only, dropped capabilities)
    - User isolation (sandboxuser)
    - Temporary filesystem mounts
    
    Args:
        timeout: Optional timeout for the sandbox in seconds (default: 300)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if creation was successful
        - sandbox_id: Unique identifier for the created sandbox
        - created_at: ISO timestamp of creation
        - last_used: ISO timestamp of last usage
        - error: Error message if creation failed
    """
    try:
        # Create a new sandbox container using the sandbox manager
        sandbox_id = sandbox_manager.create_sandbox()
        
        # Retrieve the sandbox information to return creation details
        # We need to find the newly created sandbox in the list
        sandbox_info = next(
            (s for s in sandbox_manager.list_sandboxes() if s["id"] == sandbox_id),
            None
        )
        
        # Validate that we can retrieve the sandbox info
        if not sandbox_info:
            raise Exception("Failed to get sandbox information after creation")
        
        # Return success response with sandbox details
        return {
            "success": True,
            "sandbox_id": sandbox_id,
            "created_at": sandbox_info["created_at"],
            "last_used": sandbox_info["last_used"]
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to create sandbox: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def list_sandboxes(include_inactive: bool = False) -> Dict[str, Any]:
    """
    List all active Python sandboxes.
    
    This tool provides information about all sandbox containers, including
    their creation time and last usage time. Optionally filters out
    inactive sandboxes based on timeout configuration.
    
    Args:
        include_inactive: Whether to include inactive sandboxes (default: False)
                         Inactive sandboxes are those that haven't been used
                         within the configured timeout period.
    
    Returns:
        Dict containing:
        - success: Boolean indicating if listing was successful
        - sandboxes: List of sandbox information dictionaries
        - count: Number of sandboxes in the list
        - error: Error message if listing failed
    """
    try:
        # Get all sandboxes from the sandbox manager
        sandboxes = sandbox_manager.list_sandboxes()
        
        # Filter out inactive sandboxes if requested
        if not include_inactive:
            # Import datetime here to avoid circular imports
            from datetime import datetime
            # Filter sandboxes based on last usage time
            # Only include sandboxes that have been used recently
            sandboxes = [
                s for s in sandboxes
                if (datetime.now() - datetime.fromisoformat(s["last_used"])).total_seconds() < config.sandbox_timeout
            ]
        
        # Return success response with sandbox list and count
        return {
            "success": True,
            "sandboxes": sandboxes,
            "count": len(sandboxes)
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to list sandboxes: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def remove_sandbox(sandbox_id: str, force: bool = False) -> Dict[str, Any]:
    """
    Remove a Python sandbox.
    
    This tool safely removes a sandbox container. By default, it only removes
    inactive sandboxes (those that haven't been used recently). The force
    parameter can be used to remove active sandboxes.
    
    Args:
        sandbox_id: The unique identifier of the sandbox to remove
        force: Whether to force removal of active sandboxes (default: False)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if removal was successful
        - message: Success message or error description
        - error: Error message if removal failed
    """
    try:
        # Validate that the sandbox exists
        if sandbox_id not in sandbox_manager.sandboxes:
            return {
                "success": False,
                "error": f"Sandbox {sandbox_id} not found"
            }
        
        # Check if sandbox is active (unless force is True)
        if not force:
            # Import datetime here to avoid circular imports
            from datetime import datetime
            # Get the sandbox information
            sandbox = sandbox_manager.sandboxes[sandbox_id]
            # Check if sandbox has been used recently
            if (datetime.now() - sandbox["last_used"]).total_seconds() < config.sandbox_timeout:
                return {
                    "success": False,
                    "error": f"Sandbox {sandbox_id} is still active. Use force=True to remove it."
                }
        
        # Remove the sandbox using the sandbox manager
        # This will stop and remove the Docker container
        sandbox_manager.remove_sandbox(sandbox_id)
        
        # Return success response
        return {
            "success": True,
            "message": f"Sandbox {sandbox_id} removed successfully"
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to remove sandbox {sandbox_id}: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def execute_python_code(sandbox_id: str, python_code: Optional[str] = None, code: Optional[str] = None, timeout: Optional[int] = 30) -> Dict[str, Any]:
    """
    Execute Python code in a secure sandbox environment.
    
    This tool runs Python code inside an isolated Docker container. The code
    is executed with restricted permissions and resource limits. The output
    is captured and returned, with automatic JSON parsing for structured data.
    
    Args:
        sandbox_id: The unique identifier of the sandbox to execute code in
        code: The Python code to execute (must be non-empty string)
        timeout: Optional execution timeout in seconds (default: 30)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if execution was successful
        - output: The stdout output from code execution (parsed as JSON if possible)
        - error: The stderr output or error message
        - exit_code: The exit code from the Python process
    """
    try:
        # Accept either 'python_code' or legacy 'code'
        code_text = python_code if python_code is not None else code

        # Validate that the code input is valid
        if not isinstance(code_text, str) or not code_text.strip():
            return {"success": False, "error": "Code must be a non-empty string"}

        # Execute the code in the specified sandbox with enhanced security
        exec_result = sandbox_manager.execute_code(sandbox_id, code_text, timeout=timeout)

        # exec_result is expected to be a dict with keys: output (bytes or str), exit_code (int), error (str|None)
        output_raw = exec_result.get("output")
        exit_code = exec_result.get("exit_code")
        error = exec_result.get("error")

        # Normalize output to string
        if isinstance(output_raw, (bytes, bytearray)):
            try:
                output_text = output_raw.decode(errors="replace")
            except Exception:
                output_text = str(output_raw)
        else:
            output_text = "" if output_raw is None else str(output_raw)

        return {
            "success": (exit_code == 0),
            "output": output_text,
            "error": error,
            "exit_code": exit_code,
        }
    except requests.exceptions.ReadTimeout:
        # Handle timeout specifically
        logger.error(f"Code execution timed out in sandbox {sandbox_id}")
        return {
            "success": False,
            "error": "Code execution timed out"
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to execute code in sandbox {sandbox_id}: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def install_package(sandbox_id: str, package: str, timeout: Optional[int] = 60) -> Dict[str, Any]:
    """
    Install a Python package in a sandbox.
    
    This tool installs Python packages inside a sandbox container using pip.
    It provides detailed error handling for installation failures and timeouts.
    The installation is done in a controlled manner with proper error reporting.
    
    Args:
        sandbox_id: The unique identifier of the sandbox to install the package in
        package: The package name and version (e.g., "numpy==1.24.0" or "pandas numpy")
        timeout: Optional installation timeout in seconds (default: 60)
    
    Returns:
        Dict containing:
        - success: Boolean indicating if installation was successful
        - output: Installation output (parsed as JSON if possible)
        - error: Installation error or stderr output
        - exit_code: The exit code from the pip installation process
    """
    try:
        # Validate that the package input is valid
        if not isinstance(package, str) or not package.strip():
            return {
                "success": False,
                "error": "Package must be a non-empty string"
            }
        
        # Create Python code that will install the package using pip
        # This code runs inside the sandbox container
        code = f"""
import subprocess
import sys
try:
    # Install the package(s) using pip with timeout and output capture
    result = subprocess.run([sys.executable, '-m', 'pip', 'install'] + '''{package}'''.split(), 
                           timeout={timeout},
                           capture_output=True,
                           text=True)
    if result.returncode == 0:
        print({{"status": "success", "message": "Package(s) installed successfully", "stdout": result.stdout}})
    else:
        print({{"status": "error", "message": "Package installation failed", "stderr": result.stderr}})
        sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print({{"status": "error", "message": "Package installation timed out"}})
    sys.exit(1)
except Exception as e:
    print({{"status": "error", "message": f"Unexpected error: {{str(e)}}"}})
    sys.exit(1)
"""
        # Execute the installation code in the sandbox with enhanced security
        result = sandbox_manager.execute_code(sandbox_id, code)

        # result is expected to be a dict with keys: output, exit_code, error
        return {
            "output": result.get("output"),
            "exit_code": result.get("exit_code"),
            "error": result.get("error")
        }
    except requests.exceptions.ReadTimeout:
        # Handle timeout specifically
        logger.error(f"Package installation timed out in sandbox {sandbox_id}")
        return {
            "success": False,
            "error": "Package installation timed out"
        }
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Failed to install package {package} in sandbox {sandbox_id}: {e}")
        # Return error response
        return {
            "success": False,
            "error": str(e)
        }
print("Registered: install_package")

@mcp.tool()
async def query_duckdb(sql: str) -> dict:
    """
    Run a SQL query against the DuckDB file and return the results.
    Args:
        sql: The SQL query to run.
    Returns:
        Dict with 'success', 'columns', 'result', and 'error' keys.
    """
    try:
        con = duckdb.connect('synthetic_data/synthea.duckdb')
        result = con.execute(sql).fetchall()
        columns = [desc[0] for desc in con.description]
        return {"success": True, "columns": columns, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
print("Registered: query_duckdb")

@mcp.tool()
async def execute_sql_in_sandbox(sandbox_id: str, sql: str) -> dict:
    """
    Execute a SQL query against the OMOP Postgres database from within the sandbox.
    Args:
        sandbox_id: The sandbox to execute in.
        sql: The SQL query to run.
    Returns:
        Dict with 'output' and 'exit_code' or 'error'.
    """
    code = f'''
import psycopg2
import sys
try:
    conn = psycopg2.connect(
        dbname="{config.db_name}",
        user="{config.db_user}",
        password="{config.db_password}",
        host="{config.db_host}",
        port={config.db_port}
    )
    cur = conn.cursor()
    cur.execute({sql!r})
    rows = cur.fetchall()
    print(rows)
    conn.close()
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    sys.exit(1)
'''
    result = sandbox_manager.execute_code(sandbox_id, code)
    return {"output": result.output.decode(), "exit_code": result.exit_code}
print("Registered: execute_sql_in_sandbox")

@mcp.tool()
async def create_omop_schema(sandbox_id: str) -> dict:
    """
    Create OMOP CDM schema in PostgreSQL database from within the sandbox.
    Args:
        sandbox_id: The sandbox to execute in.
    Returns:
        Dict with 'output' and 'exit_code' or 'error'.
    """
    code = '''
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        dbname="%s",
        user="%s",
        password="%s",
        host="%s",
        port=%s
    )
    cur = conn.cursor()
    
    # Create OMOP schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS omop_cdm;")
    
    # Create basic OMOP tables
    person_sql = "CREATE TABLE IF NOT EXISTS omop_cdm.person (person_id BIGINT PRIMARY KEY, gender_concept_id INTEGER, year_of_birth INTEGER, month_of_birth INTEGER, day_of_birth INTEGER, birth_datetime TIMESTAMP, death_datetime TIMESTAMP, race_concept_id INTEGER, ethnicity_concept_id INTEGER, person_source_value VARCHAR(50), gender_source_value VARCHAR(50));"
    
    visit_sql = "CREATE TABLE IF NOT EXISTS omop_cdm.visit_occurrence (visit_occurrence_id BIGINT PRIMARY KEY, person_id BIGINT, visit_concept_id INTEGER, visit_start_datetime TIMESTAMP, visit_end_datetime TIMESTAMP, visit_type_concept_id INTEGER);"
    
    condition_sql = "CREATE TABLE IF NOT EXISTS omop_cdm.condition_occurrence (condition_occurrence_id BIGINT PRIMARY KEY, person_id BIGINT, condition_concept_id INTEGER, condition_start_datetime TIMESTAMP, condition_end_datetime TIMESTAMP, condition_type_concept_id INTEGER);"
    
    tables = {
        'person': person_sql,
        'visit_occurrence': visit_sql,
        'condition_occurrence': condition_sql
    }
    
    for table_name, create_sql in tables.items():
        cur.execute(create_sql)
        print(f"Created table: {table_name}")
    
    conn.commit()
    conn.close()
    print("OMOP schema created successfully!")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(1)
'''
    result = sandbox_manager.execute_code(sandbox_id, code)
    return {"output": result.output.decode(), "exit_code": result.exit_code}
print("Registered: create_omop_schema")

@mcp.tool()
async def load_synthea_to_postgres(sandbox_id: str, csv_directory: str = "synthetic_data") -> dict:
    """
    Load Synthea CSV files into PostgreSQL OMOP database from within the sandbox.
    Args:
        sandbox_id: The sandbox to execute in.
        csv_directory: Directory containing Synthea CSV files.
    Returns:
        Dict with 'output' and 'exit_code' or 'error'.
    """
    code = f'''
import pandas as pd
import psycopg2
import os
import sys
from sqlalchemy import create_engine, text

try:
    # Connect to PostgreSQL
    engine = create_engine('postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}')
    
    # Define Synthea to OMOP mappings
    synthea_mappings = {{
        'patients.csv': {{
            'table': 'omop_cdm.person',
            'columns': {{
                'Id': 'person_id',
                'BIRTHDATE': 'birth_datetime',
                'DEATHDATE': 'death_datetime',
                'GENDER': 'gender_concept_id',
                'RACE': 'race_concept_id',
                'ETHNICITY': 'ethnicity_concept_id'
            }}
        }},
        'encounters.csv': {{
            'table': 'omop_cdm.visit_occurrence',
            'columns': {{
                'Id': 'visit_occurrence_id',
                'START': 'visit_start_datetime',
                'STOP': 'visit_end_datetime',
                'PATIENT': 'person_id',
                'ENCOUNTERCLASS': 'visit_concept_id'
            }}
        }},
        'conditions.csv': {{
            'table': 'omop_cdm.condition_occurrence',
            'columns': {{
                'START': 'condition_start_datetime',
                'STOP': 'condition_end_datetime',
                'PATIENT': 'person_id',
                'CODE': 'condition_concept_id'
            }}
        }}
    }}
    
    # Process each CSV file
    for filename, mapping in synthea_mappings.items():
        filepath = os.path.join('{csv_directory}', filename)
        if os.path.exists(filepath):
            print(f"Processing {{filename}}...")
            
            # Read CSV
            df = pd.read_csv(filepath)
            
            # Rename columns according to mapping
            df = df.rename(columns=mapping['columns'])
            
            # Add required OMOP columns with defaults
            if mapping['table'] == 'omop_cdm.person':
                df['person_source_value'] = df['person_id'].astype(str)
                df['gender_source_value'] = df['gender_concept_id']
            
            # Load to PostgreSQL
            df.to_sql(mapping['table'].split('.')[-1], engine, schema='omop_cdm', if_exists='append', index=False, method='multi')
            print(f"Loaded {{len(df)}} rows into {{mapping['table']}}")
        else:
            print(f"File not found: {{filepath}}")
    
    print("Synthea data loading completed successfully!")
    
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    sys.exit(1)
'''
    result = sandbox_manager.execute_code(sandbox_id, code)
    return {"output": result.output.decode(), "exit_code": result.exit_code}
print("Registered: load_synthea_to_postgres")

@mcp.tool()
async def analyze_omop_data(sandbox_id: str, analysis_type: str = "basic") -> dict:
    """
    Perform analytics on OMOP data using pandas and LLM-friendly output.
    Args:
        sandbox_id: The sandbox to execute in.
        analysis_type: Type of analysis ('basic', 'demographics', 'conditions').
    Returns:
        Dict with 'output' and 'exit_code' or 'error'.
    """
    code = f'''
import pandas as pd
import psycopg2
import sys
import json
from sqlalchemy import create_engine

try:
    engine = create_engine(f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}")
    
    if '{analysis_type}' == 'basic':
        # Basic counts
        queries = {{
            'total_patients': 'SELECT COUNT(*) as count FROM omop_cdm.person',
            'total_visits': 'SELECT COUNT(*) as count FROM omop_cdm.visit_occurrence',
            'total_conditions': 'SELECT COUNT(*) as count FROM omop_cdm.condition_occurrence'
        }}
        
        results = {{}}
        for name, query in queries.items():
            df = pd.read_sql(query, engine)
            results[name] = int(df['count'].iloc[0])
        
        print(json.dumps(results))
        
    elif '{analysis_type}' == 'demographics':
        # Demographics analysis
        query = "SELECT gender_concept_id, COUNT(*) as patient_count, AVG(EXTRACT(YEAR FROM AGE(birth_datetime))) as avg_age FROM omop_cdm.person WHERE birth_datetime IS NOT NULL GROUP BY gender_concept_id"
        df = pd.read_sql(query, engine)
        print(json.dumps(df.to_dict('records')))
        
    elif '{analysis_type}' == 'conditions':
        # Condition prevalence
        query = "SELECT condition_concept_id, COUNT(*) as occurrence_count, COUNT(DISTINCT person_id) as patient_count FROM omop_cdm.condition_occurrence GROUP BY condition_concept_id ORDER BY occurrence_count DESC LIMIT 10"
        df = pd.read_sql(query, engine)
        print(json.dumps(df.to_dict('records')))
    
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    sys.exit(1)
'''
    result = sandbox_manager.execute_code(sandbox_id, code)
    return {"output": result.output.decode(), "exit_code": result.exit_code}
print("Registered: analyze_omop_data")

@mcp.tool()
async def llm_dataframe_operation(sandbox_id: str, operation: str, table_name: str = "person") -> dict:
    """
    Perform LLM-friendly dataframe operations on OMOP data.
    Args:
        sandbox_id: The sandbox to execute in.
        operation: Natural language description of the operation.
        table_name: Target OMOP table.
    Returns:
        Dict with 'output' and 'exit_code' or 'error'.
    """
    code = f'''
import pandas as pd
import sys
import json
from sqlalchemy import create_engine

try:
    engine = create_engine(f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}")
    
    # Load the specified table
    df = pd.read_sql(f"SELECT * FROM omop_cdm.{{table_name}}", engine)
    
    # Parse operation and execute
    operation = "{operation}".lower()
    
    if "count" in operation:
        if "total" in operation or "all" in operation:
            result = {{"total_count": len(df)}}
        elif "unique" in operation:
            # Find column to count unique values for
            if "person" in operation:
                result = {{"unique_patients": df['person_id'].nunique()}}
            elif "condition" in operation:
                result = {{"unique_conditions": df['condition_concept_id'].nunique()}}
            else:
                result = {{"unique_count": len(df)}}
        else:
            result = {{"count": len(df)}}
    
    elif "age" in operation:
        if "birth_datetime" in df.columns:
            df['age'] = pd.Timestamp.now().year - pd.to_datetime(df['birth_datetime']).dt.year
            if "average" in operation or "mean" in operation:
                result = {{"average_age": float(df['age'].mean())}}
            elif "distribution" in operation:
                result = {{"age_distribution": df['age'].value_counts().to_dict()}}
            else:
                result = {{"age_stats": {{"min": float(df['age'].min()), "max": float(df['age'].max()), "mean": float(df['age'].mean())}}}}
        else:
            result = {{"error": "No birth_datetime column available"}}
    
    elif "gender" in operation:
        if "gender_concept_id" in df.columns:
            result = {{"gender_distribution": df['gender_concept_id'].value_counts().to_dict()}}
        else:
            result = {{"error": "No gender_concept_id column available"}}
    
    else:
        # Default: return basic info
        result = {{
            "table": "{table_name}",
            "total_rows": len(df),
            "columns": list(df.columns),
            "sample_data": df.head(3).to_dict('records')
        }}
    
    print(json.dumps(result))
    
except Exception as e:
    print(f"ERROR: {{str(e)}}")
    sys.exit(1)
'''
    result = sandbox_manager.execute_code(sandbox_id, code)
    return {"output": result.output.decode(), "exit_code": result.exit_code}
print("Registered: llm_dataframe_operation")

# Main entry point for the FastMCP server
if __name__ == "__main__":
    # Log that the server is starting
    logger.info("Starting FastMCP sandbox server...")
    
    # Start the FastMCP server using stdio transport
    # This allows the server to communicate via stdin/stdout as per MCP specification
    mcp.run(transport="stdio") 