#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda

plasma_id=$(docker run -d --ipc="shareable" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR   oremda/basic_example_plasma)
loader_id=$(docker run -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR     oremda/basic_example_loader)
add_id=$(docker run -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/basic_example_add)
multiply_id=$(docker run -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/basic_example_multiply)
viewer_id=$(docker run -d --ipc="container:$plasma_id" -v $OREMDA_VAR_DIR:$OREMDA_VAR_DIR oremda/basic_example_viewer)

# Wait for the loader to finish
docker wait $loader_id

docker kill $plasma_id $add_id $multiply_id $viewer_id

docker logs $loader_id
docker logs $viewer_id
