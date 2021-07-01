#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/background_fit $script_dir
