"""Read-only, data-minimising query tools for OMOP CDM data stores."""

from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import duckdb
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from omcp_py.core.db import get_engine
from omcp_py.core.globals import config

logger = logging.getLogger(__name__)

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_DISALLOWED_SQL_RE = re.compile(
    r"\b(?:alter|attach|call|comment|copy|create|delete|detach|drop|execute|"
    r"export|grant|import|insert|install|load|merge|pragma|reindex|reset|"
    r"revoke|set|truncate|update|vacuum)\b",
    re.IGNORECASE,
)
_RISKY_FUNCTION_RE = re.compile(
    r"\b(?:dblink|glob|http_get|http_post|lo_import|nextval|pg_advisory_lock|"
    r"pg_ls_dir|pg_read_binary_file|pg_read_file|pg_terminate_backend|"
    r"postgres_scan|read_blob|read_csv|read_csv_auto|read_json|read_ndjson|"
    r"read_parquet|setval|sqlite_scan)\s*\(",
    re.IGNORECASE,
)


def _resolve_duckdb_path(default: Optional[str] = None) -> Optional[str]:
    """Resolve a DuckDB path from the environment or a fallback default."""
    env_path = os.getenv("DB_PATH")
    return str(Path(env_path).expanduser()) if env_path else default


def _normalise_readonly_sql(sql: str) -> Optional[str]:
    """Return a normalised single read-only query, or ``None`` when unsafe.

    This is a defence-in-depth parser, not a replacement for a least-privilege
    database role. It rejects comments, multiple statements, data-modifying CTEs,
    filesystem/network table functions, and state-changing functions.
    """
    if not isinstance(sql, str) or not sql.strip():
        return None

    query = sql.strip()
    if query.endswith(";"):
        query = query[:-1].rstrip()
    if not query or ";" in query or "--" in query or "/*" in query or "*/" in query:
        return None

    # Remove quoted literals and identifiers before keyword/function checks so
    # harmless words inside values do not cause false positives. Unterminated
    # quotes and PostgreSQL dollar-quoted strings are rejected conservatively.
    scrubbed: List[str] = []
    index = 0
    while index < len(query):
        char = query[index]
        if char == "$":
            return None
        if char not in ("'", '"'):
            scrubbed.append(char)
            index += 1
            continue

        quote = char
        scrubbed.append(" ")
        index += 1
        closed = False
        while index < len(query):
            current = query[index]
            if current == quote:
                if index + 1 < len(query) and query[index + 1] == quote:
                    index += 2
                    continue
                closed = True
                index += 1
                break
            if current == "\\" and quote == "'":
                index += 2
            else:
                index += 1
        if not closed:
            return None

    candidate = "".join(scrubbed).strip()
    if not re.match(r"^(?:select|with)\b", candidate, re.IGNORECASE):
        return None
    if re.search(r"\bselect\b[\s\S]*\binto\b", candidate, re.IGNORECASE):
        return None
    if _DISALLOWED_SQL_RE.search(candidate) or _RISKY_FUNCTION_RE.search(candidate):
        return None
    return query


def _is_readonly_sql(sql: str) -> bool:
    """Return whether SQL passes the read-only defence-in-depth policy."""
    return _normalise_readonly_sql(sql) is not None


def _bounded_limit(requested: int) -> int:
    """Clamp a requested row limit to the configured data-minimisation cap."""
    try:
        value = int(requested)
    except (TypeError, ValueError):
        value = config.query_default_limit
    return min(max(1, value), config.query_max_rows)


def _limited_query(sql: str, limit: int) -> str:
    """Wrap a validated query and fetch one extra row to detect truncation."""
    return f"SELECT * FROM ({sql}) AS omcp_readonly_query LIMIT {limit + 1}"


def _audit_metadata(
    backend: str, row_limit: int, returned: int, truncated: bool
) -> Dict[str, Any]:
    """Create metadata suitable for audit logs without recording SQL or PHI."""
    return {
        "query_id": uuid4().hex,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "backend": backend,
        "row_limit": row_limit,
        "rows_returned": returned,
        "truncated": truncated,
    }


def _connect_duckdb(path: str):
    """Open DuckDB read-only and disable external filesystem/network access."""
    options: Dict[str, Any] = {"config": {"enable_external_access": "false"}}
    if path != ":memory:":
        options["read_only"] = True
    return duckdb.connect(path, **options)


def _duckdb_query(sql: str, path: str, limit: int) -> Dict[str, Any]:
    with _connect_duckdb(path) as connection:
        cursor = connection.execute(_limited_query(sql, limit))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
    truncated = len(rows) > limit
    rows = rows[:limit]
    return {
        "success": True,
        "columns": columns,
        "result": rows,
        "audit": _audit_metadata("duckdb", limit, len(rows), truncated),
    }


async def query_duckdb(sql: str, max_rows: int = 1000) -> Dict[str, Any]:
    """Execute one bounded, read-only query against the configured DuckDB file."""
    query = _normalise_readonly_sql(sql)
    if query is None:
        return {
            "success": False,
            "error": "Query rejected by the read-only SQL policy.",
        }

    path = _resolve_duckdb_path(default="synthetic_data/synthea.duckdb")
    if path is None or (path != ":memory:" and not Path(path).is_file()):
        return {"success": False, "error": f"DuckDB file not found at {path}"}

    try:
        return await asyncio.to_thread(
            _duckdb_query, query, path, _bounded_limit(max_rows)
        )
    except (duckdb.Error, OSError, RuntimeError, TypeError, ValueError) as error:
        logger.warning("DuckDB query failed", exc_info=config.debug)
        return {"success": False, "error": str(error)}


