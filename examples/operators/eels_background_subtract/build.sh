#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/eels_background_subtract $script_dir
