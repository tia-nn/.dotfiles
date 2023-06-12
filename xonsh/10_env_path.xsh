def _xonshrc_env_path():
    from xonsh.tools import EnvPath

    source-bash --suppress-skip-message ~/.dotfiles/sh/paths
    $PATH = EnvPath(sorted(set($PATH), key=$PATH.index))  # delete duplicated


_xonshrc_env_path()
