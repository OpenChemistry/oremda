#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/unit_cell $script_dir "$@"
