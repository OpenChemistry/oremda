#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda
DATA_DIR=/home/patrick/virtualenvs/oremda/data
DOCKER_SOCKET=/var/run/docker.sock

docker run \
  --shm-size=750m \
  -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR \
  -v $DATA_DIR:/data \
  -v $DOCKER_SOCKET:$DOCKER_SOCKET \
  --ipc=shareable \
  oremda/volume_renderer_runner
