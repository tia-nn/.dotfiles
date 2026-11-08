"""実行時の情報と、ファイルを変更する操作の窓口。

ファイルを変更する操作はすべてここを通す。dry-run のときは、実行する操作を表示するだけで何も変更しない。
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import urllib.request
from collections.abc import Mapping
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

    def announce(self, *args: str | Path) -> bool:
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
        if self.announce("mkdir", "-p", path):
            path.mkdir(parents=True, exist_ok=True)

    def move(self, src: Path, dest: Path) -> None:
        if self.announce("mv", src, dest):
            os.rename(src, dest)

    def copy(self, src: Path, dest: Path) -> None:
        if self.announce("cp", "-p", src, dest):
            shutil.copy2(src, dest)

    def symlink(self, target: Path, link: Path) -> None:
        if self.announce("ln", "-s", target, link):
            link.symlink_to(target)

    def run(self, *args: str | Path, env: Mapping[str, str] | None = None) -> bool:
        """外部コマンドを実行する。成功したら（dry-run なら常に）True。env は環境変数をまるごと指定する"""
        if not self.announce(*args):
            return True
        try:
            result = subprocess.run([str(arg) for arg in args], env=env, check=False)
        except OSError as e:
            self.warn(f"failed to run {args[0]}: {e}")
            return False
        if result.returncode != 0:
            self.warn(f"command failed with exit code {result.returncode}: {shlex.join(map(str, args))}")
            return False
        return True

    def download(self, url: str, dest: Path) -> None:
        """url を dest に保存する。途中で失敗しても dest に中途半端なファイルを残さない"""
        if not self.announce("curl", "-fsSL", "-o", dest, url):
            return
        tmp = dest.with_name(dest.name + ".part")
        try:
            with urllib.request.urlopen(url, timeout=60) as response, tmp.open("wb") as f:
                shutil.copyfileobj(response, f)
            os.replace(tmp, dest)
        finally:
            tmp.unlink(missing_ok=True)

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
