#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda
DATA_DIR=/home/alessandro/oremda_data
DOCKER_SOCKET=/var/run/docker.sock

docker run \
  -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR \
  -v $DATA_DIR:/data \
  -v $DOCKER_SOCKET:$DOCKER_SOCKET \
  --ipc=shareable \
  oremda/runner
