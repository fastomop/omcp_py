# OMCP Python Sandbox - Technical Documentation

Welcome to the technical documentation for the OMCP Python Sandbox project. This documentation provides comprehensive information about the codebase architecture, implementation details, and usage patterns.

## 📚 Documentation Structure

### Core Documentation
- **[Architecture Overview](architecture.md)** - High-level system architecture and design principles
- **[Codebase Structure](codebase-structure.md)** - Detailed breakdown of the codebase organization
- **[Implementation Details](implementation.md)** - Deep dive into key components and their implementation
- **[Security Model](security.md)** - Security architecture and threat mitigation strategies

### Usage Documentation
- **[API Reference](api-reference.md)** - Complete API documentation for all MCP tools
- **[Configuration Guide](configuration.md)** - Environment variables and configuration options
- **[Deployment Guide](deployment.md)** - Production deployment and operational considerations

### Development Documentation
- **[Development Setup](development.md)** - Setting up the development environment
- **[Testing Guide](testing.md)** - Testing strategies and test execution
- **[Contributing Guidelines](contributing.md)** - How to contribute to the project

## 🏗️ Project Overview

The OMCP Python Sandbox is a secure, Model Context Protocol (MCP) compliant Python code execution environment that provides isolated, containerized Python environments for safe code execution. Built with enterprise-grade security features, it enables AI agents and applications to execute Python code without compromising system security.

### Key Components

1. **FastMCP Server** (`src/omcp_py/main.py`) - Main MCP server implementation using FastMCP framework
2. **Sandbox Manager** (`src/omcp_py/sandbox_manager.py`) - Docker container lifecycle management
3. **Configuration System** (`src/omcp_py/config.py`) - Environment-based configuration management
4. **Security Layer** - Comprehensive security measures including container isolation and resource limits

### Architecture Highlights

- **Docker-based Isolation**: Each sandbox runs in a separate Docker container with enhanced security
- **MCP Compliance**: Full Model Context Protocol specification compliance
- **Resource Management**: Automatic cleanup and resource limits
- **Security First**: Network isolation, read-only filesystems, dropped capabilities
- **Healthcare Ready**: OMOP CDM integration for clinical data analysis

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/fastomop/omcp_py.git
cd omcp_py
uv pip install -e .
```

### Running the Server
```bash
python src/omcp_py/main.py
```

### Using MCP Inspector
```bash
npx @modelcontextprotocol/inspector python src/omcp_py/main.py
```

## 📋 Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture Overview](architecture.md) | System architecture, component interactions, and design patterns |
| [Codebase Structure](codebase-structure.md) | File organization, module structure, and code organization |
| [Implementation Details](implementation.md) | Detailed implementation of core components and algorithms |
| [Security Model](security.md) | Security architecture, threat model, and mitigation strategies |
| [API Reference](api-reference.md) | Complete API documentation for all MCP tools and endpoints |
| [Configuration Guide](configuration.md) | Environment variables, configuration options, and tuning |
| [Deployment Guide](deployment.md) | Production deployment, monitoring, and operational procedures |
| [Development Setup](development.md) | Development environment setup and workflow |
| [Testing Guide](testing.md) | Testing strategies, test execution, and quality assurance |
| [Contributing Guidelines](contributing.md) | How to contribute, code standards, and pull request process |

## 🔧 Technology Stack

- **Python 3.10+** - Core runtime and development language
- **FastMCP** - MCP server implementation framework
- **Docker** - Containerization and isolation
- **SQLAlchemy** - Database connectivity (for OMOP CDM)
- **Pydantic** - Data validation and settings management
- **Flask** - Web server capabilities (if needed)
- **uv** - Modern Python package management

## 🏥 OMOP CDM Integration

The project includes comprehensive support for OMOP Common Data Model (CDM) integration, enabling secure clinical data analysis through MCP agents. See the [OMOP CDM Integration Guide](omop-cdm-integration.md) for detailed information.

## 📞 Support

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: This comprehensive documentation suite

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

*This documentation is maintained by the OMCP Python Sandbox development team. For the latest updates, check the GitHub repository.* 