#!/usr/bin/bash

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $script_dir/../../

find . -name "pyproject.toml" -print0 | while read -d $'\0' project_file
do
    package_dir=$(dirname "$project_file")
    name=$(echo $package_dir | sed 's/\.\///g')
    echo "Linking oremda-$name"
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