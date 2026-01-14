#!/bin/bash
: "${DOCKERFILE:=benchmark/Dockerfile}"
: "${TAG:=cecli-cat}"

set -e

docker build \
  --file "${DOCKERFILE}" \
  -t "${TAG}"  \
  .
