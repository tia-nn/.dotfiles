def _xonshrc_env_path():
    from xonsh.tools import EnvPath
    from xonsh.tools import EnvPath
    from xonsh.built_ins import XSH

    from lib.typing_builtins import env, aliases, env_path

    aliases['source-bash'](['--suppress-skip-message',
                               '~/.dotfiles/sh/paths'])

    # delete duplicated
    env['PATH'] = EnvPath(sorted(set(env_path), key=env_path.index))


_xonshrc_env_path()
