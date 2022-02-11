#!/usr/bin/bash

script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "${script_dir}/packages.sh"

cd $script_dir/../../

for package_dir in $package_dirs
do
    echo "Unlinking oremda-$package_dir"
    cd $package_dir
    oremda_packages=$(poetry show | grep "^oremda-" | sed "s/\(oremda-[a-z]*\)[^0-9]*\([0-9\.]*\).*/\1@^\2/g")

    package_versions=""
    for pkg_version in $oremda_packages
    do
        package_versions="${package_versions} $pkg_version"
    done

    if [ -n "$package_versions" ]; then
        poetry add $package_versions
    fi
    cd ..
done