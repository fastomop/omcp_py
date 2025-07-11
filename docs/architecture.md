# Architecture Overview

This document provides a comprehensive overview of the OMCP Python Sandbox architecture, including system design, component interactions, and architectural patterns.

## 🏗️ System Architecture

### High-Level Architecture

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

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MCP Client Layer                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   AI Agent      │  │   Web App       │  │   CLI Tool      │  │   MCP Inspector │   │
│  │                 │  │                 │  │                 │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ JSON-RPC over stdio
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FastMCP Server Layer                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              src/omcp_py/main.py                                   │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │ │
│  │  │ create_sandbox  │  │ list_sandboxes  │  │ remove_sandbox  │  │ execute_python  │ │ │
│  │  │                 │  │                 │  │                 │  │                 │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘ │ │
│  │  ┌─────────────────┐                                                               │ │
│  │  │ install_package │                                                               │ │
│  │  │                 │                                                               │ │
│  │  └─────────────────┘                                                               │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ Direct calls
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  Sandbox Manager Layer                                  │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                           src/omcp_py/sandbox_manager.py                           │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │ │
│  │  │ create_sandbox  │  │ remove_sandbox  │  │ execute_code    │  │ list_sandboxes  │ │ │
│  │  │                 │  │                 │  │                 │  │                 │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘ │ │
│  │  ┌─────────────────┐                                                               │ │
│  │  │ _cleanup_old_   │                                                               │ │
│  │  │ sandboxes       │                                                               │ │
│  │  └─────────────────┘                                                               │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ Docker API
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    Docker Engine Layer                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ Container 1     │  │ Container 2     │  │ Container 3     │  │ Container N     │   │
│  │ (Sandbox 1)     │  │ (Sandbox 2)     │  │ (Sandbox 3)     │  │ (Sandbox N)     │   │
│  │                 │  │                 │  │                 │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Component Details

### 1. MCP Client Layer

**Purpose**: External applications that need to execute Python code securely

**Components**:
- **AI Agents**: AI assistants requiring code execution capabilities
- **Web Applications**: Web-based tools and dashboards
- **CLI Tools**: Command-line utilities
- **MCP Inspector**: Web-based testing and debugging interface

**Protocol**: JSON-RPC over stdio (MCP specification)

**Key Features**:
- Standardized MCP protocol compliance
- Multiple client types supported
- Web-based debugging interface

### 2. FastMCP Server Layer

**Purpose**: MCP protocol implementation and tool orchestration

**Location**: `src/omcp_py/main.py`

**Key Components**:
- **FastMCP Instance**: Main server object using decorator-based tool definitions
- **Tool Decorators**: `@mcp.tool()` decorators for MCP tool definitions
- **Error Handling**: Comprehensive error handling and logging
- **Input Validation**: Parameter validation and sanitization

**Architecture Patterns**:
- **Decorator Pattern**: Tool definitions using `@mcp.tool()`
- **Singleton Pattern**: Single server instance
- **Factory Pattern**: Tool response creation

### 3. Sandbox Manager Layer

**Purpose**: Docker container lifecycle management

**Location**: `src/omcp_py/sandbox_manager.py`

**Key Components**:
- **Docker Client**: Connection to Docker daemon
- **Container Management**: Create, execute, and remove containers
- **Resource Tracking**: Sandbox metadata and usage tracking
- **Cleanup Logic**: Automatic removal of expired sandboxes

**Architecture Patterns**:
- **Singleton Pattern**: Single manager instance
- **Observer Pattern**: Automatic cleanup of expired sandboxes
- **Factory Pattern**: Container creation with consistent configuration

### 4. Docker Engine Layer

**Purpose**: Container isolation and execution

**Components**:
- **Python Containers**: Isolated Python execution environments
- **Security Restrictions**: Network isolation, resource limits, capability dropping
- **Temporary Filesystems**: Read-only with temporary mounts

**Security Features**:
- Network isolation (`network_mode="none"`)
- Resource limits (memory, CPU)
- User isolation (non-root)
- Filesystem security (read-only with tmpfs)
- Capability dropping (all capabilities removed)

## 🔄 Data Flow Architecture

### 1. Sandbox Creation Flow

```
MCP Client → FastMCP Server → Sandbox Manager → Docker Engine
     │              │              │              │
     │              │              │              ▼
     │              │              │        Container Created
     │              │              ▼
     │              │        Sandbox ID Generated
     │              ▼
     │        Success Response
     ▼
Sandbox ID Received
```

**Detailed Flow**:
1. **Client Request**: MCP client calls `create_sandbox()`
2. **Server Processing**: FastMCP server validates request
3. **Manager Delegation**: SandboxManager creates container
4. **Container Creation**: Docker engine creates isolated container
5. **ID Generation**: Unique UUID generated for sandbox
6. **Response**: Success response with sandbox ID

### 2. Code Execution Flow

```
MCP Client → FastMCP Server → Sandbox Manager → Docker Container
     │              │              │              │
     │              │              │              ▼
     │              │              │        Code Executed
     │              │              ▼
     │              │        Output Captured
     │              ▼
     │        Response Formatted
     ▼
Results Received
```

