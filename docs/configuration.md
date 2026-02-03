# Configuration Guide

This document provides comprehensive information about configuring the OMCP Python Sandbox, including environment variables, configuration options, and tuning parameters.

## ⚙️ Configuration Overview

The OMCP Python Sandbox uses environment-based configuration with sensible defaults. Configuration is loaded from environment variables and can be customized for different deployment scenarios.

## 🔧 Environment Variables

### Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SANDBOX_TIMEOUT` | `int` | `300` | Sandbox timeout in seconds |
| `MAX_SANDBOXES` | `int` | `10` | Maximum number of concurrent sandboxes |
| `DOCKER_IMAGE` | `str` | `fastomop/sandbox:python-3.11-slim` | Base Docker image for sandboxes |
| `SANDBOX_BASE_URL` | `str` | `None` | Base URL for sandbox services (optional) |
| `DEBUG` | `bool` | `false` | Enable debug mode |
| `LOG_LEVEL` | `str` | `INFO` | Logging level |
| `SANDBOX_ALLOW_HOST_GATEWAY` | `bool` | `false` | Allow `host.docker.internal` mapping |
| `SANDBOX_READ_ONLY` | `bool` | `true` | Run sandboxes with read-only root filesystem |
| `SANDBOX_NETWORK` | `str` | `None` | Attach sandboxes to a Docker network (`auto` uses compose network) |
| `ALLOW_UNSAFE_SQL` | `bool` | `false` | Allow raw `WHERE` clauses in `query_omop_table` |
| `DB_HOST` | `str` | `db` | Postgres host for OMOP tools |
| `DB_PORT` | `int` | `5432` | Postgres port |
| `DB_USER` | `str` | `omcp` | Postgres user |
| `DB_PASSWORD` | `str` | `postgres` | Postgres password |
| `DB_NAME` | `str` | `omcp` | Postgres database |

### Docker Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCKER_HOST` | `str` | `unix://var/run/docker.sock` | Docker daemon connection URL |
| `DOCKER_TLS_VERIFY` | `bool` | `false` | Enable Docker TLS verification |
| `DOCKER_CERT_PATH` | `str` | `None` | Path to Docker certificates |

### Docker SDK Notes

The Docker SDK respects standard Docker environment variables such as `DOCKER_HOST`,
`DOCKER_TLS_VERIFY`, and `DOCKER_CERT_PATH`.

## 📝 Configuration File

### Environment File Template

Create a `.env` file in the project root with your configuration:

```env
# Core Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=10
DOCKER_IMAGE=fastomop/sandbox:python-3.11-slim
DEBUG=false
LOG_LEVEL=INFO

# Docker Configuration
DOCKER_HOST=unix://var/run/docker.sock
DOCKER_TLS_VERIFY=false

# Sandbox Runtime
SANDBOX_ALLOW_HOST_GATEWAY=false
SANDBOX_READ_ONLY=true
# SANDBOX_NETWORK=auto
ALLOW_UNSAFE_SQL=false

# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_USER=omcp
DB_PASSWORD=postgres
DB_NAME=omcp

# Optional: Sandbox Services
SANDBOX_BASE_URL=http://localhost:8080
```

### Sample Environment File

A `sample.env` file is provided in the project root:

```env
# Sandbox Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=10
DOCKER_IMAGE=fastomop/sandbox:python-3.11-slim

# Logging
DEBUG=false
LOG_LEVEL=INFO

# Sandbox Runtime
SANDBOX_ALLOW_HOST_GATEWAY=false
SANDBOX_READ_ONLY=true
```

## 🏗️ Configuration Implementation

### Configuration Class

The configuration is implemented using a dataclass in `src/omcp_py/config.py`:

```python
@dataclass
class SandboxConfig:
    """Configuration settings for sandbox behavior and limits."""
    sandbox_timeout: int
    max_sandboxes: int  
    docker_image: str
    sandbox_base_url: Optional[str]
    debug: bool
    log_level: str
    allow_host_gateway: bool
    sandbox_read_only: bool
    sandbox_network: Optional[str]
    allow_unsafe_sql: bool
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
```

### Configuration Loading

```python
def get_config() -> SandboxConfig:
    """Load and return configuration from environment variables."""
    return SandboxConfig(
        sandbox_timeout=int(os.getenv("SANDBOX_TIMEOUT", "300")),
        max_sandboxes=int(os.getenv("MAX_SANDBOXES", "10")),
        docker_image=os.getenv("DOCKER_IMAGE", "fastomop/sandbox:python-3.11-slim"),
        sandbox_base_url=os.getenv("SANDBOX_BASE_URL"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        allow_host_gateway=os.getenv("SANDBOX_ALLOW_HOST_GATEWAY", "false").lower() == "true",
        sandbox_read_only=os.getenv("SANDBOX_READ_ONLY", "true").lower() == "true",
        sandbox_network=os.getenv("SANDBOX_NETWORK") or None,
        allow_unsafe_sql=os.getenv("ALLOW_UNSAFE_SQL", "false").lower() == "true",
        db_host=os.getenv("DB_HOST", "db"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_user=os.getenv("DB_USER", "omcp"),
        db_password=os.getenv("DB_PASSWORD", "postgres"),
        db_name=os.getenv("DB_NAME", "omcp"),
    )
```

