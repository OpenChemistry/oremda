#!/usr/bin/env bash

export PYTHONUNBUFFERED=1

export OREMDA_DATA_DIR=$HOME/data/oremda
export OREMDA_CONTAINER_TYPE=singularity
export OREMDA_SIF_DIR=images
export OREMDA_OPERATOR_CONFIG_FILE="operator_config.json"

mpirun -np 8 oremda run pipeline.json
