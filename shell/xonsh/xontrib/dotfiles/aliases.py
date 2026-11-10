"""aliases。xonsh -c やスクリプトの実行でも使えるように、常に読む。"""

import subprocess
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from xonsh.tools import uncapturable, unthreadable

from xontrib.dotfiles import xontrib_names
from xontrib.dotfiles._changes import Changes
from xontrib.dotfiles._git import default_branch, merged_branches

if TYPE_CHECKING:
    from xonsh.built_ins import XonshSession

_changes = Changes()


def on_terminal[F: Callable[..., Any]](func: F) -> F:
    """端末を直接使う alias にする（メインスレッドで動かし、出力を取り込まない）。

    git pull が認証を尋ねるときなどに、確実に端末で受けられるようにする。
    """
    # xonsh のデコレータは属性を付けるだけで、func をそのまま返す（型情報がないので包む）
    uncapturable(unthreadable(func))
    return func


def _load_xontrib_(xsh: XonshSession, **_: Any) -> None:
    @on_terminal
    def git_prune_localbranch() -> int:
        """デフォルトブランチを最新にして、マージ済みのローカルブランチを消す"""
        env = xsh.env.detype()
        branch = default_branch(env)
        if branch is None:
            print(
                "default branch is unknown; set $GIT_DEFAULTBRANCH or git init.defaultBranch", file=sys.stderr
            )
            return 1
        for args in (("git", "switch", branch), ("git", "pull", "origin", branch)):
            if subprocess.run(args, env=env, check=False).returncode != 0:
                return 1

        targets = merged_branches(env)
        if targets is None:
            return 1
        if targets:
            subprocess.run(("git", "branch", "-d", *targets), env=env, check=False)
        subprocess.run(("git", "switch", "-"), env=env, check=False)
        return 0

    def dotfiles_reload() -> None:
        """dotfiles の xontrib を読み込み直す（変更したファイルを反映する）"""
        from xonsh.xontribs import xontribs_reload

        xontribs_reload(xontrib_names(bool(xsh.env.get("XONSH_INTERACTIVE"))))

    _changes.set(xsh.aliases, "git-prune-localbranch", git_prune_localbranch)
    _changes.set(xsh.aliases, "dotfiles-reload", dotfiles_reload)


def _unload_xontrib_(xsh: XonshSession, **_: Any) -> None:
    _changes.restore()
