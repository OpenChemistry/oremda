#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/stateful_volume_renderer $script_dir "$@"
