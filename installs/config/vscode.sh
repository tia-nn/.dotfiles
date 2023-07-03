#!/bin/sh
# see also https://code.visualstudio.com/docs/getstarted/settings#_settings-file-locations

if [ "$(uname)" == 'Darwin' ]; then
    vscode_profile_dir="$HOME/Library/Application Support/Code/User"
    vscode_keybindings_file="vscode_keybindings_mac.json"
elif [ "$(expr substr $(uname -s) 1 5)" == 'Linux' ]; then
    vscode_profile="$HOME/.config/Code/User"
    vscode_keybindings_file="vscode_keybindings_linux.json"
else
    echo "not supported your platform..." >&2
    exit
fi
mv "${vscode_profile_dir}/settings.json" "${vscode_profile_dir}/settings.old.json"
mv "${vscode_profile_dir}/keybindings.json" "${vscode_profile_dir}/keybindings.old.json"
ln -s "$HOME/.dotfiles/apps/vscode.json" "${vscode_profile_dir}/settings.json"
ln -s "$HOME/.dotfiles/apps/${vscode_keybindings_file}" "${vscode_profile_dir}/keybindings.json"

echo '
eamodio.gitlens
github.vscode-github-actions
GitHub.vscode-pull-request-github
jnoortheen.xonsh
ms-azuretools.vscode-docker
MS-CEINTL.vscode-language-pack-ja
ms-python.autopep8
ms-python.python
ms-python.vscode-pylance
ms-vscode-remote.remote-containers
ms-vsliveshare.vsliveshare
streetsidesoftware.code-spell-checker
' | xargs -L 1 code --install-extension
