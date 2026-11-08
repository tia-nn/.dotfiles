"""abbrevs や aliases から使う git の情報。"""

from __future__ import annotations

import os
import subprocess


def _git(*args: str) -> str | None:
    """git ARGS... の標準出力を返す。失敗したら（git がない場合も）None"""
    try:
        result = subprocess.run(("git", *args), capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.rstrip()


def default_branch() -> str | None:
    """デフォルトブランチ名。$GIT_DEFAULTBRANCH、git の init.defaultBranch の順に探す"""
    return os.environ.get("GIT_DEFAULTBRANCH") or _git("config", "init.defaultBranch")


def current_branch() -> str | None:
    """今のブランチ名"""
    return _git("rev-parse", "--abbrev-ref", "HEAD")
