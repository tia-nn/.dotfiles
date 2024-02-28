from typing import cast
import warnings

from xonsh.built_ins import XSH
from xonsh.environ import Env
from xonsh.tools import EnvPath
from xonsh.execer import Execer
from xonsh.aliases import Aliases
from lib.xonshrc_warnings import AbbrevsXontribNotInstalled


__all__ = ["XSH", "env", "env_path", "aliases", "execer"]


env = cast(Env, XSH.env)
env_path = cast(EnvPath, env["PATH"])

aliases = cast(Aliases, XSH.aliases)

execer = cast(Execer, XSH.execer)

