import os
import subprocess


def get_git_defaultbranch():
    if (b := os.getenv('GIT_DEFAULTBRANCH')):
        return b
    if (git_conf := subprocess.run(('git', 'config', 'init.defaultBranch'), capture_output=True)).returncode == 0:
        return git_conf.stdout.decode().rstrip()
    else:
        return '<edit>'

def get_current_branch():
    if (r := subprocess.run(('git', 'rev-parse', '--abbrev-ref', 'HEAD'), capture_output=True)).returncode == 0:
        return r.stdout.decode().rstrip()
    else:
        return '<edit>'
