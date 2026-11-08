"""フォントを入れる。

- 源ノ角ゴシック Code（Source Han Code JP）: https://github.com/adobe-fonts/source-han-code-jp
- Nerd Fonts Symbols Only: https://github.com/ryanoasis/nerd-fonts （アイコン用。最新のリリースから取る）

置き場所は Linux が ${XDG_DATA_HOME:-~/.local/share}/fonts/dotfiles、mac が ~/Library/Fonts。
すでにあるものはダウンロードしない。
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from ..archive import extract_zip_files
from ..context import Context

SOURCE_HAN_CODE_JP = (
    "https://github.com/adobe-fonts/source-han-code-jp/releases/download/2.012R/SourceHanCodeJP.ttc"
)
# releases/latest/download/ は最新のリリースのアセットに転送される（API を使わないので回数制限もない）
NERD_FONTS_SYMBOLS = (
    "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/NerdFontsSymbolsOnly.zip"
)


def font_dir(ctx: Context) -> Path:
    if ctx.os_name == "mac":
        return ctx.home / "Library" / "Fonts"
    data_home = Path(os.environ.get("XDG_DATA_HOME") or ctx.home / ".local" / "share")
    return data_home / "fonts" / "dotfiles"


def install(ctx: Context) -> bool:
    fonts = font_dir(ctx)
    ctx.mkdir(fonts)
    changed = False

    ttc = fonts / "SourceHanCodeJP.ttc"
    if ttc.exists():
        ctx.info(f"ok: {ttc}")
    else:
        ctx.download(SOURCE_HAN_CODE_JP, ttc)
        changed = True

    if any(fonts.glob("SymbolsNerdFont*.ttf")):
        ctx.info(f"ok: {fonts}/SymbolsNerdFont*.ttf")
    elif ctx.dry_run:
        ctx.announce("unzip", "NerdFontsSymbolsOnly.zip", "*.ttf", "-d", fonts)
        changed = True
    else:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "NerdFontsSymbolsOnly.zip"
            ctx.download(NERD_FONTS_SYMBOLS, archive)
            ctx.announce("unzip", archive, "*.ttf", "-d", fonts)
            extract_zip_files(archive, fonts, ".ttf")
        changed = True

    # Linux はフォントのキャッシュを作り直す（mac は不要）
    if changed and ctx.os_name == "linux" and shutil.which("fc-cache"):
        return ctx.run("fc-cache", "-f", fonts)
    return True
