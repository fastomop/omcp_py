#!/usr/bin/env python3
"""
Bootstrap script to create OMOP schema and load Synthea CSV files into Postgres.
Usage: python scripts/bootstrap_synthea.py
"""
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from omcp_py.config import get_config
import duckdb

CSV_MAPPINGS = {
    "patients.csv": {
        "table": "person",
        "schema": "omop_cdm",
        "columns": {
            "Id": "person_id",
            "BIRTHDATE": "birth_datetime",
            "DEATHDATE": "death_datetime",
            "GENDER": "gender_concept_id",
            "RACE": "race_concept_id",
            "ETHNICITY": "ethnicity_concept_id",
        },
    },
    "encounters.csv": {
        "table": "visit_occurrence",
        "schema": "omop_cdm",
        "columns": {
            "Id": "visit_occurrence_id",
            "START": "visit_start_datetime",
            "STOP": "visit_end_datetime",
            "PATIENT": "person_id",
            "ENCOUNTERCLASS": "visit_concept_id",
        },
    },
    "conditions.csv": {
        "table": "condition_occurrence",
        "schema": "omop_cdm",
        "columns": {
            "START": "condition_start_datetime",
            "STOP": "condition_end_datetime",
            "PATIENT": "person_id",
            "CODE": "condition_concept_id",
        },
    },
}


def ensure_schema_and_tables(engine):
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS omop_cdm;"))
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS omop_cdm.person (person_id BIGINT PRIMARY KEY, gender_concept_id INTEGER, year_of_birth INTEGER, month_of_birth INTEGER, day_of_birth INTEGER, birth_datetime TIMESTAMP, death_datetime TIMESTAMP, race_concept_id INTEGER, ethnicity_concept_id INTEGER, person_source_value VARCHAR(50), gender_source_value VARCHAR(50));"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS omop_cdm.visit_occurrence (visit_occurrence_id BIGINT PRIMARY KEY, person_id BIGINT, visit_concept_id INTEGER, visit_start_datetime TIMESTAMP, visit_end_datetime TIMESTAMP, visit_type_concept_id INTEGER);"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS omop_cdm.condition_occurrence (condition_occurrence_id BIGINT PRIMARY KEY, person_id BIGINT, condition_concept_id INTEGER, condition_start_datetime TIMESTAMP, condition_end_datetime TIMESTAMP, condition_type_concept_id INTEGER);"
            )
        )
    print("Schema and base tables ensured.")


def load_csvs(engine, data_dir: Path, chunk_size: int):
    for fname, meta in CSV_MAPPINGS.items():
        path = data_dir / fname
        if not path.exists():
            print(f"Skipping {fname}: not found")
            continue
        print(f"Loading {fname} -> {meta['schema']}.{meta['table']}")
        df = pd.read_csv(path)
        # rename columns we know about
        df = df.rename(columns=meta["columns"])
        # add simple defaults where required
        if meta["table"] == "person":
            if "person_id" in df.columns:
                df["person_source_value"] = df["person_id"].astype(str)
            if "gender_concept_id" in df.columns:
                df["gender_source_value"] = df["gender_concept_id"]
        # write to sql
        df.to_sql(
            meta["table"],
            engine,
            schema=meta["schema"],
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunk_size,
        )
        print(f"Loaded {len(df)} rows into {meta['schema']}.{meta['table']}")


def load_from_duckdb(engine, duckdb_path: Path, chunk_size: int):
    """Load tables from a DuckDB file if available."""
    con = duckdb.connect(database=str(duckdb_path), read_only=True)
    try:
        tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
        print("DuckDB tables:", tables)

        for fname, meta in CSV_MAPPINGS.items():
            tbl = Path(fname).stem
            if tbl not in tables:
                print(f"Skipping DuckDB table {tbl}: not found")
                continue
            print(f"Loading DuckDB table {tbl} -> {meta['schema']}.{meta['table']}")
            df = con.execute(f"SELECT * FROM {tbl}").df()

            df = df.rename(columns=meta["columns"])

            if meta["table"] == "person":
                if "person_id" in df.columns:
                    df["person_source_value"] = df["person_id"].astype(str)
                if "gender_concept_id" in df.columns:
                    df["gender_source_value"] = df["gender_concept_id"]

            df.to_sql(
                meta["table"],
                engine,
                schema=meta["schema"],
                if_exists="append",
                index=False,
                method="multi",
                chunksize=chunk_size,
            )
            print(
                f"Loaded {len(df)} rows from DuckDB table {tbl} into {meta['schema']}.{meta['table']}"
            )
    finally:
        con.close()


if __name__ == "__main__":
    cfg = get_config()
    url = f"postgresql://{cfg.db_user}:{cfg.db_password}@{cfg.db_host}:{cfg.db_port}/{cfg.db_name}"
    engine = create_engine(url)

    data_dir = Path("synthetic_data")
    chunk_size = int(os.environ.get("OMOP_LOAD_CHUNKSIZE", "5000"))
    ensure_schema_and_tables(engine)
    # Prefer loading from DuckDB snapshot if present, otherwise CSVs
    duckdb_file = data_dir / "synthea.duckdb"
    if duckdb_file.exists():
        print("Found duckdb snapshot, loading from synthea.duckdb")
        load_from_duckdb(engine, duckdb_file, chunk_size)
    else:
        load_csvs(engine, data_dir, chunk_size)
    print("Bootstrap complete")
