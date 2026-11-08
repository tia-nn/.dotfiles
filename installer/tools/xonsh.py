"""xonsh を専用の venv に入れ、~/.local/bin/xonsh にリンクする。

venv は ${XDG_DATA_HOME:-~/.local/share}/dotfiles/venvs/xonsh に作る（リポジトリの中には置かない）。
更新は `xpip install --upgrade 'xonsh[full]'` で行う（このツールは、すでにあれば何もしない）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from ..context import Context
from ..links import Link, make_link

PACKAGE = "xonsh[full]"


def venv_dir(ctx: Context) -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME") or ctx.home / ".local" / "share")
    return data_home / "dotfiles" / "venvs" / "xonsh"


def install(ctx: Context) -> bool:
    venv = venv_dir(ctx)
    python = venv / "bin" / "python"
    xonsh = venv / "bin" / "xonsh"

    if xonsh.exists():
        ctx.info(f"ok: {xonsh}")
    else:
        if not python.exists():
            ctx.mkdir(venv.parent)
            # Debian / Ubuntu では python3-venv が必要（install.sh packages で入る）
            if not ctx.run(sys.executable, "-m", "venv", venv):
                return False
        if not ctx.run(python, "-m", "pip", "install", "--upgrade", "pip"):
            return False
        if not ctx.run(python, "-m", "pip", "install", PACKAGE):
            return False

    return make_link(Link(xonsh, ctx.home / ".local" / "bin" / "xonsh"), ctx, require_src=not ctx.dry_run)
