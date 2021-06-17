#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda

script_dir=$(dirname "$0")
singularity_dir=$script_dir/.singularity
prefix=basic_example_

singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}loader.simg &
# Wait for the plasma store to start and the queues to be created
sleep 10
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}add.simg &
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}multiply.simg &
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}view.simg &


# FIXME: double check that everything is being closed and cleaned up properly
