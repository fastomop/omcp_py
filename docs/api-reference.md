# API Reference

This document provides comprehensive API documentation for all MCP tools available in the OMCP Python Sandbox.

## 📋 API Overview

The OMCP Python Sandbox exposes 5 MCP tools for secure Python code execution:

1. **`create_sandbox`** - Create new isolated Python environments
2. **`list_sandboxes`** - List and manage active sandboxes
3. **`remove_sandbox`** - Safely remove sandboxes with force option
4. **`execute_python_code`** - Run Python code in isolated containers
5. **`install_package`** - Install Python packages in sandboxes

## 🔧 Tool Specifications

### 1. `create_sandbox`

Creates a new isolated Python sandbox environment.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeout` | `Optional[int]` | No | `300` | Sandbox timeout in seconds |

#### Returns

```json
{
    "success": true,
    "sandbox_id": "uuid-string",
    "created_at": "2024-01-01T12:00:00",
    "last_used": "2024-01-01T12:00:00"
}
```

#### Error Response

```json
{
    "success": false,
    "error": "Error message describing the failure"
}
```

#### Example Usage

```python
# Create a new sandbox with default timeout
result = await mcp.create_sandbox()

# Create a new sandbox with custom timeout
result = await mcp.create_sandbox(timeout=600)
```

#### Implementation Details

- **Container Creation**: Creates a new Docker container with enhanced security
- **Security Features**: Network isolation, resource limits, read-only filesystem
- **ID Generation**: Generates unique UUID for sandbox identification
- **Metadata Tracking**: Tracks creation time and last usage time
- **Capacity Limits**: Enforces maximum sandbox count configuration

### 2. `list_sandboxes`

Lists all active Python sandboxes.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_inactive` | `bool` | No | `false` | Whether to include inactive sandboxes |

#### Returns

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

#### Error Response

```json
{
    "success": false,
    "error": "Error message describing the failure"
}
```

#### Example Usage

```python
# List only active sandboxes
result = await mcp.list_sandboxes()

# List all sandboxes including inactive ones
result = await mcp.list_sandboxes(include_inactive=true)
```

#### Implementation Details

- **Active Filtering**: Filters out inactive sandboxes based on timeout configuration
- **Timeout Calculation**: Uses `SANDBOX_TIMEOUT` environment variable
- **Metadata Retrieval**: Returns creation and last usage timestamps
- **Count Tracking**: Provides count of sandboxes in the list

### 3. `remove_sandbox`

Removes a Python sandbox.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sandbox_id` | `str` | Yes | - | The unique identifier of the sandbox to remove |
| `force` | `bool` | No | `false` | Whether to force removal of active sandboxes |

#### Returns

```json
{
    "success": true,
    "message": "Sandbox uuid-string removed successfully"
}
```

#### Error Response

```json
{
    "success": false,
    "error": "Error message describing the failure"
}
```

#### Example Usage

```python
# Remove an inactive sandbox
result = await mcp.remove_sandbox(sandbox_id="uuid-string")

# Force remove an active sandbox
result = await mcp.remove_sandbox(sandbox_id="uuid-string", force=true)
```

#### Implementation Details

- **Existence Validation**: Checks if sandbox exists before removal
- **Activity Check**: Prevents removal of active sandboxes (unless forced)
- **Force Option**: Allows forced removal of active sandboxes
- **Container Cleanup**: Stops and removes Docker container
- **Metadata Cleanup**: Removes sandbox tracking data

### 4. `execute_python_code`

Executes Python code in a secure sandbox environment.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sandbox_id` | `str` | Yes | - | The unique identifier of the sandbox |
| `code` | `str` | Yes | - | The Python code to execute |
| `timeout` | `Optional[int]` | No | `30` | Execution timeout in seconds |

#### Returns

```json
{
    "success": true,
    "output": "Code execution output",
    "error": "",
    "exit_code": 0
}
```

#### Error Response

