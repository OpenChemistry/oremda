#!/usr/bin/env bash

DATA_DIR=/data/oremda
IMAGES_DIR=$PWD/images
OREMDA_DIR=$(git rev-parse --show-toplevel)
RUNNER_DIR=$PWD/runner

sudo singularity run \
  --bind $DATA_DIR:/data \
  --bind $IMAGES_DIR:/images \
  --bind $OREMDA_DIR:/oremda \
  --bind $RUNNER_DIR:/runner \
  --ipc \
  $IMAGES_DIR/oremda_runner.simg
