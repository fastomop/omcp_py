#!/usr/bin/env bash
set -euo pipefail

# Stop and remove demo server log/process, bring down docker compose services used by demo
# Run from repo root

# Bring down compose services
docker compose down || true

# Remove any demo sandbox containers with name prefix 'omcp-sandbox-'
docker ps -a --filter "name=omcp-sandbox-" -q | xargs -r docker rm -f || true

# Remove the prebuilt sandbox image (optional)
if docker image inspect fastomop/sandbox:python-3.11-slim >/dev/null 2>&1; then
  docker image rm -f fastomop/sandbox:python-3.11-slim || true
fi

echo "Clean complete."