## 🔧 Configuration Options

### 1. Sandbox Timeout (`SANDBOX_TIMEOUT`)

**Purpose**: Controls how long sandboxes remain active before automatic cleanup

**Values**:
- **Minimum**: `60` seconds
- **Recommended**: `300` seconds (5 minutes)
- **Maximum**: `3600` seconds (1 hour)

**Usage**:
```bash
# Short timeout for testing
export SANDBOX_TIMEOUT=60

# Long timeout for complex analysis
export SANDBOX_TIMEOUT=1800
```

**Impact**:
- **Short Timeout**: Faster cleanup, less resource usage
- **Long Timeout**: Better for complex workflows, higher resource usage

### 2. Maximum Sandboxes (`MAX_SANDBOXES`)

**Purpose**: Limits the number of concurrent sandboxes

**Values**:
- **Minimum**: `1`
- **Recommended**: `10` (development), `50` (production)
- **Maximum**: `100` (depending on system resources)

**Usage**:
```bash
# Development environment
export MAX_SANDBOXES=5

# Production environment
export MAX_SANDBOXES=50
```

**Impact**:
- **Low Count**: Lower resource usage, potential queueing
- **High Count**: Higher resource usage, better concurrency

### 3. Docker Image (`DOCKER_IMAGE`)

**Purpose**: Specifies the base Docker image for sandboxes

**Options**:
- **`fastomop/sandbox:python-3.11-slim`** (default) - Project-provided sandbox image
- **`python:3.12-slim`** - Latest Python version
- **`python:3.10-slim`** - Older Python version
- **Custom images** - Your own base images

**Usage**:
```bash
# Use latest Python version
export DOCKER_IMAGE=python:3.12-slim

# Use custom image with pre-installed packages
export DOCKER_IMAGE=myorg/python-analytics:latest
```

**Considerations**:
- **Slim Images**: Smaller size, faster startup
- **Full Images**: More packages, slower startup
- **Custom Images**: Pre-installed dependencies, larger size

### 4. Debug Mode (`DEBUG`)

**Purpose**: Enables debug logging and additional information

**Values**:
- **`false`** (default) - Production mode
- **`true`** - Debug mode

**Usage**:
```bash
# Enable debug mode
export DEBUG=true
```

**Impact**:
- **Debug Mode**: More verbose logging, performance impact
- **Production Mode**: Minimal logging, better performance

### 5. Log Level (`LOG_LEVEL`)

**Purpose**: Controls the verbosity of logging

**Values**:
- **`DEBUG`** - Most verbose
- **`INFO`** (default) - Standard information
- **`WARNING`** - Warnings and errors only
- **`ERROR`** - Errors only

**Usage**:
```bash
# Verbose logging for development
export LOG_LEVEL=DEBUG

# Minimal logging for production
export LOG_LEVEL=WARNING
```

## 🔒 Security Configuration

Sandbox security defaults (network isolation, read-only filesystem, dropped capabilities) are enabled by default and can be adjusted via `SANDBOX_NETWORK`, `SANDBOX_ALLOW_HOST_GATEWAY`, and `SANDBOX_READ_ONLY`. Resource limits are currently set in code and can be adjusted by editing `SandboxManager.create_sandbox` if needed.

## 🐳 Docker Configuration

### Docker Host (`DOCKER_HOST`)

**Purpose**: Specifies how to connect to the Docker daemon

**Values**:
- **`unix://var/run/docker.sock`** (default) - Local Docker daemon
- **`tcp://host:port`** - Remote Docker daemon
- **`npipe:////./pipe/docker_engine`** - Windows named pipe

**Usage**:
```bash
# Connect to remote Docker daemon
export DOCKER_HOST=tcp://192.168.1.100:2376

# Use Docker Desktop on Windows
export DOCKER_HOST=npipe:////./pipe/docker_engine
```

### Docker TLS (`DOCKER_TLS_VERIFY`)

**Purpose**: Enables TLS verification for Docker connections

**Values**:
- **`false`** (default) - No TLS verification
- **`true`** - Enable TLS verification

**Usage**:
```bash
# Enable TLS for secure Docker connections
export DOCKER_TLS_VERIFY=true
export DOCKER_CERT_PATH=/path/to/certs
```

## 📊 Performance Tuning

### Resource Optimization

**For High Concurrency**:
```bash
# Increase sandbox limit
export MAX_SANDBOXES=50

# Shorter timeout for faster cleanup
export SANDBOX_TIMEOUT=180
```

