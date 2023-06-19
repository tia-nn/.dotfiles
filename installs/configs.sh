#!/bin/sh

## git
git config --global user.name tia-nn
git config --global user.email yknms3533642@yahoo.co.jp

git config --global diff.indentHeuristic true


## npm
npm config -g set prefix=$HOME/.npm


## vscode  see also https://code.visualstudio.com/docs/getstarted/settings#_settings-file-locations
if [ "$(uname)" == 'Darwin' ]; then
    vscode_profile="$HOME/Library/Application\ Support/Code/User/settings.json"
elif [ "$(expr substr $(uname -s) 1 5)" == 'Linux' ]; then
    vscode_profile="$HOME/.config/Code/User/settings.json"
else
    echo "not supported your platform..." >&2
    exit 1
fi
mv ${vscode_profile} $(dirname $vscode_profile)/settings.old.json
