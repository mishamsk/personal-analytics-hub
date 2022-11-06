#!/usr/bin/env bash

set -eo pipefail

REPO_PREFIX="${PAH_DOCKER_REPO_PREFIX:-pah}"
REPO_NAME="${REPO_PREFIX}/superset"
SUPERSET_VER="${PAH_SUPERSET_VER:-2.0.0}"

echo "Building Superset Docker images"

#
# Build the "base" image used for app, init abd beat
#
docker build --target base \
  --build-arg "SUPERSET_VERSION=${SUPERSET_VER}" \
  -t "${REPO_NAME}:${SUPERSET_VER}" \
  -t "${REPO_NAME}:latest" \
  superset

#
# Build the "worker" image
#

docker build --target worker \
  --build-arg "SUPERSET_VERSION=${SUPERSET_VER}" \
  -t "${REPO_NAME}-worker:${SUPERSET_VER}" \
  -t "${REPO_NAME}-worker:latest" \
  superset

REPO_NAME="${REPO_PREFIX}/etl"
PY_VER="${PAH_PY_VER:-3.10}"

echo "Building ETL Docker images"

#
# Build the etl image
#
docker build \
  --build-arg "PY_VER=${PY_VER}" \
  --build-arg "PAH_SUPERSET_ADMIN_EMAIL=${PAH_SUPERSET_ADMIN_EMAIL:-pah@localhost}" \
  --build-arg "PAH_NULLMAILER_REMOTE_SPEC=${PAH_NULLMAILER_REMOTE_SPEC}" \
  --build-arg "PAH_ETL_SCHEDULE=${PAH_ETL_SCHEDULE:-0 0 * * *}" \
  -t "${REPO_NAME}:${PY_VER}" \
  -t "${REPO_NAME}:latest" \
  etl