```json
{
    "success": false,
    "error": "Error message describing the failure"
}
```

#### Example Usage

```python
# Execute simple Python code
result = await mcp.execute_python_code(
    sandbox_id="uuid-string",
    code="print('Hello, World!')"
)

# Execute complex code with timeout
result = await mcp.execute_python_code(
    sandbox_id="uuid-string",
    code="""
import numpy as np
data = np.random.randn(1000)
print(f"Mean: {np.mean(data):.2f}")
print(f"Std: {np.std(data):.2f}")
""",
    timeout=60
)
```

#### Implementation Details

- **Input Validation**: Validates sandbox existence and code content
- **Code Execution**: Executes Python code in isolated container
- **Output Capture**: Captures stdout, stderr, and exit codes
- **Success Determination**: Based on exit code (0 = success)
- **Timeout Control**: Enforces execution time limits

### 5. `install_package`

Installs a Python package in a sandbox.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sandbox_id` | `str` | Yes | - | The unique identifier of the sandbox |
| `package` | `str` | Yes | - | The package name and version (e.g., "numpy==1.24.0") |
| `timeout` | `Optional[int]` | No | `60` | Installation timeout in seconds |

#### Returns

```json
{
    "success": true,
    "output": "Installation output",
    "error": "",
    "exit_code": 0
}
```

#### Error Response

```json
{
    "success": false,
    "error": "Error message describing the failure"
}
```

#### Example Usage

```python
# Install a specific package version
result = await mcp.install_package(
    sandbox_id="uuid-string",
    package="numpy==1.24.0"
)

# Install latest version of a package
result = await mcp.install_package(
    sandbox_id="uuid-string",
    package="pandas"
)

# Install multiple packages
packages = ["numpy", "pandas", "scikit-learn"]
for package in packages:
    result = await mcp.install_package(
        sandbox_id="uuid-string",
        package=package
    )
```

#### Implementation Details

- **Package Validation**: Validates package name and sandbox existence
- **Command Escaping**: Uses `shlex.quote` for shell safety
- **Pip Installation**: Uses pip for package installation
- **Output Handling**: Captures installation output and errors
- **Timeout Control**: Enforces installation time limits

## 📊 Response Format

### Standard Response Structure

All tools return responses in a consistent format:

```json
{
    "success": boolean,
    "data": object | null,
    "error": string | null,
    "metadata": object | null
}
```

### Success Response

```json
{
    "success": true,
    "data": {
        // Tool-specific data
    },
    "error": null,
    "metadata": {
        "timestamp": "2024-01-01T12:00:00",
        "execution_time_ms": 150
    }
}
```

### Error Response

```json
{
    "success": false,
    "data": null,
    "error": "Detailed error message",
    "metadata": {
        "timestamp": "2024-01-01T12:00:00",
        "error_code": "SANDBOX_NOT_FOUND"
    }
}
```

## 🔒 Security Considerations

### Input Validation

All tools implement comprehensive input validation:

- **Sandbox ID Validation**: Ensures sandbox exists before operations
- **Code Validation**: Validates code content and length
- **Package Validation**: Validates package names and versions
- **Parameter Validation**: Validates parameter types and ranges

### Command Escaping

```python
# Example: Package installation with command escaping
escaped_package = quote(package.strip())
install_command = f"pip install {escaped_package}"
```

### Container Security

- **Network Isolation**: Containers run with `network_mode="none"`
- **Resource Limits**: Memory (512MB), CPU (50% of one core)
- **User Isolation**: Non-root user (UID 1000)
- **Filesystem Security**: Read-only with temporary mounts
- **Capability Dropping**: All Linux capabilities removed

## ⏱️ Timeout Configuration

### Default Timeouts

| Tool | Default Timeout | Environment Variable |
|------|----------------|---------------------|
| `create_sandbox` | 300 seconds | `SANDBOX_TIMEOUT` |
| `execute_python_code` | 30 seconds | - |
| `install_package` | 60 seconds | - |

### Timeout Behavior

- **Sandbox Creation**: Timeout for sandbox lifecycle
- **Code Execution**: Timeout for individual code execution
- **Package Installation**: Timeout for package installation
- **Auto-cleanup**: Automatic removal of expired sandboxes

## 📈 Performance Characteristics

### Resource Limits

- **Memory**: 512MB per sandbox
- **CPU**: 50% of one core per sandbox
- **Disk**: 100MB temporary filesystem
- **Network**: No network access

### Scalability

- **Concurrent Sandboxes**: Configurable maximum (default: 10)
- **Auto-cleanup**: Automatic removal of inactive sandboxes
- **Resource Management**: Efficient container lifecycle management

## 🧪 Testing and Validation

### Tool Testing

Each tool can be tested using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python src/omcp_py/main.py
```

