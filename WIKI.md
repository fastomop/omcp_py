# OMCP Python Sandbox - Complete Wiki

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
5. [Quick Start](#quick-start)
6. [Usage Guide](#usage-guide)
7. [API Reference](#api-reference)
8. [Security](#security)
9. [Development](#development)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [Contributing](#contributing)
13. [FAQ](#faq)
14. [OMOP CDM Integration](#omop-cdm-integration)

---

## Overview

The OMCP Python Sandbox is a secure, Model Context Protocol (MCP) compliant Python code execution environment that provides isolated, containerized Python environments for safe code execution. Built with enterprise-grade security features, it enables AI agents and applications to execute Python code without compromising system security.

### Key Benefits
- **🔒 Enterprise Security**: Docker-based isolation with comprehensive security measures
- **🚀 MCP Compliance**: Full Model Context Protocol specification compliance
- **⚡ Fast Execution**: Optimized for performance with resource management
- **🛠️ Developer Friendly**: Simplified structure with single entry point
- **📊 Production Ready**: Robust error handling, logging, and monitoring
- **🏥 Healthcare Ready**: OMOP CDM integration for clinical data analysis

### Use Cases
- **AI Agent Code Execution**: Safe Python code execution for AI assistants
- **OMOP CDM Analysis**: Clinical data analysis and research
- **Educational Platforms**: Isolated coding environments for learning
- **Code Testing**: Secure testing environments for untrusted code
- **API Services**: Python execution as a service
- **Development Tools**: Local development with sandboxed execution

---

## Architecture

### System Overview
```
┌─────────────────┐    JSON-RPC    ┌──────────────────┐    Docker API    ┌─────────────────┐
│   MCP Client    │ ──────────────▶ │  FastMCP Server  │ ────────────────▶ │ Docker Engine   │
│   (Agent/App)   │                │ (src/omcp_py/)   │                  │                 │
└─────────────────┘                └──────────────────┘                  └─────────────────┘
         │                                   │                                     │
         │                                   │                                     │
         ▼                                   ▼                                     ▼
┌─────────────────┐                ┌──────────────────┐                ┌─────────────────┐
│   MCP Inspector │                │ Sandbox Manager  │                │ Python Sandbox  │
│   (Web UI)      │                │ (sandbox_manager)│                │ (Container)     │
└─────────────────┘                └──────────────────┘                └─────────────────┘
```

### Component Details

#### 1. MCP Client Layer
- **Purpose**: External applications or AI agents that need to execute Python code
- **Protocol**: JSON-RPC over stdio (MCP specification)
- **Tools**: create_sandbox, execute_python_code, install_package, list_sandboxes, remove_sandbox

#### 2. FastMCP Server Layer
- **Implementation**: `src/omcp_py/main.py`
- **Framework**: FastMCP with decorator-based tool definitions
- **Features**: Enhanced security, timeout handling, structured logging
- **Transport**: stdio (MCP standard)

#### 3. Sandbox Manager Layer
- **Location**: `src/omcp_py/sandbox_manager.py`
- **Responsibilities**: 
  - Docker container lifecycle management
  - Resource allocation and cleanup
  - Security policy enforcement
  - Error handling and recovery

#### 4. Docker Container Layer
- **Base Image**: `python:3.11-slim`
- **Security**: Enhanced Docker security options
- **Isolation**: Complete network and filesystem isolation
- **Resources**: CPU and memory limits

## Database Integration and OMOP CDM Roadmap

### Current State
- Sandbox metadata is now persisted in a PostgreSQL database using SQLAlchemy, ensuring robust tracking and management of sandboxes across server restarts.

### Future Direction: OMOP CDM Integration
- The project aims to enable sandboxed Python code to securely connect to and query OMOP Common Data Model (CDM) data stored in PostgreSQL.
- This will support clinical data science, analytics, and AI agents running code against OMOP CDM in a secure, auditable environment.
- Planned features include:
  - Secure credential injection for sandboxes to access OMOP CDM tables
  - Example tools and code snippets for querying OMOP CDM (e.g., patient counts, cohort definitions)
  - Fine-grained access controls and auditing for database queries
  - Documentation and best practices for OMOP CDM analytics in the sandbox

For more details and to contribute to this direction, see the Contributing section below.

---

## Features

### Core Functionality

#### Sandbox Management
- **Create Sandboxes**: Instantiate isolated Python environments
- **List Sandboxes**: Monitor active sandboxes with status information
- **Remove Sandboxes**: Clean up sandboxes with force options
- **Auto-cleanup**: Automatic removal of inactive sandboxes

#### Code Execution
- **Python Code Execution**: Run arbitrary Python code in isolated containers
- **Package Installation**: Install Python packages using pip
- **Output Capture**: Capture stdout, stderr, and exit codes
- **JSON Output**: Automatic JSON parsing for structured data return

#### Security Features
- **Container Isolation**: Each sandbox runs in a separate Docker container
- **User Isolation**: Containers run as non-root user (UID 1000)
- **Read-only Filesystem**: Prevents file system modifications
- **Dropped Capabilities**: Removes all Linux capabilities
- **No Privilege Escalation**: Prevents privilege escalation attacks
- **Command Injection Protection**: Proper command escaping with `shlex.quote`
- **Resource Limits**: CPU, memory, and execution time limits
- **Network Isolation**: Complete network isolation (`network_mode="none"`)
- **Timeout Controls**: Configurable execution timeouts
- **Input Validation**: Comprehensive input sanitization

### Development Tools

#### MCP Inspector Integration
- **Web-based Interface**: Interactive tool testing at `http://127.0.0.1:6274`
- **Real-time Testing**: Test all MCP tools with live feedback
- **Request/Response Inspection**: View JSON-RPC messages
- **Error Debugging**: Detailed error messages and stack traces
- **Performance Monitoring**: Track execution times and resource usage
- **Session Persistence**: Save and load test scenarios

---

## Installation

### Prerequisites

#### System Requirements
- **Operating System**: Linux, macOS, or Windows (with Docker support)
- **Python**: 3.10 or higher
- **Docker**: Latest stable version with sudo access
- **Node.js**: 18.0.0 or higher (for MCP Inspector)

#### Package Managers
- **uv**: Modern Python package manager (recommended)
- **pip**: Traditional Python package manager (alternative)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py
```

#### 2. Install Python Dependencies
```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

#### 3. Install Node.js (for MCP Inspector)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm

# macOS
brew install node

# Windows
# Download from https://nodejs.org/
```

#### 4. Verify Installation
```bash
# Check Python dependencies
python -c "import omcp_py; print('Package installed successfully')"

# Check Node.js
node --version  # Should be 18.0.0 or higher

# Check Docker
docker ps  # Should show Docker is running
```

### Environment Configuration

#### Optional Environment Variables
Create a `.env` file in the project root:
```env
# Sandbox Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=10
DOCKER_IMAGE=python:3.11-slim

# Logging
DEBUG=false
LOG_LEVEL=INFO

# Security
```

---

## Quick Start

### 1. Start the Server
```bash
python src/omcp_py/main.py
```

### 2. Launch MCP Inspector (Optional)
```bash
npx @modelcontextprotocol/inspector python src/omcp_py/main.py
```

### 3. Test Basic Functionality
```python
# Create a sandbox
result = await mcp.create_sandbox()
sandbox_id = result["sandbox_id"]

# Execute code
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="print('Hello, World!')"
)

# Install a package
result = await mcp.install_package(
    sandbox_id=sandbox_id,
    package="numpy"
)
```

---

## OMOP CDM Integration

### Overview

The OMCP Python Sandbox is specifically designed to support OMOP Common Data Model (CDM) analysis workflows through MCP agents. This integration enables secure, isolated execution of clinical data analysis code while maintaining compliance with healthcare data security standards.

### OMOP CDM Use Cases

#### 1. Clinical Research Analysis
**Use Case**: Researchers need to analyze patient data for clinical studies
```python
# Example: Cohort analysis for diabetes patients
code = """
import pandas as pd
import numpy as np

# Connect to OMOP CDM database
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host:port/omop_cdm')

# Define diabetes cohort
diabetes_query = '''
SELECT person_id, observation_period_start_date, observation_period_end_date
FROM observation_period op
JOIN condition_occurrence co ON op.person_id = co.person_id
JOIN concept c ON co.condition_concept_id = c.concept_id
WHERE c.concept_name LIKE '%diabetes%'
AND co.condition_start_date BETWEEN op.observation_period_start_date 
    AND op.observation_period_end_date
'''

cohort = pd.read_sql(diabetes_query, engine)
print({"cohort_size": len(cohort), "analysis": "diabetes_cohort"})
"""

result = await mcp.execute_python_code(sandbox_id=sandbox_id, code=code)
```

#### 2. Drug Safety Analysis
**Use Case**: Pharmacovigilance teams analyzing adverse drug events
```python
# Example: Adverse event analysis
code = """
import pandas as pd

# Analyze drug-adverse event associations
drug_ae_query = '''
SELECT 
    c1.concept_name as drug1,
    c2.concept_name as drug2,
    COUNT(DISTINCT de1.person_id) as patients_with_both
FROM drug_exposure de1
JOIN drug_exposure de2 ON de1.person_id = de2.person_id
JOIN concept c1 ON de1.drug_concept_id = c1.concept_id
JOIN concept c2 ON de2.drug_concept_id = c2.concept_id
WHERE de1.drug_exposure_start_date BETWEEN de2.drug_exposure_start_date 
    AND de2.drug_exposure_end_date
GROUP BY c1.concept_name, c2.concept_name
HAVING COUNT(DISTINCT de1.person_id) > 5
ORDER BY patients_with_both DESC
'''

results = pd.read_sql(drug_ae_query, engine)
print({"analysis": "drug_safety", "results": results.to_dict()})
"""
```

#### 3. Population Health Analytics
**Use Case**: Public health officials analyzing population-level health trends
```python
# Example: Population health metrics
code = """
import pandas as pd
from datetime import datetime, timedelta

# Calculate population health metrics
health_metrics = '''
SELECT 
    EXTRACT(YEAR FROM observation_period_start_date) as year,
    COUNT(DISTINCT person_id) as population_size,
    AVG(EXTRACT(YEAR FROM observation_period_start_date) - 
        EXTRACT(YEAR FROM birth_datetime)) as avg_age
FROM observation_period op
JOIN person p ON op.person_id = p.person_id
GROUP BY EXTRACT(YEAR FROM observation_period_start_date)
ORDER BY year
'''

metrics = pd.read_sql(health_metrics, engine)
print({"analysis": "population_health", "metrics": metrics.to_dict()})
"""
```

#### 4. Clinical Decision Support
**Use Case**: AI agents providing clinical decision support based on patient data
```python
# Example: Risk stratification for cardiovascular disease
code = """
import pandas as pd
import numpy as np

def calculate_cvd_risk(patient_id):
    # Get patient demographics and conditions
    patient_query = f'''
    SELECT 
        p.gender_concept_id,
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) as age,
        c.concept_name as condition_name
    FROM person p
    LEFT JOIN condition_occurrence co ON p.person_id = co.person_id
    LEFT JOIN concept c ON co.condition_concept_id = c.concept_id
    WHERE p.person_id = {patient_id}
    '''
    
    patient_data = pd.read_sql(patient_query, engine)
    
    # Simple risk calculation (simplified for example)
    risk_score = 0
    if patient_data['age'].iloc[0] > 65:
        risk_score += 2
    if 'hypertension' in patient_data['condition_name'].values:
        risk_score += 1
    if 'diabetes' in patient_data['condition_name'].values:
        risk_score += 1
        
    return {"patient_id": patient_id, "cvd_risk_score": risk_score}

# Calculate risk for a specific patient
result = calculate_cvd_risk(12345)
print(result)
"""
```

#### 5. Real-time Patient Monitoring
**Use Case**: Continuous monitoring of patient vitals and alerts
```python
# Example: Real-time vital sign monitoring
code = """
import pandas as pd
from datetime import datetime, timedelta

def monitor_patient_vitals(patient_id, hours_back=24):
    # Get recent vital signs
    vitals_query = f'''
    SELECT 
        m.measurement_datetime,
        c.concept_name as vital_type,
        m.value_as_number,
        m.unit_concept_id
    FROM measurement m
    JOIN concept c ON m.measurement_concept_id = c.concept_id
    WHERE m.person_id = {patient_id}
    AND m.measurement_datetime >= NOW() - INTERVAL '{hours_back} hours'
    AND c.concept_name IN ('Systolic Blood Pressure', 'Diastolic Blood Pressure', 
                          'Body Temperature', 'Heart Rate', 'Respiratory Rate')
    ORDER BY m.measurement_datetime DESC
    '''
    
    vitals = pd.read_sql(vitals_query, engine)
    
    # Check for critical values
    alerts = []
    for vital_type in vitals['vital_type'].unique():
        vital_data = vitals[vitals['vital_type'] == vital_type]
        latest_value = vital_data['value_as_number'].iloc[0]
        
        if vital_type == 'Systolic Blood Pressure' and latest_value > 180:
            alerts.append(f"High systolic BP: {latest_value}")
        elif vital_type == 'Heart Rate' and latest_value > 100:
            alerts.append(f"Tachycardia: {latest_value} bpm")
        elif vital_type == 'Body Temperature' and latest_value > 38:
            alerts.append(f"Fever: {latest_value}°C")
    
    return {
        "patient_id": patient_id,
        "monitoring_period_hours": hours_back,
        "vital_signs": vitals.to_dict(),
        "alerts": alerts,
        "timestamp": datetime.now().isoformat()
    }

# Monitor specific patient
result = monitor_patient_vitals(12345, hours_back=12)
print(result)
"""
```

#### 6. Clinical Trial Recruitment
**Use Case**: Identifying eligible patients for clinical trials
```python
# Example: Clinical trial eligibility screening
code = """
import pandas as pd

def screen_trial_eligibility(trial_criteria):
    """
    Screen patients for clinical trial eligibility
    
    Args:
        trial_criteria: Dict with inclusion/exclusion criteria
    """
    # Build dynamic query based on criteria
    inclusion_conditions = []
    exclusion_conditions = []
    
    if 'age_min' in trial_criteria:
        inclusion_conditions.append(f"EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) >= {trial_criteria['age_min']}")
    
    if 'age_max' in trial_criteria:
        inclusion_conditions.append(f"EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) <= {trial_criteria['age_max']}")
    
    if 'required_conditions' in trial_criteria:
        conditions = "', '".join(trial_criteria['required_conditions'])
        inclusion_conditions.append(f"""
        EXISTS (
            SELECT 1 FROM condition_occurrence co
            JOIN concept c ON co.condition_concept_id = c.concept_id
            WHERE co.person_id = p.person_id
            AND c.concept_name IN ('{conditions}')
        )
        """)
    
    if 'excluded_conditions' in trial_criteria:
        conditions = "', '".join(trial_criteria['excluded_conditions'])
        exclusion_conditions.append(f"""
        NOT EXISTS (
            SELECT 1 FROM condition_occurrence co
            JOIN concept c ON co.condition_concept_id = c.concept_id
            WHERE co.person_id = p.person_id
            AND c.concept_name IN ('{conditions}')
        )
        """)
    
    # Build final query
    where_clause = " AND ".join(inclusion_conditions + exclusion_conditions)
    
    eligibility_query = f'''
    SELECT 
        p.person_id,
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) as age,
        p.gender_concept_id
    FROM person p
    WHERE {where_clause}
    '''
    
    eligible_patients = pd.read_sql(eligibility_query, engine)
    
    return {
        "trial_criteria": trial_criteria,
        "eligible_count": len(eligible_patients),
        "eligible_patients": eligible_patients.to_dict(),
        "screening_date": datetime.now().isoformat()
    }

# Example: Diabetes trial screening
diabetes_trial_criteria = {
    "age_min": 18,
    "age_max": 75,
    "required_conditions": ["Type 2 Diabetes Mellitus"],
    "excluded_conditions": ["Pregnancy", "End Stage Renal Disease"]
}

result = screen_trial_eligibility(diabetes_trial_criteria)
print(result)
"""
```

#### 7. Quality Metrics and Reporting
**Use Case**: Healthcare quality improvement and regulatory reporting
```python
# Example: Healthcare quality metrics calculation
code = """
import pandas as pd
from datetime import datetime, timedelta

def calculate_quality_metrics(metric_type, date_range=None):
    """
    Calculate healthcare quality metrics
    
    Args:
        metric_type: Type of metric ('diabetes_control', 'hypertension_control', 'preventive_care')
        date_range: Tuple of (start_date, end_date)
    """
    
    if date_range is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
    else:
        start_date, end_date = date_range
    
    if metric_type == 'diabetes_control':
        # HbA1c control metrics
        diabetes_metrics = f'''
        SELECT 
            COUNT(DISTINCT p.person_id) as total_diabetes_patients,
            COUNT(CASE WHEN m.value_as_number < 7.0 THEN 1 END) as controlled_patients,
            AVG(m.value_as_number) as avg_hba1c
        FROM person p
        JOIN condition_occurrence co ON p.person_id = co.person_id
        JOIN concept c ON co.condition_concept_id = c.concept_id
        LEFT JOIN measurement m ON p.person_id = m.person_id
        LEFT JOIN concept mc ON m.measurement_concept_id = mc.concept_id
        WHERE c.concept_name ILIKE '%diabetes%'
        AND mc.concept_name ILIKE '%HbA1c%'
        AND m.measurement_date BETWEEN '{start_date.date()}' AND '{end_date.date()}'
        '''
        
        metrics = pd.read_sql(diabetes_metrics, engine)
        control_rate = (metrics['controlled_patients'].iloc[0] / metrics['total_diabetes_patients'].iloc[0]) * 100
        
        return {
            "metric_type": "diabetes_control",
            "total_patients": metrics['total_diabetes_patients'].iloc[0],
            "controlled_patients": metrics['controlled_patients'].iloc[0],
            "control_rate_percent": round(control_rate, 2),
            "average_hba1c": round(metrics['avg_hba1c'].iloc[0], 2),
            "measurement_period": f"{start_date.date()} to {end_date.date()}"
        }
    
    elif metric_type == 'preventive_care':
        # Preventive care metrics
        preventive_metrics = f'''
        SELECT 
            COUNT(DISTINCT p.person_id) as total_patients,
            COUNT(CASE WHEN p.person_id IN (
                SELECT DISTINCT person_id FROM procedure_occurrence po
                JOIN concept c ON po.procedure_concept_id = c.concept_id
                WHERE c.concept_name ILIKE '%mammogram%'
                AND po.procedure_date BETWEEN '{start_date.date()}' AND '{end_date.date()}'
            ) THEN 1 END) as mammogram_patients,
            COUNT(CASE WHEN p.person_id IN (
                SELECT DISTINCT person_id FROM procedure_occurrence po
                JOIN concept c ON po.procedure_concept_id = c.concept_id
                WHERE c.concept_name ILIKE '%colonoscopy%'
                AND po.procedure_date BETWEEN '{start_date.date()}' AND '{end_date.date()}'
            ) THEN 1 END) as colonoscopy_patients
        FROM person p
        WHERE EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) >= 50
        '''
        
        metrics = pd.read_sql(preventive_metrics, engine)
        
        return {
            "metric_type": "preventive_care",
            "total_eligible_patients": metrics['total_patients'].iloc[0],
            "mammogram_rate": round((metrics['mammogram_patients'].iloc[0] / metrics['total_patients'].iloc[0]) * 100, 2),
            "colonoscopy_rate": round((metrics['colonoscopy_patients'].iloc[0] / metrics['total_patients'].iloc[0]) * 100, 2),
            "measurement_period": f"{start_date.date()} to {end_date.date()}"
        }

# Calculate diabetes control metrics
diabetes_metrics = calculate_quality_metrics('diabetes_control')
print(diabetes_metrics)

# Calculate preventive care metrics
preventive_metrics = calculate_quality_metrics('preventive_care')
print(preventive_metrics)
"""
```

### MCP Agent Integration for OMOP CDM

#### Agent Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OMOP MCP      │    │   OMCP Python   │    │   OMOP CDM      │
│   Agent         │◄──►│   Sandbox       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Clinical      │    │   Secure Code   │    │   Patient       │
│   Queries       │    │   Execution     │    │   Data          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Agent Workflow
1. **Query Reception**: Agent receives clinical analysis request
2. **Code Generation**: Agent generates Python code for OMOP CDM analysis
3. **Sandbox Execution**: Code executed in isolated container
4. **Result Processing**: Results returned to agent for interpretation
5. **Response Generation**: Agent provides clinical insights

#### Security Considerations for Healthcare Data
- **HIPAA Compliance**: All data processing in isolated containers
- **Audit Trails**: Complete logging of all code execution
- **Data Minimization**: Only necessary data accessed
- **Access Controls**: Strict container isolation
- **Encryption**: Data encrypted in transit and at rest

### OMOP CDM Analysis Tools

#### Pre-installed Packages for OMOP Analysis
```python
# Install OMOP-specific packages
packages = [
    "pandas",
    "numpy", 
    "sqlalchemy",
    "psycopg2-binary",
    "scikit-learn",
    "matplotlib",
    "seaborn"
]

for package in packages:
    result = await mcp.install_package(sandbox_id=sandbox_id, package=package)
```

#### Common OMOP Analysis Patterns
```python
# Pattern 1: Cohort Definition
cohort_code = """
# Define study cohort
cohort_query = '''
SELECT DISTINCT person_id
FROM condition_occurrence co
JOIN concept c ON co.condition_concept_id = c.concept_id
WHERE c.concept_name ILIKE '%diabetes%'
AND co.condition_start_date >= '2020-01-01'
'''
"""

# Pattern 2: Outcome Analysis
outcome_code = """
# Analyze outcomes
outcome_query = '''
SELECT 
    co.condition_concept_id,
    c.concept_name,
    COUNT(*) as event_count
FROM condition_occurrence co
JOIN concept c ON co.condition_concept_id = c.concept_id
WHERE co.person_id IN ({cohort_person_ids})
GROUP BY co.condition_concept_id, c.concept_name
ORDER BY event_count DESC
'''
"""
```

### Integration Examples

#### Example 1: Clinical Trial Feasibility Analysis
```python
# Agent receives request: "Analyze feasibility of diabetes trial"
agent_code = """
# Generate feasibility analysis code
feasibility_analysis = '''
import pandas as pd
from sqlalchemy import create_engine

# Connect to OMOP CDM
engine = create_engine('postgresql://user:pass@host:port/omop_cdm')

# Find eligible patients
eligibility_query = '''
SELECT COUNT(DISTINCT p.person_id) as eligible_patients
FROM person p
JOIN condition_occurrence co ON p.person_id = co.person_id
JOIN concept c ON co.condition_concept_id = c.concept_id
WHERE c.concept_name ILIKE '%diabetes%'
AND EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) BETWEEN 18 AND 75
AND p.gender_concept_id = 8507  -- Male
'''

result = pd.read_sql(eligibility_query, engine)
print({"eligible_patients": result['eligible_patients'].iloc[0]})
'''

# Execute in sandbox
sandbox_result = await mcp.execute_python_code(sandbox_id=sandbox_id, code=feasibility_analysis)
"""
```

#### Example 2: Real-time Clinical Decision Support
```python
# Agent receives patient data and needs to provide recommendations
decision_support = """
# Generate decision support analysis
patient_analysis = '''
import pandas as pd
import numpy as np

def analyze_patient_risk(patient_id):
    # Get patient history
    history_query = f'''
    SELECT 
        c.concept_name,
        co.condition_start_date,
        co.condition_end_date
    FROM condition_occurrence co
    JOIN concept c ON co.condition_concept_id = c.concept_id
    WHERE co.person_id = {patient_id}
    ORDER BY co.condition_start_date DESC
    '''
    
    history = pd.read_sql(history_query, engine)
    
    # Risk assessment logic
    risk_factors = ['hypertension', 'diabetes', 'obesity', 'smoking']
    risk_score = sum(1 for factor in risk_factors if factor in history['concept_name'].values)
    
    recommendations = []
    if risk_score >= 3:
        recommendations.append("High cardiovascular risk - consider statin therapy")
    if 'diabetes' in history['concept_name'].values:
        recommendations.append("Monitor HbA1c levels quarterly")
    
    return {
        "patient_id": patient_id,
        "risk_score": risk_score,
        "recommendations": recommendations
    }

# Analyze specific patient
result = analyze_patient_risk(12345)
print(result)
'''
"""
```

### Best Practices for OMOP CDM Integration

#### 1. Data Privacy
- Always use parameterized queries
- Implement data minimization principles
- Log all data access for audit purposes
- Use de-identified data when possible

#### 2. Performance Optimization
- Use appropriate indexes on OMOP tables
- Implement query timeouts
- Cache frequently used cohort definitions
- Use materialized views for complex analyses

#### 3. Error Handling
- Implement comprehensive error handling for database connections
- Provide meaningful error messages for clinical users
- Log all errors for debugging and compliance

#### 4. Validation
- Validate all clinical concepts before querying
- Implement result validation for clinical plausibility
- Use OMOP CDM conventions for concept mapping

### OMOP CDM MCP Agent Patterns

#### Pattern 1: Clinical Query Agent
**Purpose**: AI agent that translates natural language clinical questions into OMOP CDM queries

```python
# Agent workflow for clinical queries
async def clinical_query_agent(question: str, sandbox_id: str):
    """
    Process clinical questions and return OMOP CDM analysis
    """
    
    # Step 1: Generate SQL query from natural language
    query_generation = f"""
    # Generate OMOP CDM query from clinical question
    question = "{question}"
    
    # Use LLM to generate SQL (simplified example)
    if "diabetes" in question.lower() and "prevalence" in question.lower():
        sql_query = '''
        SELECT 
            COUNT(DISTINCT p.person_id) as diabetes_patients,
            COUNT(DISTINCT p.person_id) * 100.0 / (
                SELECT COUNT(DISTINCT person_id) FROM person
            ) as prevalence_percent
        FROM person p
        JOIN condition_occurrence co ON p.person_id = co.person_id
        JOIN concept c ON co.condition_concept_id = c.concept_id
        WHERE c.concept_name ILIKE '%diabetes%'
        '''
    elif "drug" in question.lower() and "interaction" in question.lower():
        sql_query = '''
        SELECT 
            c1.concept_name as drug1,
            c2.concept_name as drug2,
            COUNT(DISTINCT de1.person_id) as patients_with_both
        FROM drug_exposure de1
        JOIN drug_exposure de2 ON de1.person_id = de2.person_id
        JOIN concept c1 ON de1.drug_concept_id = c1.concept_id
        JOIN concept c2 ON de2.drug_concept_id = c2.concept_id
        WHERE de1.drug_exposure_start_date BETWEEN de2.drug_exposure_start_date 
            AND de2.drug_exposure_end_date
        GROUP BY c1.concept_name, c2.concept_name
        HAVING COUNT(DISTINCT de1.person_id) > 5
        ORDER BY patients_with_both DESC
        '''
    
    # Step 2: Execute query in sandbox
    analysis_code = f'''
    import pandas as pd
    from sqlalchemy import create_engine
    
    # Connect to OMOP CDM
    engine = create_engine('postgresql://user:pass@host:port/omop_cdm')
    
    # Execute generated query
    result = pd.read_sql("""{sql_query}""", engine)
    
    # Format results for clinical interpretation
    print({{
        "question": "{question}",
        "analysis_type": "clinical_query",
        "results": result.to_dict(),
        "interpretation": "Clinical analysis completed"
    }})
    '''
    
    # Execute in sandbox
    result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code=analysis_code,
        timeout=120
    )
    
    return result
```

#### Pattern 2: Patient Cohort Agent
**Purpose**: AI agent that manages patient cohorts for clinical research

```python
# Agent workflow for cohort management
async def cohort_management_agent(cohort_definition: dict, sandbox_id: str):
    """
    Manage patient cohorts for clinical research
    """
    
    # Step 1: Create cohort based on definition
    cohort_creation = f"""
    import pandas as pd
    from datetime import datetime
    
    # Define cohort based on criteria
    cohort_criteria = {cohort_definition}
    
    # Build cohort query
    inclusion_conditions = []
    if 'age_range' in cohort_criteria:
        min_age, max_age = cohort_criteria['age_range']
        inclusion_conditions.append(f"EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) BETWEEN {min_age} AND {max_age}")
    
    if 'conditions' in cohort_criteria:
        conditions = "', '".join(cohort_criteria['conditions'])
        inclusion_conditions.append(f'''
        EXISTS (
            SELECT 1 FROM condition_occurrence co
            JOIN concept c ON co.condition_concept_id = c.concept_id
            WHERE co.person_id = p.person_id
            AND c.concept_name IN ('{conditions}')
        )
        ''')
    
    where_clause = " AND ".join(inclusion_conditions)
    
    cohort_query = f'''
    SELECT 
        p.person_id,
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) as age,
        p.gender_concept_id,
        op.observation_period_start_date,
        op.observation_period_end_date
    FROM person p
    JOIN observation_period op ON p.person_id = op.person_id
    WHERE {where_clause}
    '''
    
    # Execute cohort query
    cohort = pd.read_sql(cohort_query, engine)
    
    # Calculate cohort statistics
    cohort_stats = {{
        "cohort_id": cohort_criteria.get('cohort_name', 'unnamed_cohort'),
        "total_patients": len(cohort),
        "age_distribution": {{
            "mean_age": cohort['age'].mean(),
            "min_age": cohort['age'].min(),
            "max_age": cohort['age'].max()
        }},
        "gender_distribution": cohort['gender_concept_id'].value_counts().to_dict(),
        "observation_period": {{
            "mean_duration_days": (cohort['observation_period_end_date'] - cohort['observation_period_start_date']).dt.days.mean()
        }},
        "created_at": datetime.now().isoformat()
    }}
    
    print(cohort_stats)
    """
    
    # Execute cohort creation
    result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code=cohort_creation,
        timeout=60
    )
    
    return result
```

#### Pattern 3: Clinical Decision Support Agent
**Purpose**: AI agent that provides real-time clinical recommendations

```python
# Agent workflow for clinical decision support
async def clinical_decision_agent(patient_id: int, clinical_context: str, sandbox_id: str):
    """
    Provide clinical decision support for specific patient
    """
    
    # Step 1: Gather patient data
    patient_analysis = f"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Gather comprehensive patient data
    patient_query = f'''
    SELECT 
        p.person_id,
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) as age,
        p.gender_concept_id,
        c.concept_name as condition_name,
        co.condition_start_date,
        co.condition_end_date,
        m.measurement_concept_id,
        mc.concept_name as measurement_name,
        m.value_as_number,
        m.unit_concept_id,
        d.drug_concept_id,
        dc.concept_name as drug_name,
        d.drug_exposure_start_date,
        d.drug_exposure_end_date
    FROM person p
    LEFT JOIN condition_occurrence co ON p.person_id = co.person_id
    LEFT JOIN concept c ON co.condition_concept_id = c.concept_id
    LEFT JOIN measurement m ON p.person_id = m.person_id
    LEFT JOIN concept mc ON m.measurement_concept_id = mc.concept_id
    LEFT JOIN drug_exposure d ON p.person_id = d.person_id
    LEFT JOIN concept dc ON d.drug_concept_id = dc.concept_id
    WHERE p.person_id = {patient_id}
    AND (co.condition_start_date >= NOW() - INTERVAL '2 years' OR co.condition_start_date IS NULL)
    AND (m.measurement_date >= NOW() - INTERVAL '1 year' OR m.measurement_date IS NULL)
    AND (d.drug_exposure_start_date >= NOW() - INTERVAL '1 year' OR d.drug_exposure_start_date IS NULL)
    ORDER BY co.condition_start_date DESC, m.measurement_date DESC, d.drug_exposure_start_date DESC
    '''
    
    patient_data = pd.read_sql(patient_query, engine)
    
    # Step 2: Analyze clinical context
    context = "{clinical_context}"
    
    # Step 3: Generate clinical recommendations
    recommendations = []
    risk_factors = []
    
    # Age-based recommendations
    age = patient_data['age'].iloc[0] if not patient_data.empty else 0
    if age >= 65:
        risk_factors.append("Advanced age")
        recommendations.append("Consider geriatric assessment")
    
    # Condition-based recommendations
    conditions = patient_data['condition_name'].dropna().unique()
    if 'diabetes' in [c.lower() for c in conditions]:
        risk_factors.append("Diabetes")
        recommendations.append("Monitor HbA1c quarterly")
        recommendations.append("Consider ACE inhibitor for renal protection")
    
    if 'hypertension' in [c.lower() for c in conditions]:
        risk_factors.append("Hypertension")
        recommendations.append("Monitor blood pressure monthly")
    
    # Medication-based recommendations
    medications = patient_data['drug_name'].dropna().unique()
    if 'warfarin' in [m.lower() for m in medications]:
        recommendations.append("Monitor INR regularly")
        recommendations.append("Avoid NSAIDs due to bleeding risk")
    
    # Vital signs analysis
    vitals = patient_data[patient_data['measurement_name'].notna()]
    if not vitals.empty:
        bp_readings = vitals[vitals['measurement_name'].str.contains('Blood Pressure', na=False)]
        if not bp_readings.empty:
            latest_bp = bp_readings['value_as_number'].iloc[0]
            if latest_bp > 140:
                recommendations.append("Blood pressure elevated - consider medication adjustment")
    
    # Step 4: Generate clinical summary
    clinical_summary = {{
        "patient_id": {patient_id},
        "age": age,
        "risk_factors": risk_factors,
        "active_conditions": list(conditions),
        "current_medications": list(medications),
        "recommendations": recommendations,
        "clinical_context": context,
        "analysis_timestamp": datetime.now().isoformat(),
        "confidence_score": 0.85  # Based on data completeness
    }}
    
    print(clinical_summary)
    """
    
    # Execute clinical analysis
    result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code=patient_analysis,
        timeout=90
    )
    
    return result
```

#### Pattern 4: Quality Metrics Agent
**Purpose**: AI agent that monitors and reports healthcare quality metrics

```python
# Agent workflow for quality metrics
async def quality_metrics_agent(metric_types: list, date_range: tuple, sandbox_id: str):
    """
    Calculate and report healthcare quality metrics
    """
    
    # Step 1: Calculate multiple quality metrics
    metrics_analysis = f"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Define date range
    start_date, end_date = {date_range}
    
    # Calculate multiple quality metrics
    metrics_results = {{}}
    
    # Diabetes control metrics
    if 'diabetes_control' in {metric_types}:
        diabetes_query = f'''
        SELECT 
            COUNT(DISTINCT p.person_id) as total_diabetes_patients,
            COUNT(CASE WHEN m.value_as_number < 7.0 THEN 1 END) as controlled_patients,
            AVG(m.value_as_number) as avg_hba1c
        FROM person p
        JOIN condition_occurrence co ON p.person_id = co.person_id
        JOIN concept c ON co.condition_concept_id = c.concept_id
        LEFT JOIN measurement m ON p.person_id = m.person_id
        LEFT JOIN concept mc ON m.measurement_concept_id = mc.concept_id
        WHERE c.concept_name ILIKE '%diabetes%'
        AND mc.concept_name ILIKE '%HbA1c%'
        AND m.measurement_date BETWEEN '{start_date}' AND '{end_date}'
        '''
        
        diabetes_metrics = pd.read_sql(diabetes_query, engine)
        control_rate = (diabetes_metrics['controlled_patients'].iloc[0] / 
                       diabetes_metrics['total_diabetes_patients'].iloc[0]) * 100
        
        metrics_results['diabetes_control'] = {{
            "metric_type": "diabetes_control",
            "total_patients": diabetes_metrics['total_diabetes_patients'].iloc[0],
            "controlled_patients": diabetes_metrics['controlled_patients'].iloc[0],
            "control_rate_percent": round(control_rate, 2),
            "average_hba1c": round(diabetes_metrics['avg_hba1c'].iloc[0], 2),
            "target_rate": 70.0,
            "status": "meets_target" if control_rate >= 70.0 else "below_target"
        }}
    
    # Hypertension control metrics
    if 'hypertension_control' in {metric_types}:
        hypertension_query = f'''
        SELECT 
            COUNT(DISTINCT p.person_id) as total_hypertension_patients,
            COUNT(CASE WHEN m.value_as_number < 140 THEN 1 END) as controlled_patients,
            AVG(m.value_as_number) as avg_systolic_bp
        FROM person p
        JOIN condition_occurrence co ON p.person_id = co.person_id
        JOIN concept c ON co.condition_concept_id = c.concept_id
        LEFT JOIN measurement m ON p.person_id = m.person_id
        LEFT JOIN concept mc ON m.measurement_concept_id = mc.concept_id
        WHERE c.concept_name ILIKE '%hypertension%'
        AND mc.concept_name ILIKE '%Systolic Blood Pressure%'
        AND m.measurement_date BETWEEN '{start_date}' AND '{end_date}'
        '''
        
        hypertension_metrics = pd.read_sql(hypertension_query, engine)
        control_rate = (hypertension_metrics['controlled_patients'].iloc[0] / 
                       hypertension_metrics['total_hypertension_patients'].iloc[0]) * 100
        
        metrics_results['hypertension_control'] = {{
            "metric_type": "hypertension_control",
            "total_patients": hypertension_metrics['total_hypertension_patients'].iloc[0],
            "controlled_patients": hypertension_metrics['controlled_patients'].iloc[0],
            "control_rate_percent": round(control_rate, 2),
            "average_systolic_bp": round(hypertension_metrics['avg_systolic_bp'].iloc[0], 2),
            "target_rate": 60.0,
            "status": "meets_target" if control_rate >= 60.0 else "below_target"
        }}
    
    # Preventive care metrics
    if 'preventive_care' in {metric_types}:
        preventive_query = f'''
        SELECT 
            COUNT(DISTINCT p.person_id) as total_eligible_patients,
            COUNT(CASE WHEN p.person_id IN (
                SELECT DISTINCT person_id FROM procedure_occurrence po
                JOIN concept c ON po.procedure_concept_id = c.concept_id
                WHERE c.concept_name ILIKE '%mammogram%'
                AND po.procedure_date BETWEEN '{start_date}' AND '{end_date}'
            ) THEN 1 END) as mammogram_patients,
            COUNT(CASE WHEN p.person_id IN (
                SELECT DISTINCT person_id FROM procedure_occurrence po
                JOIN concept c ON po.procedure_concept_id = c.concept_id
                WHERE c.concept_name ILIKE '%colonoscopy%'
                AND po.procedure_date BETWEEN '{start_date}' AND '{end_date}'
            ) THEN 1 END) as colonoscopy_patients
        FROM person p
        WHERE EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM p.birth_datetime) >= 50
        '''
        
        preventive_metrics = pd.read_sql(preventive_query, engine)
        
        metrics_results['preventive_care'] = {{
            "metric_type": "preventive_care",
            "total_eligible_patients": preventive_metrics['total_eligible_patients'].iloc[0],
            "mammogram_rate": round((preventive_metrics['mammogram_patients'].iloc[0] / 
                                   preventive_metrics['total_eligible_patients'].iloc[0]) * 100, 2),
            "colonoscopy_rate": round((preventive_metrics['colonoscopy_patients'].iloc[0] / 
                                     preventive_metrics['total_eligible_patients'].iloc[0]) * 100, 2),
            "target_mammogram_rate": 80.0,
            "target_colonoscopy_rate": 70.0
        }}
    
    # Generate quality report
    quality_report = {{
        "report_type": "quality_metrics",
        "date_range": {{
            "start_date": start_date,
            "end_date": end_date
        }},
        "metrics": metrics_results,
        "overall_status": "meets_targets" if all(
            m.get('status', 'meets_target') == 'meets_target' 
            for m in metrics_results.values() if 'status' in m
        ) else "needs_improvement",
        "generated_at": datetime.now().isoformat()
    }}
    
    print(quality_report)
    """
    
    # Execute metrics analysis
    result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code=metrics_analysis,
        timeout=120
    )
    
    return result
```

### OMOP CDM Agent Integration Workflows

#### Workflow 1: Clinical Research Pipeline
```python
# Complete clinical research workflow
async def clinical_research_workflow(research_question: str, sandbox_id: str):
    """
    End-to-end clinical research workflow using OMOP CDM
    """
    
    # Step 1: Create sandbox and install packages
    await mcp.install_package(sandbox_id=sandbox_id, package="pandas")
    await mcp.install_package(sandbox_id=sandbox_id, package="sqlalchemy")
    await mcp.install_package(sandbox_id=sandbox_id, package="psycopg2-binary")
    
    # Step 2: Define research cohort
    cohort_result = await cohort_management_agent({
        "cohort_name": "research_cohort",
        "age_range": [18, 75],
        "conditions": ["Type 2 Diabetes Mellitus"],
        "exclusion_criteria": ["Pregnancy", "End Stage Renal Disease"]
    }, sandbox_id)
    
    # Step 3: Perform clinical analysis
    analysis_result = await clinical_query_agent(research_question, sandbox_id)
    
    # Step 4: Generate research report
    report_result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code=f"""
        # Generate research report
        print({{
            "research_question": "{research_question}",
            "cohort_analysis": {cohort_result},
            "clinical_analysis": {analysis_result},
            "conclusions": "Research analysis completed",
            "recommendations": "Consider further investigation",
            "timestamp": datetime.now().isoformat()
        }})
        """,
        timeout=60
    )
    
    return report_result
```

#### Workflow 2: Real-time Clinical Monitoring
```python
# Real-time clinical monitoring workflow
async def clinical_monitoring_workflow(patient_ids: list, sandbox_id: str):
    """
    Real-time monitoring of multiple patients
    """
    
    # Step 1: Set up monitoring environment
    await mcp.install_package(sandbox_id=sandbox_id, package="pandas")
    await mcp.install_package(sandbox_id=sandbox_id, package="numpy")
    
    # Step 2: Monitor each patient
    monitoring_results = []
    for patient_id in patient_ids:
        result = await clinical_decision_agent(
            patient_id=patient_id,
            clinical_context="routine monitoring",
            sandbox_id=sandbox_id
        )
        monitoring_results.append(result)
    
    # Step 3: Generate monitoring summary
    summary_result = await mcp.execute_python_code(
        sandbox_id=sandbox_id,
        code=f"""
        # Generate monitoring summary
        print({{
            "monitoring_type": "real_time_clinical",
            "patients_monitored": len({patient_ids}),
            "monitoring_results": {monitoring_results},
            "alerts_generated": sum(1 for r in {monitoring_results} if r.get('alerts')),
            "timestamp": datetime.now().isoformat()
        }})
        """,
        timeout=60
    )
    
    return summary_result
```

---

## Usage Guide

### Starting the Server

#### Method 1: Direct Execution
```bash
python src/omcp_py/main.py
```

#### Method 2: Using MCP Inspector
```bash
# Terminal 1: Start server
python src/omcp_py/main.py

# Terminal 2: Start inspector
npx @modelcontextprotocol/inspector python src/omcp_py/main.py
```

### Tool Usage Examples

#### Create and Manage Sandboxes
```python
# Create a new sandbox
result = await mcp.create_sandbox(timeout=300)
sandbox_id = result["sandbox_id"]

# List all sandboxes
sandboxes = await mcp.list_sandboxes(include_inactive=False)

# Remove a sandbox
await mcp.remove_sandbox(sandbox_id=sandbox_id, force=True)
```

#### Execute Python Code
```python
# Basic code execution
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="print('Hello from sandbox!')",
    timeout=30
)

# Complex analysis
analysis_code = """
import numpy as np
import pandas as pd

# Perform analysis
data = np.random.randn(1000)
mean_val = np.mean(data)
std_val = np.std(data)

print({
    "mean": mean_val,
    "std": std_val,
    "analysis_complete": True
})
"""

result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code=analysis_code,
    timeout=60
)
```

#### Install Packages
```python
# Install single package
result = await mcp.install_package(
    sandbox_id=sandbox_id,
    package="numpy==1.24.0",
    timeout=60
)

# Install multiple packages
packages = ["pandas", "scikit-learn", "matplotlib"]
for package in packages:
    result = await mcp.install_package(
        sandbox_id=sandbox_id,
        package=package,
        timeout=60
    )
```

---

## API Reference

### Tool Specifications

#### `create_sandbox`
Creates a new isolated Python sandbox environment.

**Parameters:**
- `timeout` (Optional[int]): Sandbox timeout in seconds (default: 300)

**Returns:**
```json
{
    "success": true,
    "sandbox_id": "uuid-string",
    "created_at": "2024-01-01T12:00:00",
    "last_used": "2024-01-01T12:00:00"
}
```

#### `execute_python_code`
Executes Python code in a secure sandbox environment.

**Parameters:**
- `sandbox_id` (str): The unique identifier of the sandbox
- `code` (str): The Python code to execute
- `timeout` (Optional[int]): Execution timeout in seconds (default: 30)

**Returns:**
```json
{
    "success": true,
    "output": "Code execution output",
    "error": "",
    "exit_code": 0
}
```

#### `install_package`
Installs a Python package in a sandbox.

**Parameters:**
- `sandbox_id` (str): The unique identifier of the sandbox
- `package` (str): The package name and version (e.g., "numpy==1.24.0")
- `timeout` (Optional[int]): Installation timeout in seconds (default: 60)

**Returns:**
```json
{
    "success": true,
    "output": "Installation output",
    "error": "",
    "exit_code": 0
}
```

#### `list_sandboxes`
Lists all active Python sandboxes.

**Parameters:**
- `include_inactive` (bool): Whether to include inactive sandboxes (default: false)

**Returns:**
```json
{
    "success": true,
    "sandboxes": [
        {
            "id": "uuid-string",
            "created_at": "2024-01-01T12:00:00",
            "last_used": "2024-01-01T12:00:00"
        }
    ],
    "count": 1
}
```

#### `remove_sandbox`
Removes a Python sandbox.

**Parameters:**
- `sandbox_id` (str): The unique identifier of the sandbox to remove
- `force` (bool): Whether to force removal of active sandboxes (default: false)

**Returns:**
```json
{
    "success": true,
    "message": "Sandbox uuid-string removed successfully"
}
```

---

## Security

### Security Architecture

#### Container Security
- **Base Image**: `python:3.11-slim` (minimal attack surface)
- **User Isolation**: Containers run as UID 1000 (non-root)
- **Read-only Filesystem**: Prevents file system modifications
- **Dropped Capabilities**: Removes all Linux capabilities
- **No Privilege Escalation**: `security_opt=["no-new-privileges"]`
- **Network Isolation**: `network_mode="none"`

#### Resource Limits
- **Memory**: 512MB per sandbox
- **CPU**: Restricted CPU usage (50% of one core)
- **Execution Time**: Configurable timeouts (default: 30s)
- **File System**: Temporary filesystem mounts with size limits

#### Input Validation
- **Command Escaping**: Uses `shlex.quote` for proper escaping
- **Type Validation**: Comprehensive input type checking
- **Size Limits**: Maximum code size and output limits
- **Content Filtering**: Prevents dangerous system calls

### Security Best Practices

#### For Developers
1. **Always validate inputs** before processing
2. **Use parameterized queries** for database operations
3. **Implement proper error handling** without information leakage
4. **Log security events** for monitoring and audit
5. **Regular security updates** for dependencies

#### For Administrators
1. **Monitor container logs** for suspicious activity
2. **Implement network segmentation** for database access
3. **Regular security audits** of the system
4. **Backup and recovery** procedures
5. **Incident response** planning

---

## Development

### Project Structure
```
omcp_py/
├── src/
│   └── omcp_py/
│       ├── __init__.py
│       ├── main.py              # Main FastMCP server
│       ├── config.py            # Configuration management
│       ├── sandbox_manager.py   # Docker container management
│       ├── core/                # Core functionality
│       ├── tools/               # MCP tool implementations
│       └── utils/               # Utility functions
├── tests/                       # Test suite
├── pyproject.toml              # Project configuration
├── install.sh                  # Installation script
└── README.md                   # Project documentation
```

### Development Setup

#### 1. Clone and Install
```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py
uv pip install -e .
```

#### 2. Install Development Dependencies
```bash
uv pip install -r requirements.txt[dev]
```

#### 3. Run Tests
```bash
pytest tests/
```

#### 4. Code Formatting
```bash
black src/
ruff check src/
```

### Adding New Tools

#### 1. Define Tool Function
```python
@mcp.tool()
async def new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Description of the new tool.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 10)
    
    Returns:
        Dict containing the tool results
    """
    try:
        # Tool implementation
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

#### 2. Add to Main Server
Add the tool function to `src/omcp_py/main.py`

#### 3. Test the Tool
```bash
# Start server
python src/omcp_py/main.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python src/omcp_py/main.py
```

---

## Deployment

### Production Deployment

#### Docker Deployment
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -e .

# Expose port for MCP Inspector
EXPOSE 6274

# Start the server
CMD ["python", "src/omcp_py/main.py"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  omcp-sandbox:
    build: .
    ports:
      - "6274:6274"
    environment:
      - SANDBOX_TIMEOUT=300
      - MAX_SANDBOXES=10
      - LOG_LEVEL=INFO
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
```

### Environment Configuration

#### Production Environment Variables
```env
# Sandbox Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=50
DOCKER_IMAGE=python:3.11-slim

# Logging
LOG_LEVEL=WARNING
DEBUG=false

# Security
DOCKER_HOST=unix://var/run/docker.sock
```

### Monitoring and Logging

#### Logging Configuration
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('omcp-sandbox.log'),
        logging.StreamHandler()
    ]
)
```

#### Health Checks
```python
# Health check endpoint
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Check the health of the sandbox system."""
    try:
        # Check Docker connectivity
        docker_client.ping()
        
        # Check sandbox manager
        active_sandboxes = len(sandbox_manager.sandboxes)
        
        return {
            "status": "healthy",
            "docker_connected": True,
            "active_sandboxes": active_sandboxes,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

---

## Troubleshooting

### Common Issues

#### Docker Connection Issues
**Problem**: Cannot connect to Docker daemon
```bash
# Solution 1: Start Docker service
sudo systemctl start docker

# Solution 2: Check Docker context
docker context use default

# Solution 3: Fix permissions
sudo usermod -aG docker $USER
newgrp docker
```

#### Package Import Errors
**Problem**: Module not found errors
```bash
# Solution: Reinstall package in editable mode
uv pip install -e .
```

#### Sandbox Creation Timeout
**Problem**: Sandbox creation takes too long
```bash
# Solution 1: Check Docker image
docker pull python:3.11-slim

# Solution 2: Increase timeout
export SANDBOX_TIMEOUT=600
```

#### MCP Inspector Connection Issues
**Problem**: Cannot connect to MCP Inspector
```bash
# Solution 1: Check if server is running
ps aux | grep main.py

# Solution 2: Check port availability
netstat -tlnp | grep 6274

# Solution 3: Restart both server and inspector
```

### Debugging

#### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python src/omcp_py/main.py
```

#### Check Container Status
```bash
# List all containers
docker ps -a

# Check container logs
docker logs <container_id>

# Inspect container
docker inspect <container_id>
```

#### Test Individual Components
```python
# Test sandbox manager
from omcp_py.sandbox_manager import SandboxManager
from omcp_py.config import get_config

config = get_config()
manager = SandboxManager(config)

# Test sandbox creation
sandbox_id = manager.create_sandbox()
print(f"Created sandbox: {sandbox_id}")

# Test code execution
result = manager.execute_code(sandbox_id, "print('test')")
print(f"Execution result: {result}")

# Clean up
manager.remove_sandbox(sandbox_id)
```

---

## Contributing

### Development Workflow

#### 1. Fork the Repository
```bash
git clone https://github.com/your-username/omcp_py.git
cd omcp_py
```

#### 2. Create Feature Branch
```bash
git checkout -b feature/new-feature
```

#### 3. Make Changes
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation

#### 4. Run Tests
```bash
pytest tests/
black src/
ruff check src/
```

#### 5. Submit Pull Request
- Provide clear description of changes
- Include test results
- Update documentation if needed

### Code Style

#### Python Style Guide
- Follow PEP 8 conventions
- Use type hints for all functions
- Add docstrings for all public functions
- Keep functions small and focused

#### Example
```python
from typing import Dict, Any, Optional

def process_data(data: Dict[str, Any], timeout: Optional[int] = 30) -> Dict[str, Any]:
    """
    Process input data with optional timeout.
    
    Args:
        data: Input data dictionary
        timeout: Optional timeout in seconds
        
    Returns:
        Processed data dictionary
        
    Raises:
        ValueError: If data is invalid
        TimeoutError: If processing times out
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    # Process data
    result = {}
    for key, value in data.items():
        result[key] = process_value(value)
    
    return result
```

---

## FAQ

### General Questions

#### Q: What is MCP?
**A**: Model Context Protocol (MCP) is a standard for AI agents to interact with external tools and data sources. It provides a secure, standardized way for AI assistants to execute code and access resources.

#### Q: Why use Docker for sandboxing?
**A**: Docker provides strong isolation between different code executions, preventing malicious code from affecting the host system or other sandboxes. It also ensures consistent execution environments.

#### Q: Is this production-ready?
**A**: Yes, the OMCP Python Sandbox is designed for production use with enterprise-grade security features, comprehensive error handling, and robust logging.

### Technical Questions

#### Q: How do I increase the number of concurrent sandboxes?
**A**: Set the `MAX_SANDBOXES` environment variable:
```bash
export MAX_SANDBOXES=50
```

#### Q: Can I use custom Python packages?
**A**: Yes, you can install any Python package using the `install_package` tool. The sandbox supports pip installations.

#### Q: How do I debug code execution issues?
**A**: Use the MCP Inspector web interface or enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python src/omcp_py/main.py
```

### Security Questions

#### Q: Is the sandbox completely secure?
**A**: The sandbox provides strong isolation through Docker containers, but no system is 100% secure. Always follow security best practices and monitor for suspicious activity.

#### Q: Can sandboxes access the internet?
**A**: No, sandboxes run with `network_mode="none"` for security. If internet access is needed, it should be carefully considered and implemented with proper security measures.

#### Q: How do I audit sandbox usage?
**A**: All sandbox operations are logged. Check the application logs for detailed audit trails of code execution and resource usage.

### OMOP CDM Questions

#### Q: How do I connect to an OMOP CDM database?
**A**: Use SQLAlchemy to connect to your OMOP CDM database within the sandbox:
```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host:port/omop_cdm')
```

#### Q: Can I use OHDSI tools in the sandbox?
**A**: Yes, you can install and use OHDSI tools like ATLAS, Achilles, or custom R/Python packages for OMOP CDM analysis.

#### Q: How do I ensure HIPAA compliance?
**A**: The sandbox provides isolation and logging, but you must also ensure:
- Database connections use encrypted connections
- All data access is logged and audited
- Proper access controls are in place
- Data minimization principles are followed

---

## Support

### Getting Help

#### Documentation
- [README.md](README.md) - Quick start guide
- [WIKI.md](WIKI.md) - Comprehensive documentation
- [API Reference](#api-reference) - Tool specifications

#### Community
- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and share ideas
- Pull Requests: Contribute code and improvements

#### Contact
- Email: [project-email@example.com]
- GitHub: [https://github.com/fastomop/omcp_py]

---

*This wiki is maintained by the OMCP Python Sandbox development team. For the latest updates, check the GitHub repository.* 