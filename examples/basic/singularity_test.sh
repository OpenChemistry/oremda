#!/usr/bin/env bash

OREMDA_VAR_DIR=/run/oremda

script_dir=$(dirname "$0")
singularity_dir=$script_dir/.singularity
prefix=basic_example_

singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}plasma.simg &
plasma_pid=$!
sleep 10
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}loader.simg &
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}add.simg &
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}multiply.simg &
singularity run --bind $OREMDA_VAR_DIR:$OREMDA_VAR_DIR $singularity_dir/${prefix}view.simg &

# Wait for the jobs to finish
sleep 20

# Plasma will not stop automatically. Kill it.
kill $plasma_pid

# FIXME: I haven't found a clean way to kill the plasma container.
# Killing it by pid does not stop the plasma_store command inside, so
# things do not get properly cleaned up. How do we do this???
# For now, kill all plasma_store processes
pkill -f "Singularity" && pkill -f "plasma_store" && rm $OREMDA_VAR_DIR/* && rm /dev/mqueue/*
