"""「リポジトリ内のファイル → リンクの置き場所」の対応表。install.sh link がこの一覧どおりにリンクを作る。

Entry(リポジトリ内のパス, リンクの置き場所, os="all" | "linux" | "mac" | "windows")
  - リンクの置き場所の先頭の ~ は $HOME に展開する。
  - os を省略するとすべての OS が対象になる。
"""

from installer.links import Entry

LINKS = [
    # xonsh は ~/.config/xonsh/rc.d の *.py / *.xsh を名前順に読む。入口のファイルだけをリンクし、
    # PC ごとの設定はその後ろの名前（90_local.xsh など）で同じ場所に置けるようにする
    Entry("shell/xonsh/rc.d/50_dotfiles.py", "~/.config/xonsh/rc.d/50_dotfiles.py"),
]
