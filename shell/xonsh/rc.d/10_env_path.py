def _xonshrc_env_path():
    from xonsh.built_ins import XSH

    from lib.paths import dotfiles_dir

    # 共通層（PATH と環境変数）を読む。重複は env.sh の側で取り除く
    dotfiles = dotfiles_dir()
    XSH.env['DOTFILES'] = str(dotfiles)
    XSH.aliases['source-bash'](['--suppress-skip-message',
                               str(dotfiles / 'shell' / 'common' / 'env.sh')])


_xonshrc_env_path()
