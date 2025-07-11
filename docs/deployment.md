# Deployment Guide

This document provides comprehensive guidance for deploying the OMCP Python Sandbox in production environments, including configuration, monitoring, and operational procedures.

## 🚀 Deployment Overview

The OMCP Python Sandbox can be deployed in various environments, from single-server setups to distributed, high-availability configurations.

## 🏗️ Deployment Architectures

### 1. Single Server Deployment

**Use Case**: Development, testing, or small-scale production

```
┌─────────────────────────────────────────────────────────┐
│                    Single Server                        │
│  ┌─────────────────┐  ┌─────────────────┐              │
│  │   MCP Server    │  │  Docker Engine  │              │
│  │                 │  │                 │              │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │              │
│  │ │ FastMCP     │ │  │ │ Container 1 │ │              │
│  │ │ Sandbox Mgr │ │  │ │ Container 2 │ │              │
│  │ └─────────────┘ │  │ │ Container N │ │              │
│  └─────────────────┘  │ └─────────────┘ │              │
│                       └─────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 2. Multi-Server Deployment

**Use Case**: High-availability production environments

```
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
        │  Server 1     │ │  Server 2     │ │  Server N     │
        │               │ │               │ │               │
        │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │
        │ │ MCP Server│ │ │ │ MCP Server│ │ │ │ MCP Server│ │
        │ │ Docker    │ │ │ │ Docker    │ │ │ │ Docker    │ │
        │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │
        └───────────────┘ └───────────────┘ └───────────────┘
```

### 3. Containerized Deployment

**Use Case**: Container orchestration environments

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   MCP Server    │  │   MCP Server    │  │   MCP Server    │  │
│  │   Pod           │  │   Pod           │  │   Pod           │  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │ FastMCP     │ │  │ │ FastMCP     │ │  │ │ FastMCP     │ │  │
│  │ │ Sandbox Mgr │ │  │ │ Sandbox Mgr │ │  │ │ Sandbox Mgr │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Production Configuration

### Environment Variables

Create a production `.env` file:

```env
# Production Configuration
SANDBOX_TIMEOUT=600
MAX_SANDBOXES=50
DOCKER_IMAGE=python:3.11-slim
DEBUG=false
LOG_LEVEL=WARNING

# Security Configuration
SANDBOX_MEMORY_LIMIT=1g
SANDBOX_CPU_LIMIT=75
SANDBOX_USER_ID=1000

# Docker Configuration
DOCKER_HOST=unix://var/run/docker.sock
DOCKER_TLS_VERIFY=false

# Optional: Monitoring
SANDBOX_BASE_URL=http://localhost:8080
```

### System Requirements

#### Minimum Requirements
- **CPU**: 4 cores
- **Memory**: 8GB RAM
- **Storage**: 20GB available space
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, etc.)

#### Recommended Requirements
- **CPU**: 8+ cores
- **Memory**: 16GB+ RAM
- **Storage**: 50GB+ available space
- **OS**: Linux with Docker support

#### High-Performance Requirements
- **CPU**: 16+ cores
- **Memory**: 32GB+ RAM
- **Storage**: 100GB+ available space
- **Network**: High-speed network connectivity

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -u 1000 appuser

# Copy application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -e .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to application user
USER appuser

# Expose port for monitoring
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import omcp_py; print('Health check passed')" || exit 1

# Start the server
CMD ["python", "src/omcp_py/main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  omcp-sandbox:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SANDBOX_TIMEOUT=600
      - MAX_SANDBOXES=50
      - DOCKER_IMAGE=python:3.11-slim
      - DEBUG=false
      - LOG_LEVEL=WARNING
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import omcp_py; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Monitoring stack
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana-storage:
```

## ☸️ Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omcp-sandbox
  labels:
    app: omcp-sandbox
