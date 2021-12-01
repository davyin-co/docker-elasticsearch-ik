#!/bin/bash
### https://blog.dockbit.com/templating-your-dockerfile-like-a-boss-2a84a67d28e9
render() {
sedStr="
  s/%%VERSION%%/$version/g;
"

sed -e "$sedStr" $1
}

versions=(7.10.1 7.11.2 7.12.1 7.13.4 7.14.2)
for version in ${versions[*]}; do
  if [ ! -d $version ]; then
    mkdir $version
  fi
  render Dockerfile.template > $version/Dockerfile
done
