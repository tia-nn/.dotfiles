def _xonshrc_env_path():
    import os
    from pathlib import Path

    from xonsh.built_ins import XSH

    # 共通層（PATH と環境変数）を読む。重複は env.sh の側で取り除く
    dotfiles = os.environ.get('DOTFILES') or str(Path.home() / '.dotfiles')
    XSH.env['DOTFILES'] = dotfiles
    XSH.aliases['source-bash'](['--suppress-skip-message',
                               str(Path(dotfiles) / 'shell' / 'common' / 'env.sh')])


_xonshrc_env_path()
