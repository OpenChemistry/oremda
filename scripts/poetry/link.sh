#!/usr/bin/env bash

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "${script_dir}/packages.sh"

cd $script_dir/../../

for package_dir in $package_dirs
do
    echo "Linking oremda-$package_dir"
    cd $package_dir
    oremda_packages=$(poetry show | grep "^oremda-" | sed "s/oremda-\([a-z]*\).*/\1/g")
    package_paths=""
    for pkg in $oremda_packages
    do
        package_paths="${package_paths} ../$pkg"
    done

    if [ -n "$package_paths" ]; then
        poetry add $package_paths
    fi
    cd ..
done

# finally until poetry 1.2 is released we need to manually add the develop=true
# option.
pyproject_files=`find . -name pyproject.toml | xargs -n1 grep -l "^oremda-.*"`
for pyproject_file in $pyproject_files
do
    sed -i 's/{path = \([^,]*\)}$/{path = \1, develop = true}/g' $pyproject_file
done

# We need to call update, for the develop=true to take effect
for package_dir in $package_dirs
do
    cd $package_dir
    poetry update
    cd ..
done