def _is_valid_identifier(value: str) -> bool:
    return isinstance(value, str) and bool(_IDENTIFIER_RE.fullmatch(value))


def _query_omop_table_sync(
    table_name: str,
    limit: int,
    columns: Optional[List[str]],
    filters: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    selected = ", ".join(columns) if columns else "*"
    statement = f"SELECT {selected} FROM omop_cdm.{table_name}"
    params: Dict[str, Any] = {"row_limit": limit + 1}

    if filters:
        clauses = []
        for index, (key, value) in enumerate(filters.items()):
            parameter = f"filter_{index}"
            clauses.append(f"{key} = :{parameter}")
            params[parameter] = value
        statement += " WHERE " + " AND ".join(clauses)
    statement += " LIMIT :row_limit"

    with get_engine().connect() as connection:
        rows = [
            dict(row._mapping) for row in connection.execute(text(statement), params)
        ]
    truncated = len(rows) > limit
    rows = rows[:limit]
    return {
        "success": True,
        "count": len(rows),
        "data": rows,
        "audit": _audit_metadata("postgresql", limit, len(rows), truncated),
    }


async def query_omop_table(
    table_name: str,
    limit: int = 100,
    columns: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Safely query one OMOP CDM table with parameterised equality filters.

    Identifiers are restricted to simple SQL names, values are bound parameters,
    the schema is fixed to ``omop_cdm``, and returned rows are strictly capped.
    """
    if not _is_valid_identifier(table_name):
        return {"success": False, "error": "Invalid table name"}
    if columns:
        invalid = next(
            (column for column in columns if not _is_valid_identifier(column)), None
        )
        if invalid:
            return {"success": False, "error": f"Invalid column name: {invalid}"}
    if filters:
        invalid = next((key for key in filters if not _is_valid_identifier(key)), None)
        if invalid:
            return {"success": False, "error": f"Invalid filter column: {invalid}"}

    try:
        return await asyncio.to_thread(
            _query_omop_table_sync,
            table_name,
            _bounded_limit(limit),
            columns,
            filters,
        )
    except (SQLAlchemyError, OSError, RuntimeError, TypeError, ValueError) as error:
        logger.warning("OMOP table query failed", exc_info=config.debug)
        return {"success": False, "error": str(error)}


def _information_schema_sync(path: Optional[str]) -> Dict[str, Any]:
    statement = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_schema, table_name
    """
    if path:
        with _connect_duckdb(path) as connection:
            cursor = connection.execute(statement)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
        backend = "duckdb"
    else:
        with get_engine().connect() as connection:
            result = connection.execute(text(statement))
            rows = result.fetchall()
            columns = list(result.keys())
        backend = "postgresql"
    return {
        "success": True,
        "columns": columns,
        "result": rows,
        "audit": _audit_metadata(backend, len(rows), len(rows), False),
    }


async def Get_information_Schema() -> Dict[str, Any]:
    """Return available database schemas and tables without exposing row data."""
    path = _resolve_duckdb_path()
    if path and path != ":memory:" and not Path(path).is_file():
        return {"success": False, "error": f"DuckDB file not found at {path}"}
    try:
        return await asyncio.to_thread(_information_schema_sync, path)
    except (duckdb.Error, SQLAlchemyError, OSError, RuntimeError, ValueError) as error:
        logger.warning("Information schema query failed", exc_info=config.debug)
        return {"success": False, "error": str(error)}


def _postgres_query(sql: str, limit: int) -> Dict[str, Any]:
    with get_engine().connect() as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            result = connection.execute(text(_limited_query(sql, limit)))
            rows = result.fetchall()
            columns = list(result.keys())
    truncated = len(rows) > limit
    rows = rows[:limit]
    return {
        "success": True,
        "columns": columns,
        "result": rows,
        "audit": _audit_metadata("postgresql", limit, len(rows), truncated),
    }


async def Select_Query(query: str, max_rows: int = 1000) -> Dict[str, Any]:
    """Execute one bounded query under the read-only SQL policy."""
    sql = _normalise_readonly_sql(query)
    if sql is None:
        return {
            "success": False,
            "error": "Query rejected by the read-only SQL policy.",
        }

    path = _resolve_duckdb_path()
    if path and path != ":memory:" and not Path(path).is_file():
        return {"success": False, "error": f"DuckDB file not found at {path}"}

    limit = _bounded_limit(max_rows)
    try:
        if path:
            return await asyncio.to_thread(_duckdb_query, sql, path, limit)
        return await asyncio.to_thread(_postgres_query, sql, limit)
    except (
        duckdb.Error,
        SQLAlchemyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        logger.warning("Read-only query failed", exc_info=config.debug)
        return {"success": False, "error": str(error)}


def register(mcp):
    """Register query tools with the MCP instance."""
    mcp.tool()(query_duckdb)
    mcp.tool()(query_omop_table)
    mcp.tool()(Get_information_Schema)
    mcp.tool()(Select_Query)