**Detailed Flow**:
1. **Client Request**: MCP client calls `execute_python_code()`
2. **Validation**: Server validates sandbox ID and code
3. **Execution**: SandboxManager executes code in container
4. **Output Capture**: stdout, stderr, and exit code captured
5. **Response**: Formatted response with results

### 3. Sandbox Cleanup Flow

```
Timer/Event → Sandbox Manager → Docker Engine
     │              │              │
     │              │              ▼
     │              │        Container Removed
     │              ▼
     │        Metadata Cleaned
     ▼
Cleanup Complete
```

**Detailed Flow**:
1. **Trigger**: Timer or manual cleanup request
2. **Expiration Check**: Find sandboxes exceeding timeout
3. **Container Removal**: Stop and remove Docker containers
4. **Metadata Cleanup**: Remove sandbox tracking data

## 🏛️ Architectural Patterns

### 1. Layered Architecture

**Benefits**:
- **Separation of Concerns**: Each layer has specific responsibilities
- **Maintainability**: Changes in one layer don't affect others
- **Testability**: Each layer can be tested independently
- **Scalability**: Layers can be scaled independently

**Layers**:
- **Presentation Layer**: MCP protocol handling
- **Business Logic Layer**: Sandbox management logic
- **Infrastructure Layer**: Docker container management

### 2. Microservices Architecture

**Characteristics**:
- **Containerized**: Each sandbox is a separate container
- **Isolated**: Complete isolation between sandboxes
- **Stateless**: Sandboxes don't maintain persistent state
- **Scalable**: Can scale number of sandboxes independently

### 3. Event-Driven Architecture

**Events**:
- **Sandbox Created**: New sandbox available
- **Code Executed**: Code execution completed
- **Sandbox Expired**: Sandbox timeout reached
- **Error Occurred**: Error in sandbox operation

### 4. Security-First Architecture

**Security Layers**:
- **Network Security**: No network access for containers
- **Resource Security**: Memory and CPU limits
- **Filesystem Security**: Read-only with temporary mounts
- **User Security**: Non-root user execution
- **Capability Security**: All Linux capabilities dropped

## 🔒 Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Protocol Layer                       │
│  - Input validation                                             │
│  - Parameter sanitization                                       │
│  - Command escaping                                             │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Container Isolation Layer                  │
│  - Network isolation (network_mode="none")                     │
│  - Resource limits (memory, CPU)                               │
│  - User isolation (UID 1000)                                   │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Filesystem Security Layer                  │
│  - Read-only filesystem                                         │
│  - Temporary mounts (tmpfs)                                     │
│  - No persistent storage                                        │
└─────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Capability Security Layer                  │
│  - All capabilities dropped                                     │
│  - No privilege escalation                                      │
│  - Restricted system calls                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Threat Model

**Threats Mitigated**:
1. **Code Injection**: Input validation and command escaping
2. **Resource Exhaustion**: Memory and CPU limits
3. **Network Attacks**: Network isolation
4. **Privilege Escalation**: Capability dropping and user isolation
5. **Data Exfiltration**: Read-only filesystem
6. **Persistence**: Auto-removal of containers

## 📊 Scalability Architecture

### Horizontal Scaling

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Server 1  │    │   MCP Server 2  │    │   MCP Server N  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Sandbox Mgr │ │    │ │ Sandbox Mgr │ │    │ │ Sandbox Mgr │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Docker Engine  │
                    │   (Shared)      │
                    └─────────────────┘
```

### Vertical Scaling

- **Container Limits**: Adjustable memory and CPU limits
- **Sandbox Count**: Configurable maximum sandbox count
- **Timeout Settings**: Adjustable sandbox timeout periods

## 🔄 State Management

### Stateless Design

**Characteristics**:
- **No Persistent State**: Sandboxes don't maintain state between executions
- **Ephemeral Containers**: Containers are created and destroyed as needed
- **Metadata Only**: Only sandbox metadata is maintained

### State Tracking

**Sandbox Metadata**:
```python
{
    "container": docker_container_object,
    "created_at": datetime,
    "last_used": datetime
}
```

**Configuration State**:
```python
{
    "sandbox_timeout": int,
    "max_sandboxes": int,
    "docker_image": str,
    "debug": bool,
    "log_level": str
}
```

## 🧪 Testing Architecture

### Testing Layers

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **End-to-End Tests**: Full system testing
4. **Security Tests**: Security measure validation

### Test Isolation

- **Container Testing**: Each test uses isolated containers
- **Mock Docker**: Docker API mocking for unit tests
- **Test Configuration**: Separate test configuration

## 🔮 Future Architecture Considerations

### Planned Enhancements

1. **Plugin Architecture**: Extensible tool system
2. **Database Integration**: Persistent metadata storage
3. **Load Balancing**: Multiple server instances
4. **Monitoring**: Metrics and observability

### Scalability Improvements

1. **Kubernetes Integration**: Container orchestration
2. **Service Mesh**: Inter-service communication
3. **Caching Layer**: Redis-based caching
4. **Message Queue**: Asynchronous processing

---

*This document provides the architectural overview. For implementation details, see [Implementation Details](implementation.md).* 