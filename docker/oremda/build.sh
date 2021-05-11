#!/usr/bin/env bash

script_dir=$(dirname "$0")
root_dir=$(git rev-parse --show-toplevel)

docker build -t oremda/oremda -f $script_dir/Dockerfile $root_dir
