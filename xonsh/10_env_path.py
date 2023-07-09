def _xonshrc_env_path():
    from xonsh.tools import EnvPath
    from xonsh.tools import EnvPath
    from xonsh.built_ins import XSH

    env = XSH.env
    path = env['PATH']

    XSH.aliases['source-bash'](['--suppress-skip-message',
                               '~/.dotfiles/sh/paths'])

    # delete duplicated
    env['PATH'] = EnvPath(sorted(set(path), key=path.index))


_xonshrc_env_path()
