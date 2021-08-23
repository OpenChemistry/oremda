#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/plot $script_dir "$@"
