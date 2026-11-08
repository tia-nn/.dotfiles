"""rc / profile へのマーカー付きブロックの挿入・更新・削除。

ファイルごと置き換えないので、ディストリビューション既定の設定はそのまま残る。
"""

from __future__ import annotations

import difflib
from pathlib import Path

from .context import Context

BEGIN = "# >>> dotfiles >>>"
END = "# <<< dotfiles <<<"


class UnterminatedBlockError(ValueError):
    """BEGIN に対応する END がない"""


def render(text: str, body: str) -> str:
    """text のブロックの中身を body に置き換えた文字列を返す。

    - ブロックがなければ末尾に追加する（前の行が空でなければ空行を1つ挟む）。
    - body が空ならブロックを削除する。
    - ブロックが複数あれば、最初の位置に1つだけ残す。
    """
    lines = text.splitlines()
    block = [BEGIN, *body.splitlines(), END] if body else []

    result: list[str] = []
    inserted = False
    i = 0
    while i < len(lines):
        if lines[i] == BEGIN:
            try:
                end = lines.index(END, i + 1)
            except ValueError:
                raise UnterminatedBlockError(f"'{BEGIN}' without '{END}'") from None
            if not inserted:
                result.extend(block)
                inserted = True
            i = end + 1
            continue
        result.append(lines[i])
        i += 1

    if not inserted:
        if not block:
            return text
        if result and result[-1] != "":
            result.append("")
        result.extend(block)
    return "".join(line + "\n" for line in result)


def apply_block(path: Path, body: str, ctx: Context) -> bool:
    """path のブロックの中身を body にする（body が空なら削除）。成功したら True を返す。

    変更があるときだけ、path を退避してから書き換える。dry-run では差分を表示するだけ。
    """
    old = path.read_text(encoding="utf-8") if path.exists() else None
    try:
        new = render(old or "", body)
    except UnterminatedBlockError as e:
        ctx.warn(f"{path}: {e}; not modified")
        return False

    if (old or "") == new:
        ctx.info(f"ok: {path}")
        return True

    if ctx.dry_run:
        ctx.info(f"[dry-run] update block in {path}")
        diff = difflib.unified_diff(
            (old or "").splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=str(path) if old is not None else "/dev/null",
            tofile=str(path),
        )
        for line in diff:
            ctx.info("    " + line.rstrip("\n"))
        return True

    if old is not None:
        backup = ctx.backup_path(path)
        ctx.mkdir(backup.parent)
        ctx.copy(path, backup)
    else:
        ctx.mkdir(path.parent)
    ctx.write_text(path, new)
    ctx.info(f"updated: {path}")
    return True


def remove_block(path: Path, ctx: Context) -> bool:
    """path からブロックを削除する"""
    return apply_block(path, "", ctx)
