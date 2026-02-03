# Security Model

This document provides comprehensive information about the security architecture, threat model, and security measures implemented in the OMCP Python Sandbox.

## 🔒 Security Overview

The OMCP Python Sandbox implements a multi-layered security architecture designed to provide secure, isolated Python code execution while protecting the host system and other sandboxes.

## 🛡️ Security Architecture

### Defense in Depth

The security model follows a defense-in-depth approach with multiple security layers:

1.  **Static Analysis Layer (Pre-Execution)**
2.  **Container Isolation Layer (Execution)**
3.  **Filesystem Security Layer (Storage)**
4.  **Capabilities Layer (Kernel)**

### 1. Static Analysis Layer (New)

Before any code reaches the container, it passes through the **Code Validator**.

-   **Component**: `src/omcp_py/security/code_validator.py`
-   **Method**: AST (Abstract Syntax Tree) parsing.
-   **Checks**:
    -   Blocks dangerous imports: `os`, `sys`, `subprocess`, `socket`, `requests`, etc.
    -   Blocks dangerous built-ins: `exec`, `eval`, `compile`, `open`.
-   **Effect**: Prevents trivial breakout attempts and standard library misuse before they even start.

### 2. Container Isolation Layer

If code passes validation, it runs in a locked-down Docker container.

-   **Network Isolation (Default)**: `network_mode="none"`
    -   The container has **no network interface** other than loopback. It cannot access the internet or the host network.
    -   To opt into network access for database use, set `SANDBOX_NETWORK` (or `SANDBOX_NETWORK=auto` to attach to the detected compose network).
-   **User Isolation**: `user="sandboxuser"` (UID 1000)
    -   Processes run as a non-root user. Even if a breakout occurs, the attacker has limited permissions on the host.
-   **Resource Limits**:
    -   `mem_limit`: Hard cap on memory usage.
    -   `cpu_quota`: CPU throttling to prevent DoS.
    -   `pids_limit`: Prevents fork bombs.

### 3. Filesystem Security Layer

-   **Read-Only Root (Default)**: `read_only=True`
    -   The entire root filesystem is mounted read-only. Hackers cannot install persistent malware or modify system binaries.
-   **Tmpfs Mounts**:
    -   Writable directories are limited to `tmpfs` (RAM disks) mounted at specific locations (e.g., `/tmp`). These are wiped instantly when the container stops.

### 4. Capabilities Layer

-   **Dropped Capabilities**: `cap_drop=["ALL"]`
    -   All Linux capabilities (like `CAP_NET_ADMIN`, `CAP_SYS_ADMIN`) are dropped. This prevents most kernel exploit vectors.
-   **No Privilege Escalation**: `security_opt=["no-new-privileges"]`
    -   Prevents setuid binaries from granting root access.

## 🎯 Threat Model & Mitigations

| Threat | Mitigation |
|--------|------------|
| **Malicious Imports** | Blocked by `CodeValidator` (AST analysis). |
| **Logic Bombs / Loops** | Enforced by `timeout` command + container time limits. |
| **Fork Bombs** | Mitigated by `pids_limit` in Docker config. |
| **Network Scanning** | Prevented by `network_mode="none"`. |
| **File Tampering** | Prevented by Read-only filesystem. |
| **Credential Theft** | DB Credentials injected as Env Vars only at runtime, never stored on disk. |

## 🔧 Local Execution Guard

Local (non-sandbox) execution is disabled by default. If you use the legacy `RunPythonTool`, set `OMCP_ALLOW_LOCAL_EXECUTION=true` to opt in.

## 🔧 Security Measures for OMOP

When dealing with healthcare data (OMOP):

-   **Credential Injection**: Database passwords are NOT embedded in Python code strings. They are passed as environment variables (`OMOP_DB_PASSWORD`) to the container running the query.
-   **Fast Path Security**: The "Fast Path" (direct query) tool is intended for **read-only** operations. (Implementation note: In production, this should connect via a read-only database user).
    -   Raw `WHERE` clauses are disabled by default; use structured `filters` or set `ALLOW_UNSAFE_SQL=true` to opt in.
