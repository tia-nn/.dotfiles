"""テストで使う小さな関数。"""

from __future__ import annotations

import io
import os
from pathlib import Path

from installer.context import Context

REPO_ROOT = Path(__file__).resolve().parent.parent


def output(ctx: Context) -> str:
    assert isinstance(ctx.out, io.StringIO)
    return ctx.out.getvalue()


def errors(ctx: Context) -> str:
    assert isinstance(ctx.err, io.StringIO)
    return ctx.err.getvalue()


def snapshot(root: Path) -> list[str]:
    """root 配下のファイル・リンク・中身の一覧（変更がないことの確認用）"""
    entries = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_symlink():
            entries.append(f"{rel} -> {os.readlink(path)}")
        elif path.is_file():
            entries.append(f"{rel} {path.read_bytes()!r}")
        else:
            entries.append(f"{rel}/")
    return entries
