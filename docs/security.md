# Security Model

This document provides comprehensive information about the security architecture, threat model, and security measures implemented in the OMCP Python Sandbox.

## 🔒 Security Overview

The OMCP Python Sandbox implements a multi-layered security architecture designed to provide secure, isolated Python code execution while protecting the host system and other sandboxes.

## 🛡️ Security Architecture

### Defense in Depth

The security model follows a defense-in-depth approach with multiple security layers:

1.  **Static Analysis Layer (Pre-Execution)**
2.  **Container Isolation Layer (Execution)**
3.  **Host Execution-Control Layer (Supervision)**
4.  **Filesystem Security Layer (Storage)**
5.  **Capabilities Layer (Kernel)**

### 1. Static Analysis Layer (New)

Before any code reaches the container, it passes through the **Code Validator**.

-   **Component**: `src/omcp_py/security/code_validator.py`
-   **Method**: AST (Abstract Syntax Tree) parsing.
-   **Checks**:
    -   Blocks dangerous imports: `os`, `sys`, `subprocess`, `socket`, `requests`, etc.
    -   Blocks dangerous built-ins: `exec`, `eval`, `compile`, `open`.
-   **Effect**: Prevents trivial misuse before execution.
-   **Boundary**: AST validation is bypassable and is not a security boundary.
    Isolation must remain effective even when validation misses malicious code.

### 2. Container Isolation Layer

If code passes validation, it runs in a locked-down Docker container.

-   **Network Isolation (Default)**: `network_mode="none"`
    -   The container has **no network interface** other than loopback. It cannot access the internet or the host network.
    -   Network access is never inferred from detected Compose services.
    -   To opt in, set `SANDBOX_NETWORK` to a dedicated restricted network.
        Host and container-shared network modes are forbidden.
-   **User Isolation**: `user="sandboxuser"` (UID 1000)
    -   Processes run as a non-root user. Even if a breakout occurs, the attacker has limited permissions on the host.
-   **Resource Limits**:
    -   `mem_limit`: Hard cap on memory usage.
    -   `cpu_quota`: CPU throttling to prevent DoS.
    -   `pids_limit`: Prevents fork bombs.

### 3. Host Execution-Control Layer

-   **Hard Deadline**: A host-side supervisor terminates and destroys a
    sandbox that exceeds the configured deadline. Guest Python cannot cancel
    this deadline by changing signal handlers.
-   **Output Budget**: Stdout and stderr are streamed into a bounded buffer.
    Exceeding the budget destroys the sandbox rather than buffering arbitrary
    output in server memory.
-   **Execution Serialization**: Only one execution can run in a sandbox at a
    time, preventing cross-run process and environment interference.

### 4. Filesystem Security Layer

-   **Read-Only Root (Default)**: `read_only=True`
    -   The entire root filesystem is mounted read-only. Hackers cannot install persistent malware or modify system binaries.
-   **Tmpfs Mounts**:
    -   Writable directories are limited to `tmpfs` (RAM disks) mounted at specific locations (e.g., `/tmp`). These are wiped instantly when the container stops.

### 5. Capabilities Layer

-   **Dropped Capabilities**: `cap_drop=["ALL"]`
    -   All Linux capabilities (like `CAP_NET_ADMIN`, `CAP_SYS_ADMIN`) are dropped. This prevents most kernel exploit vectors.
-   **No Privilege Escalation**: `security_opt=["no-new-privileges"]`
    -   Prevents setuid binaries from granting root access.

## 🎯 Threat Model & Mitigations

| Threat | Mitigation |
|--------|------------|
| **Malicious Imports** | Blocked by `CodeValidator` (AST analysis). |
| **Logic Bombs / Loops** | Host-enforced deadline followed by sandbox destruction. |
| **Output Flooding** | Bounded streaming capture followed by sandbox destruction. |
| **Fork Bombs** | Mitigated by `pids_limit` in Docker config. |
| **Network Scanning** | Prevented by `network_mode="none"`. |
| **File Tampering** | Prevented by Read-only filesystem. |
| **Credential Theft** | Requires separate least-privilege DB roles; environment injection alone does not prevent theft by code in the same container. |
| **Package Supply Chain** | Installation disabled by default; optional exact allowlist, binary-only and no-dependency policy. |

## 🔧 Local Execution Guard

Local (non-sandbox) execution is disabled by default. If you use the legacy `RunPythonTool`, set `OMCP_ALLOW_LOCAL_EXECUTION=true` to opt in.

## 🔧 Security Measures for OMOP

When dealing with healthcare data (OMOP):

-   **Credential Injection**: Database passwords are not embedded in generated
    code strings, but environment injection does not isolate credentials from
    other code in the same container. Production deployments should move
    trusted OMOP operations behind a separate service and use least-privilege,
    short-lived credentials.
-   **Fast Path Security**: Direct query tools enforce read-only SQL policy,
    bounded results, and parameterised table filters. Production deployments
    must also use a read-only database role and database statement timeouts.
