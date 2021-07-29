#!/usr/bin/env bash
set -e

script_dir=$(dirname "$0")

source $script_dir/env.sh

# Run the server in a docker container
docker run \
    --ipc=host \
    --env OREMDA_VAR_DIR=$OREMDA_VAR_DIR \
    --env OREMDA_DATA_DIR=$OREMDA_DATA_DIR \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR \
    -p 8000:80 \
    oremda/server

# Run the server locally in development
# cd $script_dir
# uvicorn server.main:app --reload