**For Heavy Computation**:
```bash
# Fewer sandboxes with more resources
export MAX_SANDBOXES=5

# Longer timeout for complex tasks
export SANDBOX_TIMEOUT=600
```

### Logging Optimization

**For Production**:
```bash
# Minimal logging
export LOG_LEVEL=WARNING
export DEBUG=false
```

**For Development**:
```bash
# Verbose logging
export LOG_LEVEL=DEBUG
export DEBUG=true
```

## 🏥 OMOP CDM Configuration

### Database Connection

For OMOP CDM integration, configure database connections in your code:

```python
# Example: OMOP CDM connection configuration
OMOP_DB_URL = "postgresql://user:pass@host:port/omop_cdm"
OMOP_DB_POOL_SIZE = 10
OMOP_DB_MAX_OVERFLOW = 20
```

### Clinical Data Security

```bash
# Enhanced security for clinical data
export SANDBOX_TIMEOUT=1800
export SANDBOX_READ_ONLY=true
export SANDBOX_NETWORK=auto
export LOG_LEVEL=INFO
```

## 🔧 Configuration Validation

### Validation Rules

The configuration system validates all inputs:

```python
def validate_config(config: SandboxConfig) -> bool:
    """Validate configuration values."""
    if config.sandbox_timeout < 60:
        raise ValueError("SANDBOX_TIMEOUT must be at least 60 seconds")
    
    if config.max_sandboxes < 1:
        raise ValueError("MAX_SANDBOXES must be at least 1")
    
    if config.max_sandboxes > 100:
        raise ValueError("MAX_SANDBOXES cannot exceed 100")
    
    return True
```

### Configuration Testing

Test your configuration:

```bash
# Test configuration loading
python -c "
from omcp_py.config import get_config
config = get_config()
print(f'Sandbox timeout: {config.sandbox_timeout}')
print(f'Max sandboxes: {config.max_sandboxes}')
print(f'Docker image: {config.docker_image}')
"
```

## 🚀 Deployment Configurations

### Development Environment

```bash
# Development configuration
export SANDBOX_TIMEOUT=300
export MAX_SANDBOXES=5
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Production Environment

```bash
# Production configuration
export SANDBOX_TIMEOUT=600
export MAX_SANDBOXES=50
export DEBUG=false
export LOG_LEVEL=WARNING
```

### Testing Environment

```bash
# Testing configuration
export SANDBOX_TIMEOUT=60
export MAX_SANDBOXES=2
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 🔍 Configuration Monitoring

### Configuration Logging

The system logs configuration on startup:

```
2024-01-01 12:00:00 - omcp_py.config - INFO - Configuration loaded:
  SANDBOX_TIMEOUT=300
  MAX_SANDBOXES=10
  DOCKER_IMAGE=fastomop/sandbox:python-3.11-slim
  DEBUG=false
  LOG_LEVEL=INFO
```

### Configuration Health Check

Monitor configuration health:

```python
# Configuration health check
def check_config_health():
    config = get_config()
    
    # Check Docker connectivity
    try:
        client = docker.DockerClient(base_url=os.getenv("DOCKER_HOST", "unix://var/run/docker.sock"))
        client.ping()
        print("✓ Docker connectivity: OK")
    except Exception as e:
        print(f"✗ Docker connectivity: {e}")
    
    # Check resource availability
    if config.max_sandboxes > 50:
        print("⚠ High sandbox limit may impact performance")
    
    print(f"✓ Configuration validation: OK")
```

## 🔄 Configuration Updates

### Runtime Configuration

Configuration is loaded at startup. To apply changes:

1. **Update environment variables**
2. **Restart the server**
3. **Verify configuration**

```bash
# Update configuration
export MAX_SANDBOXES=20

# Restart server
pkill -f "python src/omcp_py/main.py"
python src/omcp_py/main.py

# Verify changes
python -c "from omcp_py.config import get_config; print(get_config().max_sandboxes)"
```

### Configuration Persistence

For persistent configuration:

## Recent changes (2025-09-03)

Quick updates made to aid local development:

- Database connection settings are now centralized in `src/omcp_py/config.py`. The server reads `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` from environment variables or `.env`.
- A developer convenience image was added: an imported Postgres filesystem tar in `docker/images/postgres.tar` that was imported as `fastomop/postgres:from-tar`. This is intended for local development; for production use the official Postgres image.


1. **Update `.env` file**
2. **Use system environment variables**
3. **Use container environment variables**

```bash
# Persistent configuration in .env
echo "MAX_SANDBOXES=20" >> .env

# System environment variable
echo 'export MAX_SANDBOXES=20' >> ~/.bashrc
source ~/.bashrc
```

---

*This document provides comprehensive configuration information. For deployment details, see [Deployment Guide](deployment.md).* 
