#!/usr/bin/env bash

script_dir=$(dirname "$0")

docker build -t oremda/vtk_reader $script_dir
