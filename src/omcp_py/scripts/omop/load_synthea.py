
import pandas as pd
import os
import sys
from sqlalchemy import create_engine

def main():
    try:
        # Get config from env
        db_name = os.environ.get("OMOP_DB_NAME", "omcp")
        db_user = os.environ.get("OMOP_DB_USER", "omcp")
        db_password = os.environ.get("OMOP_DB_PASSWORD", "postgres")
        db_host = os.environ.get("OMOP_DB_HOST", "db")
        db_port = os.environ.get("OMOP_DB_PORT", "5432")
        
        csv_directory = os.environ.get("CSV_DIRECTORY", "synthetic_data")

        # Connect to PostgreSQL
        url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(url)
        
        # Define Synthea to OMOP mappings
        synthea_mappings = {
            'patients.csv': {
                'table': 'omop_cdm.person',
                'columns': {
                    'Id': 'person_id',
                    'BIRTHDATE': 'birth_datetime',
                    'DEATHDATE': 'death_datetime',
                    'GENDER': 'gender_concept_id',
                    'RACE': 'race_concept_id',
                    'ETHNICITY': 'ethnicity_concept_id'
                }
            },
            'encounters.csv': {
                'table': 'omop_cdm.visit_occurrence',
                'columns': {
                    'Id': 'visit_occurrence_id',
                    'START': 'visit_start_datetime',
                    'STOP': 'visit_end_datetime',
                    'PATIENT': 'person_id',
                    'ENCOUNTERCLASS': 'visit_concept_id'
                }
            },
            'conditions.csv': {
                'table': 'omop_cdm.condition_occurrence',
                'columns': {
                    'START': 'condition_start_datetime',
                    'STOP': 'condition_end_datetime',
                    'PATIENT': 'person_id',
                    'CODE': 'condition_concept_id'
                }
            }
        }
        
        # Process each CSV file
        for filename, mapping in synthea_mappings.items():
            filepath = os.path.join(csv_directory, filename)
            if os.path.exists(filepath):
                print(f"Processing {filename}...")
                
                # Read CSV
                df = pd.read_csv(filepath)
                
                # Rename columns according to mapping
                df = df.rename(columns=mapping['columns'])
                
                # Add required OMOP columns with defaults
                if mapping['table'] == 'omop_cdm.person':
                    df['person_source_value'] = df['person_id'].astype(str)
                    df['gender_source_value'] = df['gender_concept_id']
                
                # Load to PostgreSQL
                table_name = mapping['table'].split('.')[-1]
                df.to_sql(table_name, engine, schema='omop_cdm', if_exists='append', index=False, method='multi')
                print(f"Loaded {len(df)} rows into {mapping['table']}")
            else:
                print(f"File not found: {filepath}")
        
        print("Synthea data loading completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
