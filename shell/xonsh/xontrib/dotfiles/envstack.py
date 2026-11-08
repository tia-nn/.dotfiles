"""環境変数の退避と、.env ファイルの読み込み。対話シェルだけで読む。

- loadenv [FILE...]: .env 形式のファイル（既定は .env）を読み、環境変数にする
- pushe: 今の環境変数を退避する
- pope [-v]: 最後に退避した環境変数に戻す（-v で変えたものを表示する）
- push-and-loadenv [FILE...]: pushe してから loadenv する
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from xontrib.dotfiles._changes import Changes

if TYPE_CHECKING:
    from xonsh.built_ins import XonshSession

_changes = Changes()

# xonsh が alias の実行中に設定する変数。戻さない
_IGNORED = frozenset({"__ALIAS_NAME", "__ALIAS_STACK"})


def _load_xontrib_(xsh: XonshSession, **_: Any) -> None:
    env = xsh.env
    # unload / reload すると、退避した環境変数は捨てる
    stack: list[dict[str, str]] = []

    def loadenv(args: list[str]) -> int:
        texts = []
        for name in args or [".env"]:
            try:
                with open(name, encoding="utf-8") as f:
                    texts.append(f.read())
            except OSError as e:
                print(f"loadenv: ignore {name}: {e}", file=sys.stderr)
        script = "\n".join(["set -a", *texts, "set +a"])
        xsh.aliases["source-bash"](["--suppress-skip-message", script])
        return 0

    def pushe() -> None:
        stack.append(env.detype())

    def pope(args: list[str]) -> int:
        if not stack:
            print("pope: nothing was pushed", file=sys.stderr)
            return 1
        verbose = "-v" in args
        saved = stack.pop()
        current = env.detype()
        for name, value in saved.items():
            if name in _IGNORED or current.get(name) == value:
                continue
            if verbose:
                print(f"${name} = {value!r}  # was {current.get(name)!r}")
            env[name] = value
        for name in current.keys() - saved.keys() - _IGNORED:
            if verbose:
                print(f"del ${name}  # was {current[name]!r}")
            del env[name]
        return 0

    def push_and_loadenv(args: list[str]) -> int:
        pushe()
        return loadenv(args)

    _changes.set(xsh.aliases, "loadenv", loadenv)
    _changes.set(xsh.aliases, "pushe", pushe)
    _changes.set(xsh.aliases, "pope", pope)
    _changes.set(xsh.aliases, "push-and-loadenv", push_and_loadenv)


def _unload_xontrib_(xsh: XonshSession, **_: Any) -> None:
    _changes.restore()
