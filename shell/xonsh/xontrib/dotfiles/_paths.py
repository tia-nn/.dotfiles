"""dotfiles と xonsh の設定ファイルの場所。

xonsh は既定で os.environ を更新しないので、xonsh の環境変数を env で受け取る（xsh.env.detype()）。
"""

from collections.abc import Mapping
from pathlib import Path

# shell/xonsh/xontrib/dotfiles/_paths.py → リポジトリの直下
_REPO_ROOT = Path(__file__).resolve().parents[4]


def dotfiles_dir(env: Mapping[str, str]) -> Path:
    """リポジトリの場所。$DOTFILES がなければ、このファイルがあるリポジトリ"""
    return Path(env.get("DOTFILES") or _REPO_ROOT)


def xonsh_dir(env: Mapping[str, str]) -> Path:
    return dotfiles_dir(env) / "shell" / "xonsh"


def state_dir(env: Mapping[str, str]) -> Path:
    """ログなどの状態ファイルを置く場所（$XDG_STATE_HOME/xonsh）"""
    home = Path(env["HOME"]) if env.get("HOME") else Path.home()
    return Path(env.get("XDG_STATE_HOME") or home / ".local" / "state") / "xonsh"
