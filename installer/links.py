"""リンクの対応表（リポジトリ直下の links.py）の読み込みと、シンボリックリンクの作成。"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

from .context import Context

TargetOS = Literal["all", "linux", "mac", "windows"]
"""Entry の対象 OS"""

OS_NAMES: tuple[TargetOS, ...] = get_args(TargetOS)


@dataclass(frozen=True)
class Entry:
    """対応表の1行。links.py に書く"""

    src: str
    """リポジトリ内のパス"""
    dest: str
    """リンクの置き場所。先頭の ~ は $HOME に展開する"""
    os: TargetOS = "all"
    """対象の OS"""

    def __post_init__(self) -> None:
        # 型は mypy で確認できるが、links.py は実行時に読み込むので値も確認する
        if self.os not in OS_NAMES:
            raise ValueError(f"unknown OS {self.os!r} for {self.src!r} (expected one of {OS_NAMES})")
        if not self.src or not self.dest:
            raise ValueError(f"src and dest must not be empty: {self!r}")
        if Path(self.src).is_absolute():
            raise ValueError(f"src must be relative to the repository: {self.src!r}")


@dataclass(frozen=True)
class Link:
    """今の環境で作るリンク（どちらも絶対パス）"""

    src: Path
    dest: Path


def expand_home(path: str, home: Path) -> Path:
    """先頭の ~ だけを home に展開する"""
    if path == "~":
        return home
    if path.startswith("~/"):
        return home / path[2:]
    return Path(path)


def load_entries(path: Path) -> list[Entry]:
    """links.py を読み込んで LINKS を返す"""
    spec = importlib.util.spec_from_file_location("dotfiles_links", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    entries = getattr(module, "LINKS", None)
    if not isinstance(entries, list) or not all(isinstance(e, Entry) for e in entries):
        raise ValueError(f"{path}: LINKS must be a list of Entry")
    return entries


def resolve(entries: list[Entry], *, os_name: str, dotfiles: Path, home: Path) -> list[Link]:
    """entries のうち os_name に当てはまるものを、絶対パスの Link にして返す"""
    return [
        Link(dotfiles / e.src, expand_home(e.dest, home)) for e in entries if e.os in ("all", os_name)
    ]


def make_link(link: Link, ctx: Context) -> bool:
    """link.dest を link.src へのシンボリックリンクにする。成功したら True を返す。

    すでに正しいリンクなら何もしない。別のファイルやリンクがあれば退避してから置き換える。
    """
    src, dest = link.src, link.dest
    if not src.exists():
        ctx.warn(f"source not found: {src}")
        return False
    if dest.is_symlink() and Path(os.readlink(dest)) == src:
        ctx.info(f"ok: {dest}")
        return True
    if dest.exists() or dest.is_symlink():
        backup = ctx.backup_path(dest)
        ctx.mkdir(backup.parent)
        ctx.move(dest, backup)
    ctx.mkdir(dest.parent)
    ctx.symlink(src, dest)
    return True


def link_all(entries: list[Entry], ctx: Context) -> bool:
    """entries のうち、今の OS に当てはまるものをすべてリンクする。すべて成功したら True"""
    ok = True
    for link in resolve(entries, os_name=ctx.os_name, dotfiles=ctx.dotfiles, home=ctx.home):
        try:
            ok = make_link(link, ctx) and ok
        except OSError as e:
            ctx.warn(f"failed to link {link.dest}: {e}")
            ok = False
    return ok
