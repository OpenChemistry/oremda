#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/fft2d $script_dir "$@"
