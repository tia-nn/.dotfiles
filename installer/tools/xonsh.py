"""xonsh と、rc から読む xontrib を専用の venv に入れ、~/.local/bin/xonsh にリンクする。

venv は ${XDG_DATA_HOME:-~/.local/share}/dotfiles/venvs/xonsh に作る（リポジトリの中には置かない）。
すでに入っているパッケージはそのままにして、足りないものだけを入れる。
更新は `xpip install --upgrade 'xonsh[full]' xontrib-abbrevs xontrib-vox` で行う。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from ..context import Context
from ..links import Link, make_link

PACKAGES = {
    # パッケージ: 入っていれば venv の中にあるファイル（glob）
    "xonsh[full]": "bin/xonsh",
    # shell/xonsh/xontrib/dotfiles/__init__.py の EXTERNAL で読む xontrib
    "xontrib-abbrevs": "lib/python*/site-packages/xontrib/abbrevs.py",
    "xontrib-vox": "lib/python*/site-packages/xontrib/vox.py",
}


def venv_dir(ctx: Context) -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME") or ctx.home / ".local" / "share")
    return data_home / "dotfiles" / "venvs" / "xonsh"


def missing_packages(venv: Path) -> list[str]:
    """PACKAGES のうち、venv にまだ入っていないもの"""
    return [package for package, pattern in PACKAGES.items() if not any(venv.glob(pattern))]


def install(ctx: Context) -> bool:
    venv = venv_dir(ctx)
    python = venv / "bin" / "python"
    xonsh = venv / "bin" / "xonsh"

    missing = missing_packages(venv)
    if not missing:
        ctx.info(f"ok: {venv}")
    else:
        if not python.exists():
            ctx.mkdir(venv.parent)
            # Debian / Ubuntu では python3-venv が必要（install.sh packages で入る）
            if not ctx.run(sys.executable, "-m", "venv", venv):
                return False
            if not ctx.run(python, "-m", "pip", "install", "--upgrade", "pip"):
                return False
        if not ctx.run(python, "-m", "pip", "install", *missing):
            return False

    return make_link(Link(xonsh, ctx.home / ".local" / "bin" / "xonsh"), ctx, require_src=not ctx.dry_run)
