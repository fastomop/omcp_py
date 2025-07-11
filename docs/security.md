# Security Model

This document provides comprehensive information about the security architecture, threat model, and security measures implemented in the OMCP Python Sandbox.

## 🔒 Security Overview

The OMCP Python Sandbox implements a multi-layered security architecture designed to provide secure, isolated Python code execution while protecting the host system and other sandboxes.

## 🛡️ Security Architecture

### Defense in Depth

The security model follows a defense-in-depth approach with multiple security layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Protocol Layer                       │
│  - Input validation                                             │
│  - Parameter sanitization                                       │
│  - Command escaping                                             │
│  - Type checking                                                │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Container Isolation Layer                  │
│  - Network isolation (network_mode="none")                     │
│  - Resource limits (memory, CPU)                               │
│  - User isolation (UID 1000)                                   │
│  - Process isolation                                            │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Filesystem Security Layer                  │
│  - Read-only filesystem                                         │
│  - Temporary mounts (tmpfs)                                     │
│  - No persistent storage                                        │
│  - Size limits on temporary storage                             │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Capability Security Layer                  │
│  - All capabilities dropped                                     │
│  - No privilege escalation                                      │
│  - Restricted system calls                                      │
│  - Security options                                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Threat Model

### Identified Threats

1. **Code Injection Attacks**
   - **Threat**: Malicious code execution
   - **Mitigation**: Input validation, command escaping, container isolation

2. **Resource Exhaustion**
   - **Threat**: Denial of service through resource consumption
   - **Mitigation**: Memory and CPU limits, sandbox count limits

3. **Network Attacks**
   - **Threat**: Network-based attacks or data exfiltration
   - **Mitigation**: Network isolation, no network access

4. **Privilege Escalation**
   - **Threat**: Gaining elevated privileges
   - **Mitigation**: Non-root user, capability dropping, security options

5. **Data Exfiltration**
   - **Threat**: Unauthorized data access or theft
   - **Mitigation**: Read-only filesystem, temporary storage only

6. **Persistence Attacks**
   - **Threat**: Maintaining presence after execution
   - **Mitigation**: Auto-removal of containers, no persistent storage

## 🔧 Security Measures

### 1. Container Security

#### Network Isolation
```python
# No network access for security
network_mode="none"
```
- **Purpose**: Prevents network-based attacks
- **Implementation**: Containers run without network access
- **Benefits**: Complete network isolation

#### Resource Limits
```python
# Memory and CPU limits
mem_limit="512m"
cpu_period=100000
cpu_quota=50000  # 50% of one core
```
- **Purpose**: Prevents resource exhaustion
- **Implementation**: Hard limits on memory and CPU usage
- **Benefits**: Predictable resource usage

#### User Isolation
```python
# Non-root user execution
user=1000
```
- **Purpose**: Prevents privilege escalation
- **Implementation**: Containers run as non-root user
- **Benefits**: Reduced attack surface

### 2. Filesystem Security

#### Read-only Filesystem
```python
# Read-only filesystem
read_only=True
```
- **Purpose**: Prevents file system modifications
- **Implementation**: Container filesystem is read-only
- **Benefits**: No persistent changes possible

#### Temporary Filesystem
```python
# Temporary filesystem mounts
tmpfs={
    "/tmp": "rw,noexec,nosuid,size=100M",
    "/sandbox": "rw,noexec,nosuid,size=500M"
}
```
- **Purpose**: Provides limited writable space
- **Implementation**: Temporary filesystem mounts with size limits
- **Benefits**: Controlled temporary storage

### 3. Capability Security

#### Capability Dropping
```python
# Drop all Linux capabilities
cap_drop=["ALL"]
```
- **Purpose**: Removes unnecessary privileges
- **Implementation**: All Linux capabilities are dropped
- **Benefits**: Minimal privilege execution

#### Security Options
```python
# Prevent privilege escalation
security_opt=["no-new-privileges"]
```
- **Purpose**: Prevents privilege escalation
- **Implementation**: Security options prevent privilege changes
- **Benefits**: Stable privilege level

### 4. Input Validation

