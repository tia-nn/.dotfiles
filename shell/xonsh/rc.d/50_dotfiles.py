"""dotfiles の xonsh の設定の入口。install.sh link で ~/.config/xonsh/rc.d/50_dotfiles.py にリンクする。

リンクをたどった先から shell/xonsh を import できるようにして、設定（xontrib/dotfiles）を読み込む。
PC ごとの設定は ~/.config/xonsh/rc.d に、これより後の名前（90_local.xsh など）で置く。

rc ファイルはシェルと同じ名前空間で実行されるので、名前が残らないよう関数の中に書く。
"""


def _dotfiles_rc():
    import sys
    from pathlib import Path

    from xonsh.built_ins import XSH
    from xonsh.xontribs import xontribs_load

    xonsh_dir = str(Path(__file__).resolve().parent.parent)
    if xonsh_dir not in sys.path:
        sys.path.insert(0, xonsh_dir)

    from xontrib.dotfiles import EXTERNAL, xontrib_names

    interactive = bool(XSH.env.get("XONSH_INTERACTIVE"))
    if interactive:
        _, err, _ = xontribs_load(EXTERNAL)
        if err:
            print(err, file=sys.stderr, end="")
    xontribs_load(xontrib_names(interactive))


_dotfiles_rc()
