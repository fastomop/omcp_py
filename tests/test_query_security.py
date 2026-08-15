"""Unit tests for read-only query policy and data-minimisation controls."""

import asyncio

import pytest

from omcp_py.tools import query_tools


@pytest.mark.parametrize(
    "query",
    [
        "SELECT person_id FROM omop_cdm.person",
        "SELECT 'delete is text' AS note",
        'SELECT "update" FROM vocabulary',
        "WITH cohort AS (SELECT person_id FROM omop_cdm.person) SELECT * FROM cohort",
        "SELECT 1;",
    ],
)
def test_readonly_policy_accepts_safe_queries(query):
    assert query_tools._is_readonly_sql(query)


@pytest.mark.parametrize(
    "query",
    [
        "",
        "DELETE FROM omop_cdm.person",
        "WITH deleted AS (DELETE FROM omop_cdm.person RETURNING *) SELECT * FROM deleted",
        "SELECT * INTO copied_person FROM omop_cdm.person",
        "SELECT 1; DROP TABLE omop_cdm.person",
        "SELECT * FROM read_csv_auto('/etc/passwd')",
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT nextval('person_id_seq')",
        "SELECT 1 -- hidden statement",
        "SELECT /* hidden */ 1",
        "SELECT $$dollar quoted$$",
        "SELECT 'unterminated",
    ],
)
def test_readonly_policy_rejects_unsafe_queries(query):
    assert not query_tools._is_readonly_sql(query)


def test_query_limit_is_clamped(monkeypatch):
    monkeypatch.setattr(query_tools.config, "query_default_limit", 100)
    monkeypatch.setattr(query_tools.config, "query_max_rows", 500)

    assert query_tools._bounded_limit(-1) == 1
    assert query_tools._bounded_limit("invalid") == 100
    assert query_tools._bounded_limit(250) == 250
    assert query_tools._bounded_limit(50_000) == 500


def test_limited_query_fetches_one_extra_row():
    wrapped = query_tools._limited_query("SELECT person_id FROM omop_cdm.person", 25)

    assert wrapped.startswith("SELECT * FROM (")
    assert wrapped.endswith("LIMIT 26")


def test_audit_metadata_contains_no_query_or_patient_data():
    audit = query_tools._audit_metadata("duckdb", 100, 12, False)

    assert audit["backend"] == "duckdb"
    assert audit["row_limit"] == 100
    assert audit["rows_returned"] == 12
    assert audit["truncated"] is False
    assert "query_id" in audit
    assert "executed_at" in audit
    assert "sql" not in audit
    assert "query" not in audit
    assert "result" not in audit


def test_omop_query_rejects_invalid_identifiers_before_database_access():
    result = asyncio.run(query_tools.query_omop_table("person; DROP TABLE person"))

    assert result == {"success": False, "error": "Invalid table name"}


def test_omop_query_rejects_invalid_filter_identifier():
    result = asyncio.run(
        query_tools.query_omop_table("person", filters={"person_id OR 1=1": 1})
    )

    assert result == {
        "success": False,
        "error": "Invalid filter column: person_id OR 1=1",
    }