#### Command Escaping
```python
# Escape commands for shell safety
from shlex import quote
escaped_package = quote(package.strip())
```
- **Purpose**: Prevents command injection
- **Implementation**: Proper command escaping
- **Benefits**: Safe command execution

#### Parameter Validation
```python
# Validate input parameters
if not code or not code.strip():
    return {"success": False, "error": "Code cannot be empty"}
```
- **Purpose**: Ensures valid input
- **Implementation**: Comprehensive input validation
- **Benefits**: Prevents invalid operations

### 5. Auto-cleanup

#### Container Removal
```python
# Auto-remove when stopped
remove=True
```
- **Purpose**: Prevents persistence
- **Implementation**: Containers are automatically removed
- **Benefits**: No lingering containers

#### Timeout-based Cleanup
```python
def _cleanup_old_sandboxes(self):
    """Remove sandboxes that haven't been used within timeout period."""
    now = datetime.now()
    to_remove = []
    
    for sandbox_id, sandbox in self.sandboxes.items():
        if now - sandbox["last_used"] > timedelta(seconds=self.config.sandbox_timeout):
            to_remove.append(sandbox_id)
    
    for sandbox_id in to_remove:
        self.remove_sandbox(sandbox_id)
```
- **Purpose**: Automatic cleanup of inactive sandboxes
- **Implementation**: Timeout-based cleanup mechanism
- **Benefits**: Resource management

## 🔍 Security Monitoring

### Logging and Auditing

#### Security Event Logging
```python
# Log security events
logger.info(f"Created new sandbox {sandbox_id}")
logger.error(f"Failed to create sandbox: {e}")
```
- **Purpose**: Track security events
- **Implementation**: Comprehensive logging
- **Benefits**: Audit trail

#### Error Handling
```python
try:
    # Security-sensitive operation
    result = perform_operation()
except Exception as e:
    logger.error(f"Security error: {e}")
    return {"success": False, "error": str(e)}
```
- **Purpose**: Handle security errors gracefully
- **Implementation**: Comprehensive error handling
- **Benefits**: Secure error responses

### Security Metrics

#### Resource Usage Monitoring
- **Memory Usage**: Track memory consumption per sandbox
- **CPU Usage**: Monitor CPU utilization
- **Sandbox Count**: Track active sandbox count
- **Cleanup Events**: Monitor cleanup operations

#### Security Event Tracking
- **Failed Creations**: Track failed sandbox creations
- **Execution Errors**: Monitor code execution failures
- **Timeout Events**: Track sandbox timeouts
- **Force Removals**: Monitor forced sandbox removals

## 🏥 Healthcare Data Security

### HIPAA Compliance

For OMOP CDM and healthcare data analysis:

#### Data Privacy
- **No Persistent Storage**: Data cannot be stored permanently
- **Temporary Processing**: Data exists only during execution
- **Audit Trails**: Complete logging of all operations

#### Access Controls
- **Container Isolation**: Complete isolation between sandboxes
- **User Isolation**: Non-root execution
- **Network Isolation**: No external network access

#### Data Minimization
- **Parameterized Queries**: Use parameterized database queries
- **Minimal Data Access**: Access only necessary data
- **Secure Connections**: Encrypted database connections

### Clinical Data Best Practices

```python
# Example: Secure OMOP CDM query
def secure_clinical_query(patient_id: int):
    # Use parameterized query
    query = """
    SELECT person_id, condition_concept_id, condition_start_date
    FROM condition_occurrence
    WHERE person_id = %s
    """
    
    # Execute with parameters
    result = engine.execute(query, (patient_id,))
    
    # Log access for audit
    logger.info(f"Clinical data accessed for patient {patient_id}")
    
    return result
```

## 🔧 Security Configuration

### Security Environment Variables

```bash
# Security configuration
export SANDBOX_MEMORY_LIMIT=512m
export SANDBOX_CPU_LIMIT=50
export SANDBOX_USER_ID=1000
export SANDBOX_TIMEOUT=300
export MAX_SANDBOXES=10
```

### Security Hardening

