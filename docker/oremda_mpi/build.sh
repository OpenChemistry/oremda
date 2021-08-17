#!/usr/bin/env bash

script_dir=$(dirname "$0")
root_dir=$(git rev-parse --show-toplevel)

# First, make sure oremda/oremda is updated
$root_dir/docker/oremda/build.sh

# Next, build oremda_mpi
docker build -t oremda/oremda_mpi -f $script_dir/Dockerfile $root_dir
