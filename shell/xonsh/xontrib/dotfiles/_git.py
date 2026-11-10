"""abbrevs や aliases から使う git の情報。

xonsh は既定で os.environ を更新しない（$UPDATE_OS_ENVIRON）ので、xonsh の環境変数を env で受け取る
（xsh.env.detype()）。git もこの環境変数で実行する（env.sh で足した PATH の git を使う）。
"""

import subprocess
from collections.abc import Mapping

PROTECTED = frozenset({"main", "master", "develop"})
"""マージ済みでも消さないブランチ（ほかに release で始まるもの）"""


def git(env: Mapping[str, str], *args: str) -> str | None:
    """git ARGS... の標準出力を返す。失敗したら（git がない場合も）None"""
    try:
        result = subprocess.run(("git", *args), capture_output=True, text=True, env=dict(env), check=False)
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.rstrip()


def default_branch(env: Mapping[str, str]) -> str | None:
    """デフォルトブランチ名。$GIT_DEFAULTBRANCH、git の init.defaultBranch の順に探す"""
    return env.get("GIT_DEFAULTBRANCH") or git(env, "config", "init.defaultBranch")


def current_branch(env: Mapping[str, str]) -> str | None:
    """今のブランチ名"""
    return git(env, "rev-parse", "--abbrev-ref", "HEAD")


def is_protected(branch: str) -> bool:
    return branch in PROTECTED or branch.startswith("release")


def merged_branches(env: Mapping[str, str]) -> list[str] | None:
    """HEAD にマージ済みで、消してよいローカルブランチ。git が失敗したら None。

    守るブランチ（PROTECTED と release で始まるもの）と、今のブランチを含めて
    いずれかの worktree で使っているブランチは除く。
    """
    fmt = "--format=%(worktreepath)\t%(refname:short)"
    out = git(env, "for-each-ref", "--merged=HEAD", fmt, "refs/heads/")
    if out is None:
        return None
    branches = []
    for line in out.splitlines():
        worktree, _, branch = line.partition("\t")
        if branch and not worktree and not is_protected(branch):
            branches.append(branch)
    return branches
