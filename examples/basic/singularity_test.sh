#!/usr/bin/env bash

script_dir=$(dirname "$0")
singularity_dir=$script_dir/.singularity
prefix=basic_example_

singularity run $singularity_dir/basic_example_loader.simg      /queue0 /queue1 /queue2 &
sleep 5
singularity run $singularity_dir/basic_example_times_two.simg   /queue0 /queue1 &
singularity run $singularity_dir/basic_example_minus_three.simg /queue1 /queue2 &
singularity run $singularity_dir/basic_example_viewer.simg      /queue2 &