#### Enhanced Security Mode
```bash
# Enhanced security configuration
export SANDBOX_MEMORY_LIMIT=256m
export SANDBOX_CPU_LIMIT=25
export SANDBOX_TIMEOUT=180
export MAX_SANDBOXES=5
```

#### Production Security
```bash
# Production security settings
export SANDBOX_MEMORY_LIMIT=1g
export SANDBOX_CPU_LIMIT=75
export SANDBOX_TIMEOUT=600
export MAX_SANDBOXES=50
export LOG_LEVEL=WARNING
```

## 🧪 Security Testing

### Security Test Scenarios

#### Code Injection Tests
```python
# Test command injection prevention
malicious_code = "'; rm -rf /; #"
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code=malicious_code
)
assert result["success"] == False
```

#### Resource Exhaustion Tests
```python
# Test memory limit enforcement
memory_hog = "data = 'x' * (1024 * 1024 * 1024)"  # 1GB
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code=memory_hog
)
assert result["success"] == False
```

#### Network Isolation Tests
```python
# Test network isolation
network_test = """
import requests
try:
    response = requests.get('http://google.com')
    print('Network access available')
except:
    print('Network access blocked')
"""
result = await mcp.execute_python_code(
    sandbox_id=sandbox_id,
    code=network_test
)
assert "Network access blocked" in result["output"]
```

### Security Validation

#### Container Security Check
```python
def validate_container_security(container):
    """Validate container security settings."""
    assert container.attrs['Config']['User'] == '1000'
    assert container.attrs['HostConfig']['NetworkMode'] == 'none'
    assert container.attrs['HostConfig']['Memory'] == 536870912  # 512MB
    assert container.attrs['HostConfig']['ReadonlyRootfs'] == True
```

## 🚨 Incident Response

### Security Incident Handling

#### Detection
- **Log Monitoring**: Monitor logs for security events
- **Resource Monitoring**: Track resource usage anomalies
- **Error Monitoring**: Monitor security-related errors

#### Response
1. **Immediate Action**: Stop affected sandboxes
2. **Investigation**: Analyze logs and events
3. **Containment**: Prevent further impact
4. **Recovery**: Restore normal operations
5. **Documentation**: Document incident and response

#### Prevention
- **Regular Updates**: Keep dependencies updated
- **Security Audits**: Regular security reviews
- **Monitoring**: Continuous security monitoring
- **Training**: Security awareness training

## 📋 Security Checklist

### Deployment Security Checklist

- [ ] **Container Security**
  - [ ] Network isolation enabled
  - [ ] Resource limits configured
  - [ ] Non-root user execution
  - [ ] Read-only filesystem

- [ ] **Input Validation**
  - [ ] Command escaping implemented
  - [ ] Parameter validation active
  - [ ] Type checking enabled

- [ ] **Monitoring**
  - [ ] Security logging enabled
  - [ ] Resource monitoring active
  - [ ] Error tracking implemented

- [ ] **Configuration**
  - [ ] Security settings configured
  - [ ] Timeout values set
  - [ ] Resource limits defined

### Healthcare Data Security Checklist

- [ ] **Data Privacy**
  - [ ] No persistent storage
  - [ ] Audit trails enabled
  - [ ] Data minimization practiced

- [ ] **Access Controls**
  - [ ] Container isolation verified
  - [ ] User isolation confirmed
  - [ ] Network isolation tested

- [ ] **Compliance**
  - [ ] HIPAA requirements met
  - [ ] Audit logging enabled
  - [ ] Security policies documented

## 🔮 Future Security Enhancements

### Planned Security Improvements

1. **Advanced Monitoring**
   - Real-time security monitoring
   - Anomaly detection
   - Security metrics dashboard

2. **Enhanced Isolation**
   - Additional security layers
   - Advanced container security
   - Hardware-based isolation

3. **Compliance Features**
   - Automated compliance checking
   - Regulatory reporting
   - Audit automation

4. **Threat Intelligence**
   - Threat detection
   - Security updates
   - Vulnerability scanning

---

*This document provides comprehensive security information. For implementation details, see [Implementation Details](implementation.md).* 