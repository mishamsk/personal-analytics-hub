#!/bin/bash

# Run from repo root, not from scripts folder!

set -x
set -e

docker-compose -p pah down --remove-orphans
scripts/docker_build.sh
docker-compose -p pah up -d
