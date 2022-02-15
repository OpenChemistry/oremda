#!/usr/bin/env bash

package_dir=$(pwd)
package_name=$(basename $package_dir)

# Special can for the meta package
if [[ $package_name == "meta" ]]; then
  package_name="oremda"
else
  package_name="oremda-${package_name}"
fi

current_published_version=$(curl https://pypi.org/pypi/${package_name}/json 2>/dev/null | jq '.info.version')
if [ $? -ne 0 ]
then
  echo "Package version not found for: $package_name"
  exit 1
fi

current_published_version=$(echo $current_published_version | sed 's/\"//g')
current_version=$(cat pyproject.toml  | grep ^version | sed 's/version = \"\([0-9\.]*\)\"/\1/g')

if [ "$current_published_version" = "$current_version" ]; then
    echo "Version has not changed, nothing to publish."
else
    rm -rf dist/
    poetry publish -n --build -u __token__
fi
