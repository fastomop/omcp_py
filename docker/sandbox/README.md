Prebuilt sandbox image

Build locally with:

```bash
# from repo root
docker build -t fastomop/sandbox:python-3.11-slim -f docker/sandbox/Dockerfile .
```

Then set `DOCKER_IMAGE` to `fastomop/sandbox:python-3.11-slim` in `.env` or export it before running the server:

```bash
export DOCKER_IMAGE=fastomop/sandbox:python-3.11-slim
PYTHONPATH=src python3 src/omcp_py/main.py
```

```

How to use locally (copy/paste)
1) Build the prebuilt sandbox image (from repo root)
```bash
docker build -t fastomop/sandbox:python-3.11-slim -f docker/sandbox/Dockerfile .
```

2) (Optional) Start `db` via docker compose if you want the Compose-managed DB
```bash
docker compose up -d db
```

3) Export image name (or set in .env) so server uses prebuilt sandbox image
```bash
export DOCKER_IMAGE=fastomop/sandbox:python-3.11-slim
```

4) Start the MCP server (foreground so you see logs)
```bash
PYTHONPATH=src python3 src/omcp_py/main.py
```

5) Create and test a sandbox quickly (run in separate shell)
```bash
PYTHONPATH=src python3 - <<'PY'
from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager
c = get_config()
sm = SandboxManager(c)
sid = sm.create_sandbox()
print('sandbox', sid)
print('python version:', sm.execute_code(sid, 'import sys; print(sys.version)'))
print('pip version:', sm.execute_code(sid, 'import subprocess,sys; print(subprocess.run([sys.executable, \"-m\", \"pip\", \"--version\"], capture_output=True, text=True).stdout)'))
sm.remove_sandbox(sid)
PY
```

6) Run the included local client smoke script (which uses the sandbox manager)
```bash
PYTHONPATH=src python3 scripts/local_client.py
```

