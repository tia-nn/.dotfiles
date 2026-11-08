"""shell/xonsh/lib を import できるようにする。rc.d の中で最初に読む。

~/.config/xonsh/rc.d はリポジトリの rc.d へのリンクなので、リンクをたどった先から場所を決める。
"""


def _xonshrc_import_path():
    import sys
    from pathlib import Path

    xonsh_dir = str(Path(__file__).resolve().parent.parent)
    if xonsh_dir not in sys.path:
        sys.path.insert(0, xonsh_dir)


_xonshrc_import_path()
