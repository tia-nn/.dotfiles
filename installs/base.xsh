#! /usr/bin/env xonsh

import os

# .xonshrc symbolic link to ~/.xonshrc

if not os.path.lexists(p'~/.xonshrc'):
    ln -s ~/.dotfiles/.xonshrc ~/.xonshrc
else:
    echo 'already exist ~/.xonshrc'


if 'LOGIN_SHELL_PROFILE' in ${...} and $LOGIN_SHELL_PROFILE != '':
    shell = p'$LOGIN_SHELL_PROFILE'
elif (uname_res := $(uname).rstrip()) == 'Linux':
    shell = p'~/.bash_profile'
elif uname_res == 'Darwin':
    shell = p'~/.zprofile'
else:
    echo 'please set $LOGIN_SHELL_PROFILE ex. "~/.bash_profile"'
    exit

p = r'''
if [ -d ${HOME}/.dotfiles ]; then
    source ${HOME}/.dotfiles/sh/pathes
fi
'''

echo -n @(p) >> @(shell)