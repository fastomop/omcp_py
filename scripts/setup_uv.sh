#!/usr/bin/env bash
set -euo pipefail

# Create uv-managed virtual environment and install dependencies
# Requires: uv installed on system (https://astral.sh/uv)

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Install from https://astral.sh/uv and re-run."
  exit 1
fi

# Create a venv managed by uv
uv venv .venv
# Activate and ensure pip is up to date
source .venv/bin/activate
python -m pip install --upgrade pip
# Install dependencies declared in pyproject (uv provides a pip shim, but we'll install with pip)
pip install -U \
  "mcp[cli]>=1.6.0" \
  httpx>=0.27.0 \
  flask>=3.0.0 \
  pydantic>=2.0.0 \
  docker>=7.0.0 \
  python-dotenv>=1.0.0 \
  SQLAlchemy>=2.0 \
  psycopg2-binary>=2.9 \
  fastmcp \
  pandas>=1.5.0 \
  duckdb>=0.8.0

echo "UV venv created at .venv and dependencies installed. Activate with: source .venv/bin/activate"
