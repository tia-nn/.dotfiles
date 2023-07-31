def _xonshrc_aliases():
    from lib.git import get_git_defaultbranch, get_current_branch

    def git_prune_merged_branch():
        git switch @(get_git_defaultbranch())
        git pull origin @(get_git_defaultbranch())
        git branch --merged | egrep --invert-match r'\\*|main|master|develop|release' | xargs git branch -d
        git switch -

    def measure_xonshrc_time_performance():
        import time

        start = time.monotonic()
        for f in `~/.dotfiles/xonsh/.*[.](xsh|py)`:
            before = time.monotonic()
            source @(f)
            after = time.monotonic()
            print(f'{f}: {after - before} ms.')
        end = time.monotonic()
        print(f'all: {end - start}')

    aliases['git-prune-localbranch'] = git_prune_merged_branch
    aliases['measure-xonshrc-time-performance'] = measure_xonshrc_time_performance

_xonshrc_aliases()


aliases['xpython'] = aliases['xpip'][1] if aliases['xpip'][0] == 'sudo' \
                else aliases['xpip'][0]
