
import logging
import re
import duckdb
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
        with duckdb.connect('synthetic_data/synthea.duckdb') as con:
            result = con.execute(sql).fetchall()
            columns = [desc[0] for desc in con.description]
        return {"success": True, "columns": columns, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _is_valid_identifier(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value))

async def query_omop_table(
    table_name: str,
    limit: int = 100,
    columns: Optional[List[str]] = None,
    where: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Directly query an OMOP table without sandbox overhead (Fast Path).
    
    This tool runs directly on the server, bypassing the Docker container creation
    process. It is significantly faster for read-only data retrieval.
    
    Args:
        table_name: Name of the OMOP table (e.g., 'person', 'visit_occurrence')
        limit: Maximum number of rows to return (default: 100, max: 1000)
        columns: List of columns to select (default: all)
        where: Optional raw SQL WHERE clause (disabled by default)
        filters: Optional column/value filters (equality only)
    """
    try:
        # Security check: simple table name validation
        if not _is_valid_identifier(table_name):
            return {"success": False, "error": "Invalid table name"}
            
        engine = get_engine()
        
        # Construct query
        if columns:
            for col in columns:
                if not _is_valid_identifier(col):
                    return {"success": False, "error": f"Invalid column name: {col}"}
            cols = ", ".join(columns)
        else:
            cols = "*"
        query_str = f"SELECT {cols} FROM omop_cdm.{table_name}"

        params: Dict[str, Any] = {}
        has_where = False
        if filters:
            clauses = []
            for idx, (key, value) in enumerate(filters.items()):
                if not _is_valid_identifier(key):
                    return {"success": False, "error": f"Invalid filter column: {key}"}
                param_key = f"p_{idx}"
                clauses.append(f"{key} = :{param_key}")
                params[param_key] = value
            if clauses:
                query_str += " WHERE " + " AND ".join(clauses)
                has_where = True

        if where:
            if not getattr(config, "allow_unsafe_sql", False):
                return {"success": False, "error": "Raw WHERE clause is disabled. Use filters instead or set ALLOW_UNSAFE_SQL=true."}
            # Basic SQL injection check - still unsafe, but blocks obvious multi-statement injection
            if ";" in where or "--" in where or "/*" in where:
                return {"success": False, "error": "Invalid WHERE clause"}
            query_str += f" {'AND' if has_where else 'WHERE'} {where}"
            
        # Hard cap on limit
        safe_limit = min(max(1, limit), 1000)
        query_str += f" LIMIT {safe_limit}"
        
        with engine.connect() as conn:
            result = conn.execute(text(query_str), params)
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
