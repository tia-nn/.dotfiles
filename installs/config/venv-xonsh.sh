#!/bin/sh

python -m venv ~/.dotfiles/venvs/xonsh-misc
~/.dotfiles/venvs/xonsh-misc/bin/python -m pip install --upgrade pip
~/.dotfiles/venvs/xonsh-misc/bin/pip install 'xonsh[full]'

mkdir -p ~/.local/bin
ln -s ~/.dotfiles/venvs/xonsh-misc/bin/xonsh ~/.local/bin/xonsh
