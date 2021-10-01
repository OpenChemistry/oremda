#!/usr/bin/env bash
set -e

function join_by { local IFS="$1"; shift; echo "$*"; }

# Whether or not to build singularity as well
build_singularity=true

# Whether or not to build with mpi
# This is not needed if we only allow the parent containers
# to build with MPI and they forward messages to the operator
# via plasma and message queues.
with_mpi=false

# Whether or not to build visualization containers
with_vis=false

prefix=""

directories=(
  peak_base
  background_fit
  ncem_reader
  ncem_reader_eels
  peak_find
  peak_opt
  fft2d
  crop2d
  diffractogram
  lattice_find
  unit_cell
  difference
  tile
  plot
  print
  subtract
  tiff_reader
  gaussian_blur
  picture
  scatter
  vector
  histograms
)

if [ "$with_vis" == true ]; then
  directories+='stateful_volume_renderer'
  directories+='vtk_reader'
fi

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
  bash $script_dir/$name/build.sh $(join_by ' ' $build_args)
done

if [ "$build_singularity" != true ]; then
  exit 0
fi

singularity_dir=$script_dir/images

mkdir -p $singularity_dir
rm -rf $singularity_dir/*

cd $singularity_dir
for name in "${directories[@]}"
do
  $root_dir/scripts/singularity/docker_to_singularity.py oremda/$prefix$name
done
