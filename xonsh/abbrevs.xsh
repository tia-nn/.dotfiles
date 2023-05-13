# activate abbrevs
if not ![xontrib load abbrevs]:
    xpip install xontrib-abbrevs
    xontrib load abbrevs

# tools
abbrevs['cp'] = 'cp -r'
abbrevs['c'] = 'clear'
abbrevs['l'] = 'ls -alh'
abbrevs['la'] = 'ls -a'

abbrevs['untar'] = 'tar xvf'
abbrevs['unzips'] = 'unzip -O sjis'

abbrevs['dotfiles'] = '~/.dotfiles'
abbrevs['xonshrc'] = '~/.dotfiles/.xonshrc'

aliases['dfu-hhkb'] = 'dfu-programmer atmega32u4'

# docker / podman
docker = 'docker'
abbrevs['dc'] = f'{docker}'
abbrevs['dimg'] = f'{docker} images'
abbrevs['dlsi'] = f'{docker} image ls'
abbrevs['dbld'] = f'{docker} build ./'
abbrevs['drun'] = f'{docker} run'
abbrevs['itr'] = '-it --rm'
abbrevs['dexe'] = f'{docker} exec -it'
abbrevs['drm'] = f'{docker} rm'
abbrevs['drmi'] = f'{docker} rmi'
abbrevs['diprn'] = f'{docker} image prune --force'
abbrevs['dps'] = f'{docker} ps -a'
abbrevs['dst'] = f'{docker} start'
abbrevs['dstp'] = f'{docker} stop'
abbrevs['restart'] = f'{docker} restart'
abbrevs['dpl'] = f'{docker} pull'

abbrevs['dcc'] = f'{docker}-compose'
abbrevs['dcu'] = f'{docker}-compose up'
abbrevs['dcd'] = f'{docker}-compose down'

$GIT_DEFAULTBRANCH = 'main'
abbrevs['g'] = 'git'
abbrevs['gcl'] = 'git clone'
abbrevs['gini'] = 'git init'

abbrevs['ga'] = 'git add'
abbrevs['gaa'] = 'git add -A'
abbrevs['gmv'] = 'git mv'
abbrevs['grstr'] = 'git restore -s'
abbrevs['grm'] = 'git rm'
abbrevs['grmc'] = 'git rm --cached'
abbrevs['gsch'] = 'git sparce-checkout'

abbrevs['gbis'] = 'git bisect'
abbrevs['gd'] = 'git diff'
abbrevs['gg'] = 'git grep'
abbrevs['gl'] = 'git log'
abbrevs['glg'] = 'git log --graph --oneline --all'
abbrevs['gln'] = 'git log --graph --oneline -n'
abbrevs['glmn'] = lambda buffer, word: f'git log --graph --oneline -b {$GIT_DEFAULTBRANCH} -n'
abbrevs['gsh'] = 'git show'
abbrevs['gs'] = 'git status'

abbrevs['gb'] = 'git branch'
abbrevs['gc'] = 'git commit -m'
abbrevs['gm'] = 'git merge'
abbrevs['grb'] = 'git rebase'
abbrevs['grst'] = 'git reset'
abbrevs['gsw'] = 'git switch'
abbrevs['gtag'] = 'git tag'

abbrevs['gf'] = 'git fetch'
abbrevs['gpl'] = 'git pull'
abbrevs['gplo'] = 'git pull origin'
abbrevs['gps'] = 'git push'
abbrevs['gpso'] = 'git push origin'

abbrevs['gst'] = 'git stash'
abbrevs['gsm'] = 'git submodule'
abbrevs['grmt'] = 'git remote'

abbrevs['gwt'] = 'git worktree'
