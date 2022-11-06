#!/bin/bash

# Run from repo root, not from scripts folder!

set -x
set -e

docker-compose -p pah down --remove-orphans
docker volume rm pah_db-data || true
docker volume rm pah_superset_home || true
docker volume rm pah_redis || true
scripts/docker_build.sh
docker-compose -p pah up -d
