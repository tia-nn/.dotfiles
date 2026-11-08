"""ダウンロードしたアーカイブの展開。展開先の外にファイルを書かないことを確かめる。"""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path


def _check_inside(dest: Path, name: str) -> None:
    target = (dest / name).resolve()
    if not target.is_relative_to(dest.resolve()):
        raise ValueError(f"unsafe path in archive: {name}")


def extract_tar(archive: Path, dest: Path) -> None:
    """tar.gz などを dest に展開する"""
    with tarfile.open(archive) as tar:
        if hasattr(tarfile, "data_filter"):
            # Python 3.12 以降（と一部の 3.9〜3.11 の更新版）は標準の安全な展開を使う
            tar.extractall(dest, filter="data")
            return
        for member in tar.getmembers():
            _check_inside(dest, member.name)
            if member.islnk():
                # ハードリンクの linkname はアーカイブのルートから見たパス
                _check_inside(dest, member.linkname)
            elif member.issym():
                _check_inside(dest, str(Path(member.name).parent / member.linkname))
            if member.isdev():
                raise ValueError(f"device file in archive: {member.name}")
        tar.extractall(dest)  # 上で確認済み


def extract_zip_files(archive: Path, dest: Path, suffix: str) -> list[Path]:
    """zip のうち suffix で終わるファイルだけを、ディレクトリ構造を無視して dest に置く"""
    written = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            name = Path(info.filename).name
            if info.is_dir() or not name.endswith(suffix):
                continue
            path = dest / name
            path.write_bytes(zf.read(info))
            written.append(path)
    return written
