def _xonshrc_aliases():
    import re
    import subprocess
    import sys
    import time

    from xonsh.built_ins import XSH

    from xontrib.dotfiles._git import default_branch
    from xontrib.dotfiles._paths import rc_files

    # マージ済みでも消さないブランチ
    protected = re.compile(r'\*|main|master|develop|release')

    def git_prune_merged_branch():
        """デフォルトブランチを最新にして、マージ済みのローカルブランチを消す"""
        branch = default_branch()
        if branch is None:
            print('default branch is unknown; set $GIT_DEFAULTBRANCH or git init.defaultBranch',
                  file=sys.stderr)
            return 1
        for args in (('git', 'switch', branch), ('git', 'pull', 'origin', branch)):
            if subprocess.run(args, check=False).returncode != 0:
                return 1

        merged = subprocess.run(('git', 'branch', '--merged'),
                                capture_output=True, text=True, check=False).stdout
        targets = [line.strip() for line in merged.splitlines() if not protected.search(line)]
        if targets:
            subprocess.run(('git', 'branch', '-d', *targets), check=False)
        subprocess.run(('git', 'switch', '-'), check=False)
        return 0

    def measure_xonshrc_time_performance():
        """rc.d のファイルごとに読み込みにかかる時間を表示する"""
        start = time.monotonic()
        for rc in rc_files():
            before = time.monotonic()
            XSH.aliases['source']([str(rc)])
            print(f'{rc.name}: {(time.monotonic() - before) * 1000:.1f} ms')
        print(f'all: {(time.monotonic() - start) * 1000:.1f} ms')

    XSH.aliases['git-prune-localbranch'] = git_prune_merged_branch
    XSH.aliases['measure-xonshrc-time-performance'] = measure_xonshrc_time_performance


_xonshrc_aliases()
