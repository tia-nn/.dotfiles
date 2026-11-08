"""dotfiles と xonsh の設定ファイルの場所。"""

from __future__ import annotations

import os
from pathlib import Path

# shell/xonsh/xontrib/dotfiles/_paths.py → リポジトリの直下
_REPO_ROOT = Path(__file__).resolve().parents[4]


def dotfiles_dir() -> Path:
    """リポジトリの場所。$DOTFILES がなければ、このファイルがあるリポジトリ"""
    return Path(os.environ.get("DOTFILES") or _REPO_ROOT)


def xonsh_dir() -> Path:
    return dotfiles_dir() / "shell" / "xonsh"


def state_dir() -> Path:
    """ログなどの状態ファイルを置く場所（$XDG_STATE_HOME/xonsh）"""
    state_home = os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state"
    return Path(state_home) / "xonsh"
