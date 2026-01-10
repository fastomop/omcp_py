
import logging
import duckdb
import pandas as pd
from typing import Optional, List, Any, Dict
from sqlalchemy import text
from omcp_py.core.globals import config
from omcp_py.core.db import get_engine

logger = logging.getLogger(__name__)

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

async def query_omop_table(
    table_name: str,
    limit: int = 100,
    columns: Optional[List[str]] = None,
    where: Optional[str] = None
) -> Dict[str, Any]:
    """
    Directly query an OMOP table without sandbox overhead (Fast Path).
    
    This tool runs directly on the server, bypassing the Docker container creation
    process. It is significantly faster for read-only data retrieval.
    
    Args:
        table_name: Name of the OMOP table (e.g., 'person', 'visit_occurrence')
        limit: Maximum number of rows to return (default: 100, max: 1000)
        columns: List of columns to select (default: all)
        where: Optional SQL WHERE clause (safe parameterization not guaranteed here, be careful)
    """
    try:
        # Security check: simple table name validation
        if not table_name.replace('_', '').isalnum():
            return {"success": False, "error": "Invalid table name"}
            
        engine = get_engine()
        
        # Construct query
        cols = ", ".join(columns) if columns else "*"
        query_str = f"SELECT {cols} FROM omop_cdm.{table_name}"
        
        if where:
            # Basic SQL injection check - this is a simple implementation
            if ";" in where or "--" in where:
                return {"success": False, "error": "Invalid WHERE clause"}
            query_str += f" WHERE {where}"
            
        # Hard cap on limit
        safe_limit = min(max(1, limit), 1000)
        query_str += f" LIMIT {safe_limit}"
        
        with engine.connect() as conn:
            result = conn.execute(text(query_str))
            data = [dict(row._mapping) for row in result]
            
        return {
            "success": True,
            "count": len(data),
            "data": data
        }
    except Exception as e:
        logger.error(f"Failed to query OMOP table: {e}")
        return {"success": False, "error": str(e)}

def register(mcp):
    """Register query tools with the MCP instance."""
    mcp.tool()(query_duckdb)
    mcp.tool()(query_omop_table)
