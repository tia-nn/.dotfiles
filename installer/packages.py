"""OS のパッケージをインストールする（install.sh packages）。

一覧はリポジトリ直下の packages.py に書く。入っていないものだけをまとめてインストールする。
Linux では sudo を使う（root で実行しているときは使わない）。
"""

from __future__ import annotations

import os
import shutil
import subprocess

from .context import Context
from .loader import get_str_list, load_module
from .osinfo import detect_distro

# パッケージマネージャ → packages.py の変数名
LIST_NAMES = {"apt": "APT", "dnf": "DNF", "brew": "BREW"}


def package_manager(ctx: Context) -> str | None:
    """apt / dnf / brew のどれを使うか。分からなければ None"""
    if ctx.os_name == "mac":
        return "brew"
    return {"debian": "apt", "fedora": "dnf"}.get(detect_distro())


def is_installed(manager: str, name: str) -> bool:
    """パッケージ name が入っているか"""
    if manager == "apt":
        args = ["dpkg-query", "-W", "-f=${db:Status-Abbrev}", name]
    elif manager == "dnf":
        args = ["rpm", "-q", "--whatprovides", name]
    else:
        args = ["brew", "list", "--versions", name]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if manager == "apt":
        return result.returncode == 0 and result.stdout.startswith("ii")
    return result.returncode == 0


def sudo() -> list[str]:
    return [] if os.geteuid() == 0 else ["sudo"]


def install_commands(manager: str, names: list[str]) -> list[list[str]]:
    """names をインストールするコマンドの一覧"""
    if manager == "apt":
        # tzdata などの設定画面で止まらないようにする（sudo は環境変数を引き継がないので env で渡す）
        noninteractive = ["env", "DEBIAN_FRONTEND=noninteractive"]
        return [
            [*sudo(), "apt-get", "update"],
            [*sudo(), *noninteractive, "apt-get", "install", "-y", *names],
        ]
    if manager == "dnf":
        return [[*sudo(), "dnf", "install", "-y", *names]]
    return [["brew", "install", *names]]


def install_packages(ctx: Context) -> bool:
    """packages.py の一覧のうち、入っていないものをインストールする。成功したら True"""
    manager = package_manager(ctx)
    if manager is None:
        ctx.warn("packages: unsupported distribution (supported: Debian/Ubuntu, Fedora, macOS)")
        return False
    if shutil.which(manager if manager != "apt" else "apt-get") is None:
        if manager == "brew":
            ctx.warn("packages: Homebrew is not installed. See https://brew.sh/")
        else:
            ctx.warn(f"packages: {manager} is not found")
        return False

    try:
        names = get_str_list(load_module(ctx.dotfiles / "packages.py"), LIST_NAMES[manager])
    except ValueError as e:
        ctx.warn(str(e))
        return False

    missing = [name for name in names if not is_installed(manager, name)]
    if not missing:
        ctx.info(f"ok: all {len(names)} {manager} packages are installed")
        return True
    return all(ctx.run(*args) for args in install_commands(manager, missing))
