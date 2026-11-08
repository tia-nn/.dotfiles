"""「リポジトリ内のファイル → リンクの置き場所」の対応表。install.sh link がこの一覧どおりにリンクを作る。

Entry(リポジトリ内のパス, リンクの置き場所, os="all" | "linux" | "mac" | "windows")
  - リンクの置き場所の先頭の ~ は $HOME に展開する。
  - os を省略するとすべての OS が対象になる。
"""

from installer.links import Entry

LINKS = [
    # xonsh は ~/.config/xonsh/rc.d の *.py を名前順に読む（~/.xonshrc は PC ごとの設定用に空けておく）
    Entry("shell/xonsh/rc.d", "~/.config/xonsh/rc.d"),
    Entry("apps/hyper_linux.js", "~/.hyper.js", os="linux"),
    Entry("apps/hyper_mac.js", "~/.hyper.js", os="mac"),
]
