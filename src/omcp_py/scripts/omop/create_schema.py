
import os
import sys
import psycopg2

def main():
    try:
        # Connect using environment variables
        conn = psycopg2.connect(
            dbname=os.environ.get("OMOP_DB_NAME", "omcp"),
            user=os.environ.get("OMOP_DB_USER", "omcp"),
            password=os.environ.get("OMOP_DB_PASSWORD", "postgres"),
            host=os.environ.get("OMOP_DB_HOST", "db"),
            port=int(os.environ.get("OMOP_DB_PORT", "5432"))
        )
        cur = conn.cursor()
        
        # Create OMOP schema
        print("Creating schema 'omop_cdm' if not exists...")
        cur.execute("CREATE SCHEMA IF NOT EXISTS omop_cdm;")
        
        # Create basic OMOP tables
        print("Creating tables...")
        
        person_sql = """
        CREATE TABLE IF NOT EXISTS omop_cdm.person (
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
        );"""
        
        visit_sql = """
        CREATE TABLE IF NOT EXISTS omop_cdm.visit_occurrence (
            visit_occurrence_id BIGINT PRIMARY KEY, 
            person_id BIGINT, 
            visit_concept_id INTEGER, 
            visit_start_datetime TIMESTAMP, 
            visit_end_datetime TIMESTAMP, 
            visit_type_concept_id INTEGER
        );"""
        
        condition_sql = """
        CREATE TABLE IF NOT EXISTS omop_cdm.condition_occurrence (
            condition_occurrence_id BIGINT PRIMARY KEY, 
            person_id BIGINT, 
            condition_concept_id INTEGER, 
            condition_start_datetime TIMESTAMP, 
            condition_end_datetime TIMESTAMP, 
            condition_type_concept_id INTEGER
        );"""
        
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

if __name__ == "__main__":
    main()
