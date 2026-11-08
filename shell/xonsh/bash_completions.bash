
# for m2 mac
if [ -e /opt/homebrew/etc/profile.d/bash_completion.sh ]; then
    source /opt/homebrew/etc/profile.d/bash_completion.sh
fi
if [ -e /opt/git-completion/git-completion.bash ]; then
    source /opt/git-completion/git-completion.bash
fi
if [ -d /Applications/Docker.app/Contents/Resources/etc ]; then
    source /Applications/Docker.app/Contents/Resources/etc/*.bash-completion
fi


# for linux

if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
