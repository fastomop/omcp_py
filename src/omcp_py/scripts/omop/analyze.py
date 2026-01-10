
import pandas as pd
import sys
import json
import os
from sqlalchemy import create_engine

def main():
    try:
        # Get config from env
        db_name = os.environ.get("OMOP_DB_NAME", "omcp")
        db_user = os.environ.get("OMOP_DB_USER", "omcp")
        db_password = os.environ.get("OMOP_DB_PASSWORD", "postgres")
        db_host = os.environ.get("OMOP_DB_HOST", "db")
        db_port = os.environ.get("OMOP_DB_PORT", "5432")
        
        analysis_type = os.environ.get("ANALYSIS_TYPE", "basic")
        
        url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(url)
        
        if analysis_type == 'basic':
            # Basic counts
            queries = {
                'total_patients': 'SELECT COUNT(*) as count FROM omop_cdm.person',
                'total_visits': 'SELECT COUNT(*) as count FROM omop_cdm.visit_occurrence',
                'total_conditions': 'SELECT COUNT(*) as count FROM omop_cdm.condition_occurrence'
            }
            
            results = {}
            for name, query in queries.items():
                df = pd.read_sql(query, engine)
                results[name] = int(df['count'].iloc[0])
            
            print(json.dumps(results))
            
        elif analysis_type == 'demographics':
            # Demographics analysis
            query = "SELECT gender_concept_id, COUNT(*) as patient_count, AVG(EXTRACT(YEAR FROM AGE(birth_datetime))) as avg_age FROM omop_cdm.person WHERE birth_datetime IS NOT NULL GROUP BY gender_concept_id"
            df = pd.read_sql(query, engine)
            print(json.dumps(df.to_dict('records')))
            
        elif analysis_type == 'conditions':
            # Condition prevalence
            query = "SELECT condition_concept_id, COUNT(*) as occurrence_count, COUNT(DISTINCT person_id) as patient_count FROM omop_cdm.condition_occurrence GROUP BY condition_concept_id ORDER BY occurrence_count DESC LIMIT 10"
            df = pd.read_sql(query, engine)
            print(json.dumps(df.to_dict('records')))
        else:
            print(json.dumps({"error": f"Unknown analysis type: {analysis_type}"}))
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