spec:
  replicas: 3
  selector:
    matchLabels:
      app: omcp-sandbox
  template:
    metadata:
      labels:
        app: omcp-sandbox
    spec:
      containers:
      - name: omcp-sandbox
        image: omcp-sandbox:latest
        ports:
        - containerPort: 8080
        env:
        - name: SANDBOX_TIMEOUT
          value: "600"
        - name: MAX_SANDBOXES
          value: "50"
        - name: DOCKER_IMAGE
          value: "python:3.11-slim"
        - name: DEBUG
          value: "false"
        - name: LOG_LEVEL
          value: "WARNING"
        volumeMounts:
        - name: docker-sock
          mountPath: /var/run/docker.sock
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import omcp_py; print('Liveness check passed')"
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import omcp_py; print('Readiness check passed')"
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: docker-sock
        hostPath:
          path: /var/run/docker.sock
---
apiVersion: v1
kind: Service
metadata:
  name: omcp-sandbox-service
spec:
  selector:
    app: omcp-sandbox
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

## 📊 Monitoring and Observability

### Health Checks

#### Application Health Check

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
        
        # Check resource usage
        import psutil
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        return {
            "status": "healthy",
            "docker_connected": True,
            "active_sandboxes": active_sandboxes,
            "memory_usage_percent": memory_usage,
            "cpu_usage_percent": cpu_usage,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

#### Docker Health Check

```bash
#!/bin/bash
# docker-health-check.sh

# Check Docker daemon
if ! docker ps > /dev/null 2>&1; then
    echo "Docker daemon not accessible"
    exit 1
fi

# Check container creation
if ! docker run --rm --network none --memory 512m python:3.11-slim echo "test" > /dev/null 2>&1; then
    echo "Container creation failed"
    exit 1
fi

echo "Docker health check passed"
exit 0
```

### Metrics Collection

#### Prometheus Metrics

```python
# Metrics collection
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Metrics
sandbox_created = Counter('sandbox_created_total', 'Total sandboxes created')
sandbox_removed = Counter('sandbox_removed_total', 'Total sandboxes removed')
code_executions = Counter('code_executions_total', 'Total code executions')
execution_duration = Histogram('code_execution_duration_seconds', 'Code execution duration')
active_sandboxes = Gauge('active_sandboxes', 'Number of active sandboxes')
memory_usage = Gauge('sandbox_memory_usage_bytes', 'Memory usage per sandbox')
cpu_usage = Gauge('sandbox_cpu_usage_percent', 'CPU usage per sandbox')

# Start metrics server
start_http_server(8000)
```

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'omcp-sandbox'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 5s
```

### Logging Configuration

#### Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'sandbox_id'):
            log_entry['sandbox_id'] = record.sandbox_id
        
        if hasattr(record, 'execution_time'):
            log_entry['execution_time_ms'] = record.execution_time
        
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/omcp-sandbox.log'),
        logging.StreamHandler()
    ]
)
```

## 🔄 Operational Procedures

### Startup Procedures

#### 1. Pre-deployment Checks

```bash
#!/bin/bash
# pre-deployment-checks.sh

echo "Running pre-deployment checks..."

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not installed"
    exit 1
fi

# Check Docker daemon
if ! docker ps > /dev/null 2>&1; then
    echo "ERROR: Docker daemon not running"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not installed"
    exit 1
fi

# Check dependencies
python3 -c "import docker, mcp" 2>/dev/null || {
    echo "ERROR: Required Python packages not installed"
    exit 1
}

# Check system resources
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
if [ $MEMORY_GB -lt 8 ]; then
    echo "WARNING: Less than 8GB RAM available"
fi

echo "Pre-deployment checks passed"
```

#### 2. Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting OMCP Sandbox deployment..."

# Load environment variables
source .env

# Install dependencies
echo "Installing dependencies..."
uv pip install -e .

# Start the server
echo "Starting server..."
python src/omcp_py/main.py
```

### Monitoring Procedures

#### 1. Health Monitoring

```bash
#!/bin/bash
# health-monitor.sh

while true; do
    # Check application health
    if ! curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "WARNING: Application health check failed"
        # Send alert
        curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"OMCP Sandbox health check failed"}' \
            $SLACK_WEBHOOK_URL
    fi
    
    # Check Docker health
    if ! docker ps > /dev/null 2>&1; then
        echo "ERROR: Docker health check failed"
        # Restart Docker service
        sudo systemctl restart docker
    fi
    
    sleep 30
