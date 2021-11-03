#!/usr/bin/env bash

image_name=oremda/bragg_vector_map

# Whether or not to build a sif file as well
build_sif=true

script_dir=$(dirname "$0")

# Get the root directory
root_dir=$(git rev-parse --show-toplevel)

# First, make sure that oremda is built
$root_dir/docker/oremda/build.sh

docker build -t $image_name $script_dir "$@"

if [ "$build_sif" != true ]; then
  exit 0
fi

sif_dir=$script_dir/images

mkdir -p $sif_dir
rm -rf $sif_dir/*

cd $sif_dir
$root_dir/scripts/singularity/docker_to_singularity.py $image_name:latest
