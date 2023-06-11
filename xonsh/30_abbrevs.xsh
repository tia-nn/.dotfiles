def _xonshrc_abbrevs():
    from typing import Optional, List, Callable, Union
    from prompt_toolkit.buffer import Buffer
    import warnings
    import xontrib.abbrevs
    from lib.xonshrc_warnings import AbbrevsConfigSkipWarning


    global abbrevs


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
        if 'GIT_DEFAULTBRANCH' in ${...} and $GIT_DEFAULTBRANCH:
            return $GIT_DEFAULTBRANCH
        if (git_conf := !(git config init.defaultBranch)):
            return git_conf.out.strip()
        else:
            '<edit>'


    # tools
    abbrevs['cp'] = head_only('cp -r')
    abbrevs['c'] = head_only('clear')
    abbrevs['l'] = head_only('ls -alh')
    abbrevs['la'] = head_only('ls -a')

    abbrevs['untar'] = head_only('tar xvf')
    abbrevs['unzips'] = head_only('unzip -O sjis')

    abbrevs['sx'] = head_only('source ~/.xonshrc')
    abbrevs['cx'] = head_only('code ~/.dotfiles')

    aliases['dfu-hhkb'] = 'dfu-programmer atmega32u4'
    aliases['xpython'] = aliases['xpip'][1] if aliases['xpip'][0] == 'sudo' \
                            else aliases['xpip'][0]


    # docker / podman
    def docker_abbrevs():
        if 'DOCKER_COMMAND' in ${...} and $DOCKER_COMMAND:
            docker = $DOCKER_COMMAND
        elif !(which docker):
            docker = 'docker'
        elif !(which podman):
            docker = 'podman'
        else:
            warnings.warn("Docker like command is not installed. Please install or set $DOCKER_COMMAND.", AbbrevsConfigSkipWarning)
            return

        abbrevs['dc'] = head_only(f'{docker}')
        abbrevs['dimg'] = head_only(f'{docker} images')
        abbrevs['dlsi'] = head_only(f'{docker} image ls')
        abbrevs['dbld'] = head_only(f'{docker} build ./')
        abbrevs['drun'] = head_only(f'{docker} run')
        abbrevs['itr'] = startswith(docker, '-it --rm')
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
        abbrevs['dcd'] = head_only(f'{docker}-compose down')
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
    abbrevs['grstrm'] = head_only(lambda word, buffer: f'git restore --source={get_git_defaultbranch()}')
    abbrevs['grstrh'] = head_only('git restore --source HEAD')
    abbrevs['grm'] = head_only('git rm')
    abbrevs['grmc'] = head_only('git rm --cached')
    abbrevs['gsch'] = head_only('git sparce-checkout')

    abbrevs['gbis'] = head_only('git bisect')
    abbrevs['gd'] = head_only('git diff')
    abbrevs['gg'] = head_only('git grep')
    abbrevs['gl'] = head_only('git log')
    abbrevs['glg'] = head_only('git log --graph --oneline --all')
    abbrevs['gln'] = head_only('git log --graph --oneline --max-count=')
    abbrevs['glmn'] = head_only(lambda word, buffer: f'git log --graph --oneline --branches={get_git_defaultbranch()} --max-count=')
    abbrevs['gsh'] = head_only('git show')
    abbrevs['gs'] = head_only('git status')

    abbrevs['gb'] = head_only('git branch')
    abbrevs['gc'] = head_only('git commit -m "<edit>"')
    abbrevs['gm'] = head_only('git merge')
    abbrevs['grb'] = head_only('git rebase')
    abbrevs['grst'] = head_only('git reset')
    abbrevs['gsw'] = head_only('git switch')
    abbrevs['gswc'] = head_only('git switch --create')
    abbrevs['gtag'] = head_only('git tag')

    abbrevs['gf'] = head_only('git fetch')
    abbrevs['gpl'] = head_only('git pull')
    abbrevs['gplo'] = head_only('git pull origin')
    abbrevs['gps'] = head_only('git push')
    abbrevs['gpso'] = head_only('git push origin')

    abbrevs['gst'] = head_only('git stash')
    abbrevs['gsm'] = head_only('git submodule')
    abbrevs['grmt'] = head_only('git remote')

    abbrevs['gwt'] = head_only('git worktree')
    abbrevs['gcf'] = head_only('git config')
    abbrevs['ggc'] = head_only('git gc')
    abbrevs['headbr'] = startswith('git', lambda word, buffer: r.out.strip() if (r := !(git rev-parse --abbrev-ref HEAD)) else word)


    def git_prune_merged_branch():
        git switch @(get_git_defaultbranch())
        git pull origin @(get_git_defaultbranch())
        git branch --merged | egrep --invert-match r'\\*|main|develop|release' | xargs git branch -d
        git switch -


    aliases['git-prune-localbranch'] = git_prune_merged_branch


_xonshrc_abbrevs()
