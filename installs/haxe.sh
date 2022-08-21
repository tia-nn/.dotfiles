#!/bin/sh

version=latest
path=$HOME/.haxe-versions

mkdir -p $path

json=$(curl -s https://api.github.com/repos/HaxeFoundation/haxe/releases/${version})
assetname=$(echo $json | jq -r '.assets[].name' | grep linux64.tar.gz)

asseturl=$(echo $json | jq -r ".assets[] | select(.name == \"$assetname\").browser_download_url")

assetpath=$path/$assetname
wget -O $assetpath $asseturl

haxedirname=$(tar zxvf $assetpath -C $path | head -n 1)
haxedirname=${haxedirname%/}
haxeversion=$(echo $assetname | awk -F '-' '{print $2}')

mv $path/$haxedirname $path/$haxeversion

ln -sfn $path/$haxeversion $path/default
rm $assetpath
