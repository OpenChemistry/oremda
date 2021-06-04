#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda
prefix=basic_example_

plasma_id=$(docker run --rm -d --ipc="shareable" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR   oremda/${prefix}plasma)
loader_id=$(docker run -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR     oremda/${prefix}loader)
add_id=$(docker run --rm -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/${prefix}add)
multiply_id=$(docker run --rm -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/${prefix}multiply)
view_id=$(docker run -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/${prefix}view)

# Wait for the loader to finish
docker wait $loader_id

docker logs $loader_id
docker logs $view_id

docker container rm $loader_id $view_id

# Plasma does not stop automatically... we should fix that
docker kill $plasma_id
