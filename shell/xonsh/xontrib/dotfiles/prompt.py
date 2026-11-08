"""プロンプト・履歴・補完・入力の設定。対話シェルだけで読む。

変数の意味と既定値は https://xon.sh/envvars.html を参照。
"""

from typing import TYPE_CHECKING, Any

from xontrib.dotfiles._changes import Changes
from xontrib.dotfiles._paths import xonsh_dir

if TYPE_CHECKING:
    from xonsh.built_ins import XonshSession

_changes = Changes()

_ENV: dict[str, Any] = {
    # プロンプト
    "PROMPT": (
        "{INTENSE_BLUE}{user}{INTENSE_GREEN}@{INTENSE_BLUE}{hostname}{WHITE}:{cwd}\n {RED}{prompt_end}  "
    ),
    "RIGHT_PROMPT": "{curr_branch} {env_name}",
    "MULTILINE_PROMPT": ">",
    "SUPPRESS_BRANCH_TIMEOUT_MESSAGE": True,
    "VC_HG_SHOW_BRANCH": False,
    # 入力
    "IGNOREEOF": True,
    "INDENT": "    ",
    "SUGGEST_COMMANDS": False,
    "XONSH_AUTOPAIR": True,
    "XONSH_CTRL_BKSP_DELETION": True,
    # 履歴
    "HISTCONTROL": "ignoredups",
    "XONSH_HISTORY_BACKEND": "sqlite",
    "XONSH_HISTORY_MATCH_ANYWHERE": True,
    # 補完
    "COMPLETIONS_CONFIRM": False,
}

_PROMPT_FIELDS = {
    # {env_name} の前後（vox で有効にした venv の名前など）
    "env_prefix": "[",
    "env_postfix": "]",
}


def _load_xontrib_(xsh: XonshSession, **_: Any) -> None:
    env = xsh.env
    for name, value in _ENV.items():
        _changes.set(env, name, value)
    _changes.set(env, "BASH_COMPLETIONS", str(xonsh_dir(env.detype()) / "bash_completions.bash"))
    for name, value in _PROMPT_FIELDS.items():
        _changes.set(env["PROMPT_FIELDS"], name, value)


def _unload_xontrib_(xsh: XonshSession, **_: Any) -> None:
    _changes.restore()
