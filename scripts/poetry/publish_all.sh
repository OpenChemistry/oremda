#!/usr/bin/env bash

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "${script_dir}/packages.sh"

cd $script_dir/../../

for package_dir in $package_dirs
do
    echo "Publishing oremda-$package_dir"
    cd $package_dir
    source "${script_dir}/publish.sh"
    cd ..
done