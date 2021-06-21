#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda
prefix=basic_example_

# Do not remove the loader and view immediately so we can print their logs...
loader_id=$(docker run -d --ipc="shareable" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/${prefix}loader)
add_id=$(docker run --rm -d --ipc="container:$loader_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/${prefix}add)
multiply_id=$(docker run --rm -d --ipc="container:$loader_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/${prefix}multiply)

# Wait for the loader to finish
docker wait $loader_id

docker logs $loader_id

# Clean up...
docker container rm $loader_id
