#! /bin/sh

# .xonshrc symbolic link to ~/
if [ -f '~/.xonshrc' ]; then
    ln -s ~/.dotfiles/.xonshrc ~/.xonshrc
fi

# add source command to .bash_profile
echo -n '
# Added by .dotfiles
if [ -d ~/.dotfiles ]; then
	source ~/.dotfiles/sh/pathes
	source ~/.dotfiles/sh/aliases
fi
' >> ~/.bash_profile
