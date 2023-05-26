# My cool dotfiles

my dotfiles for Xonsh and others

## install

```
$ ~/.dotfiles/installs/dotfiles.sh
```

## tools install

### pyenv

see also https://github.com/pyenv/pyenv-installer .

``` bash
curl https://pyenv.run | bash
```

#### needed libraries

see also https://github.com/pyenv/pyenv/wiki#suggested-build-environment

##### Fedora 22 ↑

``` bash
dnf install make gcc patch zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel libuuid-devel gdbm-devel libnsl2-devel
```

#### build latest python

``` bash
pyenv install $(pyenv install --list | egrep '^\s*3.[0-9]+.[0-9]+$' | tail -1)
```

### xonsh

see also https://xon.sh/

``` bash
python -m pip install 'xonsh[full]'
```

### hyper

TODO
https://hyper.is/

### .xonshrc env

$DOCKER_COMMAND: Specify a Docker like command.
