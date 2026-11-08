"""dotfiles の xonsh の設定の入口。install.sh link で ~/.config/xonsh/rc.d/50_dotfiles.py にリンクする。

リンクをたどった先から shell/xonsh を import できるようにして、設定を読み込む。
PC ごとの設定は ~/.config/xonsh/rc.d に、これより後の名前（90_local.xsh など）で置く。
"""


def _dotfiles_rc():
    import sys
    from pathlib import Path

    from xonsh.built_ins import XSH
    from xonsh.environ import xonshrc_context

    here = Path(__file__).resolve()
    xonsh_dir = str(here.parent.parent)
    if xonsh_dir not in sys.path:
        sys.path.insert(0, xonsh_dir)

    # 移行中: まだ xontrib に移していない rc.d の残りのファイルを、xonsh が rc.d を読むのと同じ方法で読む
    rest = [str(p) for p in sorted(here.parent.glob("*.py")) if p != here]
    xonshrc_context(rcfiles=rest, execer=XSH.execer, ctx=XSH.ctx, env=XSH.env,
                    login=bool(XSH.env.get("XONSH_LOGIN")))


_dotfiles_rc()
