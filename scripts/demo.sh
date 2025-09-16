#!/usr/bin/env bash
set -euo pipefail

# Demo script: build sandbox image, bring up DB, start server (background), run local client, verify DB counts
# Run from repo root

IMAGE_NAME=fastomop/sandbox:python-3.11-slim
COMPOSE_DB_SERVICE=db

echo "1/6 Build sandbox image: ${IMAGE_NAME}"
docker build -t ${IMAGE_NAME} -f docker/sandbox/Dockerfile .

echo "2/6 Start database via docker-compose"
docker compose up -d ${COMPOSE_DB_SERVICE}

echo "3/6 Start MCP server in background (logs to server.log)"
export DOCKER_IMAGE=${IMAGE_NAME}
PYTHONPATH=src nohup python3 src/omcp_py/main.py > server.log 2>&1 &
SERVER_PID=$!
# give server a moment to start
sleep 2

echo "4/6 Run local client to create sandbox, install and test"
PYTHONPATH=src python3 scripts/local_client.py || true

echo "5/6 Verify DB counts"
psql -U omcp -d omcp -h localhost -c "SELECT COUNT(*) AS person_count FROM omop_cdm.person;"
psql -U omcp -d omcp -h localhost -c "SELECT COUNT(*) AS visit_count FROM omop_cdm.visit_occurrence;"
psql -U omcp -d omcp -h localhost -c "SELECT COUNT(*) AS condition_count FROM omop_cdm.condition_occurrence;"

echo "6/6 Cleanup: stopping server"
kill ${SERVER_PID} || true
wait ${SERVER_PID} || true

echo "Demo complete. Server logs are in server.log"
