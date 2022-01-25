#!/usr/bin/bash

package_dir=$(pwd)
package_name="oremda-$(basename $package_dir)"

current_published_version=$(curl https://test.pypi.org/pypi/${package_name}/json 2>/dev/null | jq '.info.version')
if [ $? -ne 0 ]
then
  echo "Package version not found for: $package_name"
  exit 1
fi

current_published_version=$(echo $current_publish_version | sed 's/\"//g')
current_version=$(cat pyproject.toml  | grep version | sed 's/version = \"\([0-9\.]*\)\"/\1/g')

if [ "$current_published_version" = "$current_version" ]; then
    echo "Version has not changed, nothing to publish."
else
    poetry publish
fi