### Example Test Scenarios

```python
# Test sandbox creation
result = await mcp.create_sandbox()
assert result["success"] == True
sandbox_id = result["sandbox_id"]

# Test code execution
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="print('test')"
)
assert result["success"] == True
assert result["output"] == "test\n"

# Test package installation
result = await mcp.install_package(
    sandbox_id=sandbox_id,
    package="numpy"
)
assert result["success"] == True

# Test sandbox cleanup
result = await mcp.remove_sandbox(sandbox_id=sandbox_id)
assert result["success"] == True
```

## 🔄 Error Handling

### Error Types

1. **Validation Errors**: Invalid parameters or inputs
2. **Resource Errors**: Sandbox not found or resource limits exceeded
3. **Execution Errors**: Code execution failures
4. **System Errors**: Docker or system-level failures

### Error Recovery

- **Automatic Cleanup**: Failed sandboxes are automatically cleaned up
- **Resource Limits**: Enforced to prevent resource exhaustion
- **Timeout Handling**: Prevents hanging operations
- **Logging**: Comprehensive error logging for debugging

## 📚 Usage Examples

### Complete Workflow Example

```python
# 1. Create a new sandbox
result = await mcp.create_sandbox()
sandbox_id = result["sandbox_id"]

# 2. Install required packages
await mcp.install_package(sandbox_id=sandbox_id, package="numpy")
await mcp.install_package(sandbox_id=sandbox_id, package="pandas")

# 3. Execute analysis code
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="""
import numpy as np
import pandas as pd

# Perform data analysis
data = np.random.randn(1000)
df = pd.DataFrame(data, columns=['values'])

print({
    "mean": float(df['values'].mean()),
    "std": float(df['values'].std()),
    "count": len(df)
})
"""
)

# 4. Clean up sandbox
await mcp.remove_sandbox(sandbox_id=sandbox_id)
```

### OMOP CDM Analysis Example

```python
# Create sandbox for clinical analysis
result = await mcp.create_sandbox()
sandbox_id = result["sandbox_id"]

# Install clinical analysis packages
packages = ["pandas", "sqlalchemy", "psycopg2-binary"]
for package in packages:
    await mcp.install_package(sandbox_id=sandbox_id, package=package)

# Execute clinical query
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code="""
import pandas as pd
from sqlalchemy import create_engine

# Connect to OMOP CDM
engine = create_engine('postgresql://user:pass@host:port/omop_cdm')

# Query diabetes patients
query = '''
SELECT COUNT(DISTINCT person_id) as diabetes_count
FROM condition_occurrence co
JOIN concept c ON co.condition_concept_id = c.concept_id
WHERE c.concept_name ILIKE '%diabetes%'
'''

result = pd.read_sql(query, engine)
print({"diabetes_patients": int(result['diabetes_count'].iloc[0])})
"""
)

# Clean up
await mcp.remove_sandbox(sandbox_id=sandbox_id)
```

---

*This document provides complete API reference. For implementation details, see [Implementation Details](implementation.md).* 