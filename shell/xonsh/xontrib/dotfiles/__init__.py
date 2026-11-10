"""dotfiles の xonsh の設定。

xonsh の名前空間パッケージ xontrib の下に置き、各モジュールを xontrib として読む
（`xontrib load dotfiles.<名前>`）。`_` で始まるモジュールは、xontrib から使う補助。
"""

ALWAYS = ("env", "aliases")
"""xonsh -c やスクリプトの実行でも読む"""
INTERACTIVE = ("prompt", "abbrevs", "envstack")
"""対話シェルだけで読む"""
EXTERNAL = ("abbrevs", "vox")
"""対話シェルで、dotfiles の xontrib より先に読む外部の xontrib（install.sh tools xonsh で入れる）"""


def xontrib_names(interactive: bool) -> list[str]:
    """読み込む dotfiles の xontrib の名前（`dotfiles.env` など）を、読む順に返す"""
    names = ALWAYS + INTERACTIVE if interactive else ALWAYS
    return [f"dotfiles.{name}" for name in names]
