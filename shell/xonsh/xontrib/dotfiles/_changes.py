"""xontrib が変えた値を覚えておき、unload のときに元に戻す。"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

_MISSING = object()


class Changes:
    """set() で変えた値を、restore() で変える前の値に戻す（変える前になかったものは消す）"""

    def __init__(self) -> None:
        self._undo: list[tuple[MutableMapping[str, Any], str, object]] = []

    def set(self, mapping: MutableMapping[str, Any], key: str, value: Any) -> None:
        # xonsh の Env の get() は、設定されていない変数にも既定値を返すので in で確かめる
        old = mapping[key] if key in mapping else _MISSING  # noqa: SIM401
        self._undo.append((mapping, key, old))
        mapping[key] = value

    def restore(self) -> None:
        while self._undo:
            mapping, key, old = self._undo.pop()
            if old is _MISSING:
                mapping.pop(key, None)
            else:
                mapping[key] = old
