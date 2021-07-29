#!/usr/bin/env bash
set -e

script_dir=$(dirname "$0")

# Get the root directory
root_dir=$(git rev-parse --show-toplevel)

# First, make sure that oremda is built
$root_dir/docker/oremda/build.sh

docker build -t oremda/server -f $script_dir/Dockerfile $script_dir
