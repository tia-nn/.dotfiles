#! /usr/bin/env python3
from typing import *
import os
import sys
from pathlib import Path
from platform import system


platform = system()
home = Path.home()
dotfiles = home / '.dotfiles'

sys.path.insert(0, str(dotfiles / 'xonsh'))
os.makedirs(home / '.local' / 'bin', exist_ok=True)

from lib.platform_exception import PlatformNotSupported  # nopep8


def error(*values: object,
          sep: str | None = " ",
          end: str | None = "\n",
          flush: Literal[False] = False) -> None:
    ''' print to stderr '''
    print(values=values, sep=sep, end=end, flush=flush, file=sys.stderr)


if platform not in ('Linux', 'Darwin'):
    error('not supported your platform... :', platform)
    exit(1)


# .xonshrc symbolic link to ~/.xonshrc
if not os.path.lexists(home / '.xonshrc'):
    print(f'ln -s {dotfiles / ".xonshrc"} {home / ".xonshrc"}')
    os.symlink(dotfiles / '.xonshrc', home / '.xonshrc')
else:
    ans = input(
        '# Already exist ~/.xonshrc . Do you want to override? [Y/n]').lower()
    if ans == 'y' or ans == 'yes':
        print(f'mv {home / ".xonshrc"} {dotfiles / "backup" / ".xonshrc"}')
        os.replace(home / '.xonshrc', dotfiles / 'backup' / '.xonshrc')
        print(f'ln -s {dotfiles / ".xonshrc"} {home / ".xonshrc"}')
        os.symlink(dotfiles / '.xonshrc', home / '.xonshrc')


# .hyper.js symbolic link to ~/.hyper.js
if platform == 'Linux':
    hyper = dotfiles / 'apps' / 'hyper_linux.js'
elif platform == 'Darwin':
    hyper = dotfiles / 'apps' / 'hyper_mac.js'
else:
    raise PlatformNotSupported(platform)

if not os.path.lexists(home / '.hyper.js'):
    print(f'ln -s {hyper} {home / ".hyper.js"}')
    os.symlink(hyper, home / '.hyper.js')
else:
    ans = input(
        '# Already exist ~/.hyper.js . Do you want to override? [Y/n]').lower()
    if ans == 'y' or ans == 'yes':
        print(f'mv {home / ".hyper.js"} {dotfiles / "backup" / ".hyper.js"}')
        os.replace(home / '.hyper.js', dotfiles / 'backup' / '.hyper.js')
        print(f'ln -s {hyper} {home / ".hyper.js"}')
        os.symlink(hyper, home / '.hyper.js')


# xonsh traceback log file symbolic link to ~/.xonsh.traceback.log
if not os.path.lexists(home / '.xonsh.traceback.log'):
    print(f'touch {dotfiles / "xonsh.traceback.log"}')
    open(dotfiles / 'xonsh.traceback.log', 'a').close()
    print(
        f'ln -s {dotfiles / "xonsh.traceback.log"} {home / ".xonsh.traceback.log"}')
    os.symlink(dotfiles / 'xonsh.traceback.log', home / '.xonsh.traceback.log')


# write `source paths` to profile
if (profile := os.getenv('LOGIN_SHELL_PROFILE')):
    pass
elif platform == 'Linux':
    profile = home/'.bash_profile'
elif platform == 'Darwin':
    profile = home/'.zprofile'
else:
    error('please set $LOGIN_SHELL_PROFILE; ex. "~/.bash_profile"')
    exit(1)

p = r'''
if [ -d ${HOME}/.dotfiles ]; then
    source ${HOME}/.dotfiles/sh/paths
fi
'''

print(f'echo """{p}""" >> {profile}')
with open(profile, 'a') as f:
    f.write(p)


# mkdir -p ~/.local/bin
print('mkdir -p ~/.local/bin')
os.makedirs(home / '.local' / 'bin', exist_ok=True)
