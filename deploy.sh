#!/usr/bin/env bash
# Executed on the EC2 host by the GitHub Actions deploy workflow.
# Expects env vars: GHCR_USER, GHCR_TOKEN, IMAGE
set -euo pipefail

cd ~/task-api
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin

export IMAGE
docker compose -f docker-compose.prod.yml --env-file .env pull api
docker compose -f docker-compose.prod.yml --env-file .env up -d
docker image prune -f
docker logout ghcr.io