done
```

#### 2. Resource Monitoring

```bash
#!/bin/bash
# resource-monitor.sh

# Monitor memory usage
MEMORY_USAGE=$(free | awk '/Mem:/ {printf("%.1f", $3/$2 * 100.0)}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "WARNING: High memory usage: ${MEMORY_USAGE}%"
fi

# Monitor disk usage
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "WARNING: High disk usage: ${DISK_USAGE}%"
fi

# Monitor active sandboxes
ACTIVE_SANDBOXES=$(docker ps --filter "name=omcp-sandbox" --format "table {{.Names}}" | wc -l)
if [ $ACTIVE_SANDBOXES -gt 40 ]; then
    echo "WARNING: High number of active sandboxes: $ACTIVE_SANDBOXES"
fi
```

### Backup and Recovery

#### 1. Configuration Backup

```bash
#!/bin/bash
# backup-config.sh

BACKUP_DIR="/backup/omcp-sandbox"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration files
cp .env $BACKUP_DIR/env_$DATE
cp pyproject.toml $BACKUP_DIR/pyproject_$DATE.toml

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/omcp-sandbox.log

echo "Backup completed: $BACKUP_DIR"
```

#### 2. Recovery Procedures

```bash
#!/bin/bash
# recovery.sh

echo "Starting recovery procedures..."

# Stop the application
pkill -f "python src/omcp_py/main.py"

# Clean up containers
docker ps --filter "name=omcp-sandbox" -q | xargs docker stop
docker ps --filter "name=omcp-sandbox" -aq | xargs docker rm

# Restore configuration
cp /backup/omcp-sandbox/env_latest .env

# Restart the application
python src/omcp_py/main.py
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Docker Connection Issues

**Symptoms**: "Cannot connect to Docker daemon"

**Solutions**:
```bash
# Check Docker service
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker

# Check Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Resource Exhaustion

**Symptoms**: "Maximum number of sandboxes reached"

**Solutions**:
```bash
# Check active sandboxes
docker ps --filter "name=omcp-sandbox"

# Clean up inactive sandboxes
docker ps --filter "name=omcp-sandbox" --filter "status=exited" -q | xargs docker rm

# Increase limits in configuration
export MAX_SANDBOXES=100
```

#### 3. Memory Issues

**Symptoms**: "Out of memory" errors

**Solutions**:
```bash
# Check memory usage
free -h

# Reduce sandbox memory limits
export SANDBOX_MEMORY_LIMIT=256m

# Reduce concurrent sandboxes
export MAX_SANDBOXES=20
```

### Performance Tuning

#### 1. High Concurrency Tuning

```bash
# Optimize for high concurrency
export MAX_SANDBOXES=100
export SANDBOX_MEMORY_LIMIT=256m
export SANDBOX_CPU_LIMIT=25
export SANDBOX_TIMEOUT=180
```

#### 2. Heavy Computation Tuning

```bash
# Optimize for heavy computation
export MAX_SANDBOXES=10
export SANDBOX_MEMORY_LIMIT=2g
export SANDBOX_CPU_LIMIT=100
export SANDBOX_TIMEOUT=1800
```

## 📈 Scaling Strategies

### Horizontal Scaling

1. **Load Balancer**: Distribute requests across multiple servers
2. **Shared Storage**: Use shared storage for configuration
3. **Service Discovery**: Implement service discovery for dynamic scaling
4. **Health Checks**: Ensure load balancer health checks

### Vertical Scaling

1. **Resource Limits**: Increase memory and CPU limits
2. **Sandbox Count**: Increase maximum sandbox count
3. **Timeout Settings**: Adjust timeout values for workload
4. **Monitoring**: Monitor resource usage and adjust accordingly

---

*This document provides comprehensive deployment guidance. For configuration details, see [Configuration Guide](configuration.md).* 