#!/usr/bin/env bash

DATA_DIR=/home/alessandro/oremda_data
DOCKER_SOCKET=/var/run/docker.sock
OREMDA_DIR=$(git rev-parse --show-toplevel)
RUNNER_DIR=$PWD/runner

docker run \
  -v $DATA_DIR:/data \
  -v $DOCKER_SOCKET:$DOCKER_SOCKET \
  -v $OREMDA_DIR:/oremda \
  -v $RUNNER_DIR:/runner \
  --ipc=shareable \
  oremda/runner
