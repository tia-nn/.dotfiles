"""bash / zsh の rc・profile に、dotfiles を読み込むブロックを挿入する。

ファイルごと置き換えず、マーカー付きのブロックだけを挿入・更新する（installer.block）。
"""

from __future__ import annotations

import re
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path

from .block import apply_block
from .context import Context

BASH_LOGIN_FILES = (".bash_profile", ".bash_login", ".profile")
"""bash がログイン時に探す順番。最初に見つかった1つだけを読む"""


@dataclass(frozen=True)
class RcFile:
    path: Path
    script: str
    """ブロックから読み込むスクリプト（リポジトリ内のパス）"""


def dotfiles_expr(dotfiles: Path, home: Path) -> str:
    """ブロックに書く DOTFILES の値。$HOME の下なら "$HOME/..." の形にする"""
    try:
        rel = dotfiles.relative_to(home)
    except ValueError:
        return shlex.quote(str(dotfiles))
    if re.fullmatch(r"[A-Za-z0-9._/-]+", str(rel)):
        return f'"$HOME/{rel}"'
    return shlex.quote(str(dotfiles))


def block_body(script: str, ctx: Context) -> str:
    return f'export DOTFILES={dotfiles_expr(ctx.dotfiles, ctx.home)}\n. "$DOTFILES/{script}"'


def bash_login_file(home: Path) -> Path:
    """bash がログイン時に読むファイル。どれもなければ ~/.profile にする。

    ~/.bash_profile を新しく作ると、bash が ~/.profile（Debian の既定の設定）を読まなくなるので作らない。
    """
    for name in BASH_LOGIN_FILES:
        path = home / name
        if path.exists() or path.is_symlink():
            return path
    return home / ".profile"


def wants_zsh(ctx: Context) -> bool:
    """zsh の設定もするか。mac では常に、Linux では zsh が入っているときだけ"""
    return ctx.os_name == "mac" or shutil.which("zsh") is not None


def rc_files(ctx: Context) -> list[RcFile]:
    """ブロックを挿入するファイルの一覧"""
    files = [
        RcFile(bash_login_file(ctx.home), "shell/bash/profile.sh"),
        RcFile(ctx.home / ".bashrc", "shell/bash/rc.sh"),
    ]
    if wants_zsh(ctx):
        files += [
            RcFile(ctx.home / ".zprofile", "shell/zsh/zprofile.zsh"),
            RcFile(ctx.home / ".zshrc", "shell/zsh/zshrc.zsh"),
        ]
    return files


def setup_shells(ctx: Context) -> bool:
    """bash（と必要なら zsh）の rc・profile にブロックを挿入する。すべて成功したら True"""
    ok = True
    for rc in rc_files(ctx):
        try:
            ok = apply_block(rc.path, block_body(rc.script, ctx), ctx) and ok
        except OSError as e:
            ctx.warn(f"failed to update {rc.path}: {e}")
            ok = False
    return ok
