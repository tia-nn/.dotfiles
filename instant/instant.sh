#!/bin/sh

if [[ ! -x ~/.dotfiles/instant/xonsh ]]; then
    # TODO: for M1/M2 Mac
    mkdir -p ~/.dotfiles/instant/
    wget https://github.com/xonsh/xonsh/releases/latest/download/xonsh-x86_64.AppImage \
        -O ~/.dotfiles/instant/xonsh
    chmod +x ~/.dotfiles/instant/xonsh
fi

~/.dotfiles/instant/xonsh $@
