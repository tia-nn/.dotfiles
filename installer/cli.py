"""コマンドラインの入口。install.sh → install.py → main() の順に呼ばれる。"""

from __future__ import annotations

import argparse
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

from .context import Context
from .links import link_all, load_entries
from .osinfo import detect_os
from .packages import install_packages
from .shellrc import setup_shells
from .tools import TOOLS, install_tools

DOTFILES = Path(__file__).resolve().parent.parent


def cmd_link(ctx: Context) -> bool:
    ctx.info(f"==> link ({ctx.os_name})")
    try:
        entries = load_entries(ctx.dotfiles / "links.py")
    except ValueError as e:
        ctx.warn(str(e))
        return False
    links_ok = link_all(entries, ctx)

    ctx.info("==> shell rc")
    shells_ok = setup_shells(ctx)
    return links_ok and shells_ok


def cmd_packages(ctx: Context, names: list[str]) -> bool:
    ctx.info("==> packages")
    return install_packages(ctx)


def cmd_tools(ctx: Context, names: list[str]) -> bool:
    return install_tools(names, ctx)


def cmd_all(ctx: Context, names: list[str]) -> bool:
    # link はほかと独立しているので、失敗しても続ける
    link_ok = cmd_link(ctx)
    # パッケージ（git や python3-venv）が入ってからツールを入れる
    install_ok = cmd_packages(ctx, []) and cmd_tools(ctx, [])
    return link_ok and install_ok


COMMANDS: dict[str, tuple[Callable[[Context, list[str]], bool], str]] = {
    "link": (lambda ctx, names: cmd_link(ctx), "Create symlinks in links.py and set up shell rc (default)"),
    "packages": (cmd_packages, "Install OS packages in packages.py (uses sudo on Linux)"),
    "tools": (cmd_tools, "Install tools (all default tools, or only the given NAMEs)"),
    "all": (cmd_all, "Run link, packages and tools"),
}


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    commands_help = "\n".join(f"  {name:<10} {desc}" for name, (_, desc) in COMMANDS.items())
    tools_help = "\n".join(
        f"  {t.name:<10} {t.description}" for t in TOOLS.values()
    )
    parser = argparse.ArgumentParser(
        prog="install.sh",
        description="Install dotfiles. Safe to run repeatedly; never asks questions.",
        epilog=f"commands:\n{commands_help}\n\ntools:\n{tools_help}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="show what would be done without changing anything"
    )
    parser.add_argument("command", nargs="?", default="link", choices=COMMANDS, metavar="COMMAND")
    parser.add_argument("names", nargs="*", metavar="NAME", help="tool names (only for the tools command)")
    args = parser.parse_args(argv)
    if args.names and args.command != "tools":
        parser.error(f"{args.command} does not take NAME arguments")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    os_name = detect_os()
    if os_name not in ("linux", "mac"):
        print(f"error: unsupported OS: {platform.system()}", file=sys.stderr)
        return 1

    home = Path.home()
    state_home = Path(os.environ.get("XDG_STATE_HOME") or home / ".local" / "state")
    ctx = Context(
        dotfiles=DOTFILES,
        home=home,
        os_name=os_name,
        backup_dir=state_home / "dotfiles" / "backup" / datetime.now().strftime("%Y%m%d-%H%M%S"),
        dry_run=args.dry_run,
    )
    # これから呼ぶスクリプトからもリポジトリの場所を参照できるようにする
    os.environ["DOTFILES"] = str(ctx.dotfiles)

    if ctx.dry_run:
        ctx.info("(dry-run: nothing will be changed)")
    func, _ = COMMANDS[args.command]
    return 0 if func(ctx, args.names) else 1
