"""フォントを入れる。

- 源ノ角ゴシック Code（Source Han Code JP）: https://github.com/adobe-fonts/source-han-code-jp
- Nerd Fonts Symbols Only: https://github.com/ryanoasis/nerd-fonts （アイコン用）

置き場所は Linux が ${XDG_DATA_HOME:-~/.local/share}/fonts/dotfiles、mac が ~/Library/Fonts。
どちらも毎回最新のリリースをダウンロードして上書きする（実行すれば最新版になる）。
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from ..archive import extract_zip_files
from ..context import Context

# releases/latest/download/ は最新のリリースのアセットに転送される（API を使わないので回数制限もない）
SOURCE_HAN_CODE_JP = (
    "https://github.com/adobe-fonts/source-han-code-jp/releases/latest/download/SourceHanCodeJP.ttc"
)
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

    # 途中で失敗しても、今あるファイルは壊さない（ctx.download は置き換えるときだけ書き込む）
    ctx.download(SOURCE_HAN_CODE_JP, fonts / "SourceHanCodeJP.ttc")

    if ctx.dry_run:
        ctx.announce("unzip", "NerdFontsSymbolsOnly.zip", "*.ttf", "-d", fonts)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "NerdFontsSymbolsOnly.zip"
            ctx.download(NERD_FONTS_SYMBOLS, archive)
            ctx.announce("unzip", archive, "*.ttf", "-d", fonts)
            extract_zip_files(archive, fonts, ".ttf")

    # Linux はフォントのキャッシュを作り直す（mac は不要）
    if ctx.os_name == "linux" and shutil.which("fc-cache"):
        return ctx.run("fc-cache", "-f", fonts)
    return True
