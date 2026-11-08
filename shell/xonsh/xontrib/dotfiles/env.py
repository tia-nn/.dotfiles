"""PATH などの環境変数と、traceback のログ。xonsh -c やスクリプトの実行でも読む。

unload しても、env.sh で設定した環境変数は元に戻さない。
"""

from typing import TYPE_CHECKING, Any

import xonsh

from xontrib.dotfiles._changes import Changes
from xontrib.dotfiles._paths import dotfiles_dir, state_dir

if TYPE_CHECKING:
    from xonsh.built_ins import XonshSession

_changes = Changes()


def _load_xontrib_(xsh: XonshSession, **_: Any) -> None:
    env = xsh.env
    dotfiles = dotfiles_dir()
    _changes.set(env, "DOTFILES", str(dotfiles))

    # 共通層（PATH と環境変数）を読む。重複は env.sh の側で取り除く
    _changes.set(env, "FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE", True)
    xsh.aliases["source-bash"](["--suppress-skip-message", str(dotfiles / "shell" / "common" / "env.sh")])

    # 書き込めるファイルでないと、xonsh は黙って None にしてしまうので先に作る
    logfile = state_dir() / "traceback.log"
    logfile.parent.mkdir(parents=True, exist_ok=True)
    logfile.touch()
    _changes.set(env, "XONSH_TRACEBACK_LOGFILE", str(logfile))

    # screenfetch が使う（`xonsh -V` と同じ形。起動のたびに xonsh を実行しないよう、バージョンから作る）
    _changes.set(env, "shell_type", f"xonsh/{xonsh.__version__}")


def _unload_xontrib_(xsh: XonshSession, **_: Any) -> None:
    _changes.restore()
