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
from .shellrc import setup_shells

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


def cmd_packages(ctx: Context) -> bool:
    ctx.warn("packages: not implemented yet")
    return False


def cmd_tools(ctx: Context) -> bool:
    ctx.warn("tools: not implemented yet")
    return False


def cmd_all(ctx: Context) -> bool:
    return cmd_link(ctx) and cmd_packages(ctx) and cmd_tools(ctx)


COMMANDS: dict[str, tuple[Callable[[Context], bool], str]] = {
    "link": (cmd_link, "Create symlinks listed in links.py and set up shell rc files (default)"),
    "packages": (cmd_packages, "Install OS packages (not implemented yet)"),
    "tools": (cmd_tools, "Install tools such as xonsh and fonts (not implemented yet)"),
    "all": (cmd_all, "Run all of the above"),
}


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    commands_help = "\n".join(f"  {name:<10} {desc}" for name, (_, desc) in COMMANDS.items())
    parser = argparse.ArgumentParser(
        prog="install.sh",
        description="Install dotfiles. Safe to run repeatedly; never asks questions.",
        epilog=f"commands:\n{commands_help}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="show what would be done without changing anything"
    )
    parser.add_argument("command", nargs="?", default="link", choices=COMMANDS, metavar="COMMAND")
    return parser.parse_args(argv)


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
    return 0 if func(ctx) else 1
