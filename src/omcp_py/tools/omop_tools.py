
import logging
import re
from pathlib import Path
from omcp_py.core.globals import sandbox_manager, config

logger = logging.getLogger(__name__)

def _get_script_content(script_name: str) -> str:
    """Load script content."""
    # Find the script path relative to this module
    # src/omcp_py/tools/omop_tools.py -> src/omcp_py/scripts/omop/{script_name}
    script_path = Path(__file__).parent.parent / "scripts" / "omop" / script_name
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script {script_name} not found at {script_path}")
        
    return script_path.read_text()

def _db_env() -> dict:
    return {
        "OMOP_DB_NAME": config.db_name,
        "OMOP_DB_USER": config.db_user,
        "OMOP_DB_PASSWORD": config.db_password,
        "OMOP_DB_HOST": config.db_host,
        "OMOP_DB_PORT": str(config.db_port),
    }

def _validate_table_name(table_name: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name))

async def create_omop_schema(sandbox_id: str) -> dict:
    """
    Create OMOP CDM schema in PostgreSQL database from within the sandbox.
    Args:
        sandbox_id: The sandbox to execute in.
    Returns:
        Dict with 'output' and 'exit_code' or 'error'.
    """
    try:
        code = _get_script_content("create_schema.py")
        result = sandbox_manager.execute_code(sandbox_id, code, env=_db_env())
        return {
            "success": result.get("exit_code") == 0,
            "output": result.get("output", ""),
            "exit_code": result.get("exit_code"),
            "error": result.get("error")
        }
    except Exception as e:
        logger.error(f"Failed to create OMOP schema: {e}")
        return {"success": False, "error": str(e)}

async def load_synthea_to_postgres(sandbox_id: str, csv_directory: str = "synthetic_data") -> dict:
    """
    Load Synthea CSV files into PostgreSQL OMOP database from within the sandbox.
    Args:
        sandbox_id: The sandbox to execute in.
        csv_directory: Directory containing Synthea CSV files.
    """
    try:
        base_code = _get_script_content("load_synthea.py")
        env = _db_env()
        env["CSV_DIRECTORY"] = csv_directory
        result = sandbox_manager.execute_code(sandbox_id, base_code, env=env)
        return {
            "success": result.get("exit_code") == 0,
            "output": result.get("output", ""),
            "exit_code": result.get("exit_code"),
            "error": result.get("error")
        }
    except Exception as e:
        logger.error(f"Failed to load Synthea data: {e}")
        return {"success": False, "error": str(e)}

async def analyze_omop_data(sandbox_id: str, analysis_type: str = "basic") -> dict:
    """
    Perform analytics on OMOP data using pandas and LLM-friendly output.
    Args:
        sandbox_id: The sandbox to execute in.
        analysis_type: Type of analysis ('basic', 'demographics', 'conditions').
    """
    try:
        base_code = _get_script_content("analyze.py")
        env = _db_env()
        env["ANALYSIS_TYPE"] = analysis_type
        result = sandbox_manager.execute_code(sandbox_id, base_code, env=env)
        return {
            "success": result.get("exit_code") == 0,
            "output": result.get("output", ""),
            "exit_code": result.get("exit_code"),
            "error": result.get("error")
        }
    except Exception as e:
        logger.error(f"Failed to analyze OMOP data: {e}")
        return {"success": False, "error": str(e)}

async def llm_dataframe_operation(sandbox_id: str, operation: str, table_name: str = "person") -> dict:
    """
    Perform LLM-friendly dataframe operations on OMOP data.
    Args:
        sandbox_id: The sandbox to execute in.
        operation: Natural language description of the operation.
        table_name: Target OMOP table.
    """
    # This one still uses dynamic code generation so we keep it inline or move to a generalized script
    # For now, keeping inline to match current behavior but modularized
    # Actually, let's keep it inline for now as it's very dynamic
    if not _validate_table_name(table_name):
        return {"success": False, "error": "Invalid table name"}

    code = '''
import pandas as pd
import sys
import json
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(f"postgresql://{os.environ['OMOP_DB_USER']}:{os.environ['OMOP_DB_PASSWORD']}@{os.environ['OMOP_DB_HOST']}:{os.environ['OMOP_DB_PORT']}/{os.environ['OMOP_DB_NAME']}")
    table_name = os.environ.get("OMOP_TABLE_NAME", "person")
    df = pd.read_sql(f"SELECT * FROM omop_cdm.{table_name}", engine)
    operation = os.environ.get("LLM_OPERATION", "").lower()
    
    result = {{}}
    if "count" in operation:
        if "total" in operation or "all" in operation:
            result = {{"total_count": len(df)}}
        elif "unique" in operation:
            if "person" in operation:
                result = {{"unique_patients": df['person_id'].nunique()}} if 'person_id' in df else {{"unique_count": len(df)}}
            else:
                result = {{"unique_count": len(df)}}
        else:
            result = {{"count": len(df)}}
    else:
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
    env = _db_env()
    env["OMOP_TABLE_NAME"] = table_name
    env["LLM_OPERATION"] = operation
    result = sandbox_manager.execute_code(sandbox_id, code, env=env)
    return {
        "success": result.get("exit_code") == 0,
        "output": result.get("output", ""),
        "exit_code": result.get("exit_code"),
        "error": result.get("error")
    }

def register(mcp):
    """Register all OMOP tools with the MCP instance."""
    mcp.tool()(create_omop_schema)
    mcp.tool()(load_synthea_to_postgres)
    mcp.tool()(analyze_omop_data)
    mcp.tool()(llm_dataframe_operation)
