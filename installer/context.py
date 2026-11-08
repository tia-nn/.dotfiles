"""実行時の情報と、ファイルを変更する操作の窓口。

ファイルを変更する操作はすべてここを通す。dry-run のときは、実行する操作を表示するだけで何も変更しない。
"""

from __future__ import annotations

import os
import shlex
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO


@dataclass
class Context:
    dotfiles: Path
    """リポジトリの場所"""
    home: Path
    os_name: str
    """linux / mac"""
    backup_dir: Path
    """置き換えるファイルの退避先（実行ごとに別のディレクトリ）"""
    dry_run: bool = False
    out: TextIO = field(default_factory=lambda: sys.stdout)
    err: TextIO = field(default_factory=lambda: sys.stderr)

    # --- 出力 ---

    def info(self, message: str) -> None:
        print(message, file=self.out)

    def warn(self, message: str) -> None:
        print(f"warning: {message}", file=self.err)

    def _announce(self, *args: str | Path) -> bool:
        """操作を表示し、実際に実行してよければ True を返す"""
        line = shlex.join(str(arg) for arg in args)
        if self.dry_run:
            self.info(f"[dry-run] {line}")
            return False
        self.info(f"+ {line}")
        return True

    # --- ファイル操作 ---

    def mkdir(self, path: Path) -> None:
        if path.is_dir():
            return
        if self._announce("mkdir", "-p", path):
            path.mkdir(parents=True, exist_ok=True)

    def move(self, src: Path, dest: Path) -> None:
        if self._announce("mv", src, dest):
            os.rename(src, dest)

    def copy(self, src: Path, dest: Path) -> None:
        if self._announce("cp", "-p", src, dest):
            shutil.copy2(src, dest)

    def symlink(self, target: Path, link: Path) -> None:
        if self._announce("ln", "-s", target, link):
            link.symlink_to(target)

    def write_text(self, path: Path, text: str) -> None:
        """path の中身を書き換える。path がリンクならリンク先を書き換え、リンクのまま保つ"""
        if self.dry_run:
            return
        with path.open("w", encoding="utf-8") as f:
            f.write(text)

    # --- 退避 ---

    def backup_path(self, path: Path) -> Path:
        """path の退避先を返す。

        backup_dir の下に $HOME からの相対パスで置く。
        同じ場所にすでに退避したものがあれば、上書きしないように .1, .2, ... を付ける。
        """
        try:
            base = self.backup_dir / path.relative_to(self.home)
        except ValueError:
            base = self.backup_dir / "_root" / path.relative_to(path.anchor)
        candidate, n = base, 0
        while candidate.exists() or candidate.is_symlink():
            n += 1
            candidate = base.with_name(f"{base.name}.{n}")
        return candidate
