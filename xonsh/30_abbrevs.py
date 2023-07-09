def _xonshrc_abbrevs():
    from typing import Optional, List, Callable, Union
    from prompt_toolkit.buffer import Buffer
    import warnings
    from lib.xonshrc_warnings import AbbrevsConfigSkipWarning, AbbrevsXontribNotInstalled
    import os
    import subprocess

    from xonsh.built_ins import XSH

    try:
        from xontrib.abbrevs import abbrevs
    except ModuleNotFoundError:
        warnings.warn("xontrib-abbrevs not installed.",
                      AbbrevsXontribNotInstalled)
        return

    def head_only(abbr: Union[str, Callable]):
        def abbr_func(word: str, buffer: Buffer) -> str:
            if buffer.text.startswith(word):
                if callable(abbr):
                    text = abbr(buffer=buffer, word=word)
                else:
                    text = abbr
                return text
            else:
                return word
        return abbr_func

    def startswith(command: str, abbr: Union[str, Callable]):
        def abbr_func(word: str, buffer: Buffer) -> str:
            if buffer.text.startswith(command):
                if callable(abbr):
                    text = abbr(buffer=buffer, word=word)
                else:
                    text = abbr
                return text
            else:
                return word
        return abbr_func

    def get_git_defaultbranch():
        if (b := os.getenv('GIT_DEFAULTBRANCH')):
            return b
        if (git_conf := subprocess.run(('git', 'config', 'init.defaultBranch'), capture_output=True)).returncode == 0:
            return git_conf.stdout.decode().rstrip()
        else:
            return '<edit>'

    def get_current_branch():
        if (r := subprocess.run(('git', 'rev-pars', '--abbrev-ref', 'HEAD'), capture_output=True)).returncode == 0:
            return r.stdout.decode().rstrip()
        else:
            return '<edit>'

    # tools
    abbrevs['cp'] = head_only('cp -r')
    abbrevs['c'] = head_only('clear')
    abbrevs['l'] = head_only('ls -alh')
    abbrevs['la'] = head_only('ls -a')

    abbrevs['untar'] = head_only('tar xvf')
    abbrevs['unzips'] = head_only('unzip -O sjis')

    abbrevs['sx'] = head_only('source ~/.xonshrc')
    abbrevs['cx'] = head_only('code ~/.dotfiles')

    # docker / podman
    def docker_abbrevs():
        if (docker := os.getenv('DOCKER_COMMAND')):
            pass
        elif subprocess.run(('which', 'docker'), capture_output=True).returncode == 0:
            docker = 'docker'
        elif subprocess.run(('which', 'podman'), capture_output=True).returncode == 0:
            docker = 'podman'
        else:
            warnings.warn(
                "Docker like command is not installed. Please install or set $DOCKER_COMMAND.", AbbrevsConfigSkipWarning)
            return

        abbrevs['dc'] = head_only(f'{docker}')
        abbrevs['dimg'] = head_only(f'{docker} images')
        abbrevs['dlsi'] = head_only(f'{docker} image ls')
        abbrevs['dbld'] = head_only(f'{docker} build ./')
        abbrevs['drun'] = head_only(f'{docker} run')
        abbrevs['-itr'] = startswith(docker, '-it --rm')
        abbrevs['dexe'] = head_only(f'{docker} exec -it')
        abbrevs['drm'] = head_only(f'{docker} rm')
        abbrevs['drmi'] = head_only(f'{docker} rmi')
        abbrevs['diprn'] = head_only(f'{docker} image prune --force')
        abbrevs['dps'] = head_only(f'{docker} ps')
        abbrevs['dpsa'] = head_only(f'{docker} ps -a')
        abbrevs['dst'] = head_only(f'{docker} start')
        abbrevs['dstp'] = head_only(f'{docker} stop')
        abbrevs['restart'] = head_only(f'{docker} restart')
        abbrevs['dpl'] = head_only(f'{docker} pull')
        abbrevs['dvl'] = head_only(f'{docker} volume')

        abbrevs['dcc'] = head_only(f'{docker}-compose')
        abbrevs['dcu'] = head_only(f'{docker}-compose up')
        abbrevs['dcud'] = head_only(f'{docker}-compose up -d')
        abbrevs['dce'] = head_only(f'{docker}-compose exec')
        abbrevs['dcd'] = head_only(f'{docker}-compose down')
        abbrevs['dcdv'] = head_only(f'{docker}-compose down -v')
        abbrevs['dcs'] = head_only(f'{docker}-compose stop')
        abbrevs['dcr'] = head_only(f'{docker}-compose rm')
        abbrevs['dccc'] = head_only(f'{docker}-compose config')

    docker_abbrevs()

    abbrevs['g'] = head_only('git')
    abbrevs['gcl'] = head_only('git clone')
    abbrevs['gini'] = head_only('git init')

    abbrevs['ga'] = head_only('git add')
    abbrevs['gaa'] = head_only('git add --all')
    abbrevs['gmv'] = head_only('git mv')
    abbrevs['grstr'] = head_only('git restore')
    abbrevs['grstrm'] = head_only(
        lambda word, buffer: f'git restore --source={get_git_defaultbranch()}')
    abbrevs['grstrh'] = head_only('git restore --source HEAD')
    abbrevs['grm'] = head_only('git rm')
    abbrevs['grmc'] = head_only('git rm --cached')
    abbrevs['gsch'] = head_only('git sparce-checkout')

    abbrevs['gbis'] = head_only('git bisect')
    abbrevs['gd'] = head_only('git diff')
    abbrevs['gg'] = head_only('git grep')
    abbrevs['gl'] = head_only('git log')
    abbrevs['glg'] = head_only('git log --graph --oneline --all')
    abbrevs['gln'] = head_only('git log --graph --oneline --all --max-count')
    abbrevs['glmn'] = head_only(
        lambda word, buffer: f'git log --graph --oneline --branches={get_git_defaultbranch()} --max-count')
    abbrevs['gsh'] = head_only('git show')
    abbrevs['gs'] = head_only('git status')

    abbrevs['gb'] = head_only('git branch')
    abbrevs['gc'] = head_only('git commit --message "<edit>"')
    abbrevs['gm'] = head_only('git merge')
    abbrevs['grb'] = head_only('git rebase')
    abbrevs['grst'] = head_only('git reset')
    abbrevs['gsw'] = head_only('git switch')
    abbrevs['gswc'] = head_only('git switch --create')
    abbrevs['gtag'] = head_only('git tag')

    abbrevs['gf'] = head_only('git fetch')
    abbrevs['gpl'] = head_only('git pull')
    abbrevs['gplo'] = head_only('git pull origin')
    abbrevs['gploh'] = head_only(
        lambda word, buffer: f'git pull origin {get_current_branch()}')
    abbrevs['gps'] = head_only('git push')
    abbrevs['gpso'] = head_only('git push origin')
    abbrevs['gpsoh'] = head_only(
        lambda word, buffer: f'git push origin {get_current_branch()}')

    abbrevs['gst'] = head_only('git stash')
    abbrevs['gsm'] = head_only('git submodule')
    abbrevs['grmt'] = head_only('git remote')

    abbrevs['gwt'] = head_only('git worktree')
    abbrevs['gcf'] = head_only('git config')
    abbrevs['ggc'] = head_only('git gc')

    abbrevs['@b'] = startswith('git', lambda word,
                               buffer: get_current_branch())


_xonshrc_abbrevs()
