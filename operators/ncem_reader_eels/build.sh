#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/ncem_reader_eels $script_dir "$@"
