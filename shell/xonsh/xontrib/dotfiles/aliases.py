"""aliases。xonsh -c やスクリプトの実行でも使えるように、常に読む。"""

from __future__ import annotations

import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from xontrib.dotfiles import xontrib_names
from xontrib.dotfiles._changes import Changes
from xontrib.dotfiles._git import default_branch

if TYPE_CHECKING:
    from xonsh.built_ins import XonshSession

_changes = Changes()

# マージ済みでも消さないブランチ（`git branch` の出力の今のブランチの印 * も含む）
_PROTECTED = re.compile(r"\*|main|master|develop|release")


def git_prune_merged_branch() -> int:
    """デフォルトブランチを最新にして、マージ済みのローカルブランチを消す"""
    branch = default_branch()
    if branch is None:
        print("default branch is unknown; set $GIT_DEFAULTBRANCH or git init.defaultBranch", file=sys.stderr)
        return 1
    for args in (("git", "switch", branch), ("git", "pull", "origin", branch)):
        if subprocess.run(args, check=False).returncode != 0:
            return 1

    merged = subprocess.run(("git", "branch", "--merged"), capture_output=True, text=True, check=False).stdout
    targets = [line.strip() for line in merged.splitlines() if not _PROTECTED.search(line)]
    if targets:
        subprocess.run(("git", "branch", "-d", *targets), check=False)
    subprocess.run(("git", "switch", "-"), check=False)
    return 0


def _load_xontrib_(xsh: XonshSession, **_: Any) -> None:
    def dotfiles_reload() -> None:
        """dotfiles の xontrib を読み込み直す（変更したファイルを反映する）"""
        from xonsh.xontribs import xontribs_reload

        xontribs_reload(xontrib_names(bool(xsh.env.get("XONSH_INTERACTIVE"))))

    _changes.set(xsh.aliases, "git-prune-localbranch", git_prune_merged_branch)
    _changes.set(xsh.aliases, "dotfiles-reload", dotfiles_reload)


def _unload_xontrib_(xsh: XonshSession, **_: Any) -> None:
    _changes.restore()
