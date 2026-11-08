"""xonsh と、rc から読む xontrib を専用の venv に入れ、~/.local/bin/xonsh にリンクする。

venv は ${XDG_DATA_HOME:-~/.local/share}/dotfiles/venvs/xonsh に作る（リポジトリの中には置かない）。
venv の Python は、install.sh を動かしている Python ではなく、asdf で入れた全体の既定の Python
（~/.tool-versions の python）を使う。xonsh は最新の Python で動かしたいが、install.sh は
mac の Command Line Tools の python3（3.9）でも動くようにしているため。
tools では asdf が xonsh より先に動くので、新しい PC でもこの時点で入っている。

すでに入っているパッケージはそのままにして、足りないものだけを入れる。
更新は `xpip install --upgrade 'xonsh[full]' xontrib-abbrevs xontrib-vox` で行う。
asdf の Python のバージョンを上げたときは、venv を消してから入れ直す。
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from ..context import Context
from ..links import Link, make_link
from . import asdf

MIN_PYTHON = (3, 11)
"""xonsh 0.25 が必要とする Python"""
MIN_PYTHON_TEXT = ".".join(map(str, MIN_PYTHON))

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


def parse_version(text: str) -> tuple[int, int] | None:
    """"3.14.2" などの先頭の major.minor。読めなければ None"""
    match = re.match(r"(\d+)\.(\d+)", text)
    return (int(match[1]), int(match[2])) if match else None


def venv_python_version(venv: Path) -> tuple[int, int] | None:
    """venv を作った Python のバージョン（pyvenv.cfg の version）"""
    cfg = venv / "pyvenv.cfg"
    if not cfg.is_file():
        return None
    for line in cfg.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        if key.strip() in ("version", "version_info"):
            return parse_version(value.strip())
    return None


def base_python(ctx: Context) -> Path | None:
    """venv を作る Python（asdf の全体の既定の Python）。決められなければ警告を出して None"""
    version = asdf.global_versions(ctx).get("python")
    if version is None:
        if ctx.dry_run:
            # dry-run では asdf がまだ Python を入れていないので、決まっていないものとして表示する
            return Path("<python in ~/.tool-versions>")
        ctx.warn("xonsh: no python in ~/.tool-versions; run `install.sh tools asdf` first")
        return None
    parsed = parse_version(version)
    if parsed is None or parsed < MIN_PYTHON:
        ctx.warn(
            f"xonsh: python {version} in ~/.tool-versions is too old; {MIN_PYTHON_TEXT} or later is required"
        )
        return None
    python = asdf.data_dir(ctx) / "installs" / "python" / version / "bin" / "python3"
    if not python.exists() and not ctx.dry_run:
        ctx.warn(f"xonsh: {python} not found; run `install.sh tools asdf` first")
        return None
    return python


def install(ctx: Context) -> bool:
    venv = venv_dir(ctx)
    python = venv / "bin" / "python"
    xonsh = venv / "bin" / "xonsh"

    old = venv_python_version(venv)
    if old is not None and old < MIN_PYTHON:
        ctx.warn(
            f"xonsh: {venv} uses python {old[0]}.{old[1]}, but {MIN_PYTHON_TEXT} or later is required. "
            "Remove the venv and run again"
        )
        return False

    missing = missing_packages(venv)
    if not missing:
        ctx.info(f"ok: {venv}")
    else:
        if not python.exists():
            base = base_python(ctx)
            if base is None:
                return False
            ctx.mkdir(venv.parent)
            if not ctx.run(base, "-m", "venv", venv):
                return False
            if not ctx.run(python, "-m", "pip", "install", "--upgrade", "pip"):
                return False
        if not ctx.run(python, "-m", "pip", "install", *missing):
            return False

    return make_link(Link(xonsh, ctx.home / ".local" / "bin" / "xonsh"), ctx, require_src=not ctx.dry_run)
