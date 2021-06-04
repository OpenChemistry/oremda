#!/usr/bin/env bash
set -e

# Whether or not to build singularity as well
build_singularity=false

prefix="basic_example_"

directories=(
  plasma
  loader
  add
  multiply
  view
)

script_dir=$(dirname "$0")

# Get the root directory
root_dir=$(git rev-parse --show-toplevel)

# First, make sure that oremda is built
$root_dir/docker/oremda/build.sh

# Next, build all the example directories
for name in "${directories[@]}"
do
  docker build -t oremda/$prefix$name -f $script_dir/$name/Dockerfile $script_dir/$name
done

if [ "$build_singularity" != true ]; then
  exit 0
fi

singularity_dir=$script_dir/.singularity
for name in "${directories[@]}"
do
  singularity build --force $singularity_dir/$prefix$name.simg docker-daemon://oremda/$prefix$name:latest
done
