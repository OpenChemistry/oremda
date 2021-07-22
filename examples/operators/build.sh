#!/usr/bin/env bash
set -e

prefix=""

directories=(
  background_fit
  ncem_reader
  plot
  subtract
)

script_dir=$(dirname "$0")

# Get the root directory
root_dir=$(git rev-parse --show-toplevel)

# First, make sure that oremda is built
$root_dir/docker/oremda/build.sh

# Next, build all the example directories
for name in "${directories[@]}"
do
  bash $script_dir/$name/build.sh
done
