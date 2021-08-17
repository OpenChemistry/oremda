#!/usr/bin/env bash
set -e

function join_by { local IFS="$1"; shift; echo "$*"; }

# Whether or not to build singularity as well
build_singularity=false

# Whether or not to build with mpi
with_mpi=false

prefix=""

directories=(
  runner
)

build_args=()

script_dir=$(dirname "$0")

# Get the root directory
root_dir=$(git rev-parse --show-toplevel)

# First, make sure that oremda is built
$root_dir/docker/oremda/build.sh

if [ "$with_mpi" == true ]; then
  # Build oremda mpi as well
  $root_dir/docker/oremda_mpi/build.sh
  build_args+='--build-arg BASE_IMAGE=oremda/oremda_mpi'
fi


# Next, build all the example directories
for name in "${directories[@]}"
do
  docker build -t oremda/$prefix$name -f $script_dir/$name/Dockerfile $script_dir/$name $(join_by ' ' $build_args)
done

if [ "$build_singularity" != true ]; then
  exit 0
fi

singularity_dir=$script_dir/.singularity
for name in "${directories[@]}"
do
  singularity build --force $singularity_dir/$prefix$name.simg docker-daemon://oremda/$prefix$name:latest
done
