#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/gaussian_blur $script_dir "$@"
