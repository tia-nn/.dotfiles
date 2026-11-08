"""パッケージマネージャ以外で入れるもの（install.sh tools [NAME...]）。

それぞれのツールは install(ctx) -> bool を持つ。すでに入っていれば何もしない。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..context import Context
from . import asdf, fonts, git, npm, xonsh


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    install: Callable[[Context], bool]
    default: bool = True
    """名前を指定しないときにも入れるか"""


TOOLS = {
    tool.name: tool
    for tool in [
        Tool("git", "Set git global config (user, default branch, ...)", git.install),
        Tool("asdf", "Install asdf, its plugins and global versions in packages.py", asdf.install),
        Tool("xonsh", "Install xonsh into a venv and link ~/.local/bin/xonsh", xonsh.install),
        Tool("npm", "Set npm prefix to ~/.npm (npm is installed by asdf)", npm.install),
        Tool("fonts", "Install Source Han Code JP and Nerd Fonts Symbols", fonts.install),
    ]
}


def install_tools(names: list[str], ctx: Context) -> bool:
    """names のツールを順に入れる（空なら default のものすべて）。すべて成功したら True"""
    unknown = [name for name in names if name not in TOOLS]
    if unknown:
        ctx.warn(f"unknown tools: {', '.join(unknown)} (available: {', '.join(TOOLS)})")
        return False

    selected = [TOOLS[name] for name in names] if names else [t for t in TOOLS.values() if t.default]
    ok = True
    for tool in selected:
        ctx.info(f"==> tools: {tool.name}")
        try:
            ok = tool.install(ctx) and ok
        except OSError as e:
            ctx.warn(f"{tool.name}: {e}")
            ok = False
    return ok
