#!/usr/bin/env bash
set -euo pipefail

# Demo script: build sandbox image, bring up DB, start server (background),
# run local client, verify DB counts.
# Optional: pass --load-duckdb to load synthetic_data/synthea.duckdb into Postgres
# using scripts/bootstrap_synthea.py
#
# Usage:
#   ./scripts/demo.sh [--load-duckdb] [--db-port 5433]

IMAGE_NAME=fastomop/sandbox:python-3.11-slim
COMPOSE_DB_SERVICE=db

# Defaults
LOAD_DUCKDB=false
DB_PORT=${DB_PORT:-5432}

# Parse args: --load-duckdb and optional --db-port <port>
while [[ $# -gt 0 ]]; do
  case "$1" in
    --load-duckdb)
      LOAD_DUCKDB=true
      shift
      ;;
    --db-port)
      DB_PORT="$2"
      shift 2
      ;;
    --db-port=*)
      DB_PORT="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

echo "Using DB host port: ${DB_PORT}"

echo "1/7 Build sandbox image: ${IMAGE_NAME}"
docker build -t ${IMAGE_NAME} -f docker/sandbox/Dockerfile .

echo "2/7 Start database via docker-compose (host port ${DB_PORT})"
# Export DB_PORT so docker-compose picks it up in the ports mapping
export DB_PORT
docker compose up -d ${COMPOSE_DB_SERVICE}

echo "Waiting for Postgres to accept connections on localhost:${DB_PORT}..."
until PGPASSWORD=${DB_PASSWORD:-postgres} psql -U ${DB_USER:-omcp} -h localhost -p ${DB_PORT} -d ${DB_NAME:-omcp} -c '\q' >/dev/null 2>&1; do
  printf '.'
  sleep 1
done
echo " Postgres ready"

if [ "$LOAD_DUCKDB" = true ]; then
  echo "3/7 Loading synthetic_data/synthea.duckdb into Postgres via scripts/bootstrap_synthea.py"
  DB_HOST=localhost DB_USER=${DB_USER:-omcp} DB_PASSWORD=${DB_PASSWORD:-postgres} DB_NAME=${DB_NAME:-omcp} DB_PORT=${DB_PORT} python3 scripts/bootstrap_synthea.py
  STEP=4
else
  STEP=3
fi

echo "${STEP}/7 Start MCP server in background (logs to server.log)"
export DOCKER_IMAGE=${IMAGE_NAME}
PYTHONPATH=src nohup python3 src/omcp_py/main.py > server.log 2>&1 &
SERVER_PID=$!
sleep 2

echo "$(expr ${STEP} + 1)/7 Run local client to create sandbox, install and test"
PYTHONPATH=src python3 scripts/local_client.py || true

echo "6/7 Verify DB counts"
psql -U ${DB_USER:-omcp} -d ${DB_NAME:-omcp} -h localhost -p ${DB_PORT} -c "SELECT COUNT(*) AS person_count FROM omop_cdm.person;"
psql -U ${DB_USER:-omcp} -d ${DB_NAME:-omcp} -h localhost -p ${DB_PORT} -c "SELECT COUNT(*) AS visit_count FROM omop_cdm.visit_occurrence;"
psql -U ${DB_USER:-omcp} -d ${DB_NAME:-omcp} -h localhost -p ${DB_PORT} -c "SELECT COUNT(*) AS condition_count FROM omop_cdm.condition_occurrence;"

echo "7/7 Cleanup: stopping server"
kill ${SERVER_PID} || true
wait ${SERVER_PID} || true

echo "Demo complete. Server logs are in server.log"
