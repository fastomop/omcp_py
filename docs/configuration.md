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
| `DOCKER_IMAGE` | `str` | `python:3.11-slim` | Base Docker image for sandboxes |
| `SANDBOX_BASE_URL` | `str` | `None` | Base URL for sandbox services (optional) |
| `DEBUG` | `bool` | `false` | Enable debug mode |
| `LOG_LEVEL` | `str` | `INFO` | Logging level |

### Docker Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCKER_HOST` | `str` | `unix://var/run/docker.sock` | Docker daemon connection URL |
| `DOCKER_TLS_VERIFY` | `bool` | `false` | Enable Docker TLS verification |
| `DOCKER_CERT_PATH` | `str` | `None` | Path to Docker certificates |

### Security Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SANDBOX_MEMORY_LIMIT` | `str` | `512m` | Memory limit per sandbox |
| `SANDBOX_CPU_LIMIT` | `int` | `50` | CPU limit percentage per sandbox |
| `SANDBOX_USER_ID` | `int` | `1000` | User ID for sandbox containers |
| `SANDBOX_TMPFS_SIZE` | `str` | `100M` | Temporary filesystem size |

## 📝 Configuration File

### Environment File Template

Create a `.env` file in the project root with your configuration:

```env
# Core Configuration
SANDBOX_TIMEOUT=300
MAX_SANDBOXES=10
DOCKER_IMAGE=python:3.11-slim
DEBUG=false
LOG_LEVEL=INFO

# Docker Configuration
DOCKER_HOST=unix://var/run/docker.sock
DOCKER_TLS_VERIFY=false

# Security Configuration
SANDBOX_MEMORY_LIMIT=512m
SANDBOX_CPU_LIMIT=50
SANDBOX_USER_ID=1000
SANDBOX_TMPFS_SIZE=100M

# Optional: Sandbox Services
SANDBOX_BASE_URL=http://localhost:8080
```

### Sample Environment File

A `sample.env` file is provided in the project root:

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
```

### Configuration Loading

```python
def get_config() -> SandboxConfig:
    """Load and return configuration from environment variables."""
    return SandboxConfig(
        sandbox_timeout=int(os.getenv("SANDBOX_TIMEOUT", "300")),
        max_sandboxes=int(os.getenv("MAX_SANDBOXES", "10")),
        docker_image=os.getenv("DOCKER_IMAGE", "python:3.11-slim"),
        sandbox_base_url=os.getenv("SANDBOX_BASE_URL"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO")
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
- **`python:3.11-slim`** (default) - Minimal Python image
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

### Memory Limits (`SANDBOX_MEMORY_LIMIT`)

**Purpose**: Limits memory usage per sandbox

**Values**:
- **Minimum**: `128m`
- **Recommended**: `512m`
- **Maximum**: `2g` (depending on system)

**Usage**:
```bash
# Conservative memory limit
export SANDBOX_MEMORY_LIMIT=256m

# Generous memory limit for data analysis
export SANDBOX_MEMORY_LIMIT=1g
```

### CPU Limits (`SANDBOX_CPU_LIMIT`)

**Purpose**: Limits CPU usage per sandbox

**Values**:
- **Minimum**: `10` (10% of one core)
- **Recommended**: `50` (50% of one core)
- **Maximum**: `100` (full core)

**Usage**:
```bash
# Conservative CPU limit
export SANDBOX_CPU_LIMIT=25

# Generous CPU limit for computation
export SANDBOX_CPU_LIMIT=75
```

### User ID (`SANDBOX_USER_ID`)

**Purpose**: Specifies the user ID for sandbox containers

**Values**:
- **Recommended**: `1000` (non-root user)
- **Custom**: Any non-root UID

**Usage**:
```bash
# Use custom user ID
export SANDBOX_USER_ID=2000
```

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

# Reduce memory per sandbox
export SANDBOX_MEMORY_LIMIT=256m

# Reduce CPU per sandbox
export SANDBOX_CPU_LIMIT=25

# Shorter timeout for faster cleanup
export SANDBOX_TIMEOUT=180
```

**For Heavy Computation**:
```bash
# Fewer sandboxes with more resources
export MAX_SANDBOXES=5

# More memory per sandbox
export SANDBOX_MEMORY_LIMIT=1g

# More CPU per sandbox
export SANDBOX_CPU_LIMIT=75

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
export SANDBOX_MEMORY_LIMIT=1g
export SANDBOX_TIMEOUT=1800
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
export SANDBOX_MEMORY_LIMIT=512m
export SANDBOX_CPU_LIMIT=50
```

### Production Environment

```bash
# Production configuration
export SANDBOX_TIMEOUT=600
export MAX_SANDBOXES=50
export DEBUG=false
export LOG_LEVEL=WARNING
export SANDBOX_MEMORY_LIMIT=1g
export SANDBOX_CPU_LIMIT=75
```

### Testing Environment

```bash
# Testing configuration
export SANDBOX_TIMEOUT=60
export MAX_SANDBOXES=2
export DEBUG=true
export LOG_LEVEL=DEBUG
export SANDBOX_MEMORY_LIMIT=256m
export SANDBOX_CPU_LIMIT=25
```

## 🔍 Configuration Monitoring

### Configuration Logging

The system logs configuration on startup:

```
2024-01-01 12:00:00 - omcp_py.config - INFO - Configuration loaded:
  SANDBOX_TIMEOUT=300
  MAX_SANDBOXES=10
  DOCKER_IMAGE=python:3.11-slim
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