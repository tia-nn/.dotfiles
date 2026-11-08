from __future__ import annotations

import os
import shutil

import pytest
from helpers import REPO_ROOT, errors, output

from installer import packages
from installer.context import Context
from installer.loader import get_str_dict, get_str_list, load_module
from installer.packages import install_commands, install_packages, package_manager


@pytest.fixture
def apt(monkeypatch: pytest.MonkeyPatch) -> None:
    """apt があり、git と curl だけが入っている環境"""
    monkeypatch.setattr(packages, "detect_distro", lambda: "debian")
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(packages, "is_installed", lambda manager, name: name in {"git", "curl"})
    monkeypatch.setattr(os, "geteuid", lambda: 1000)


def test_repository_packages_py_is_valid() -> None:
    module = load_module(REPO_ROOT / "packages.py")
    for name in ("APT", "DNF", "BREW", "ASDF_PLUGINS"):
        values = get_str_list(module, name)
        assert values
        assert len(values) == len(set(values)), f"duplicated in {name}"
    # 既定のバージョンを入れるツールは、プラグインも追加される
    assert set(get_str_dict(module, "ASDF_GLOBAL")) <= set(get_str_list(module, "ASDF_PLUGINS"))


@pytest.mark.parametrize(
    ("os_name", "distro", "expected"),
    [
        ("mac", "unknown", "brew"),
        ("linux", "debian", "apt"),
        ("linux", "fedora", "dnf"),
        ("linux", "unknown", None),
    ],
)
def test_package_manager(
    ctx: Context, monkeypatch: pytest.MonkeyPatch, os_name: str, distro: str, expected: str | None
) -> None:
    monkeypatch.setattr(packages, "detect_distro", lambda: distro)
    ctx.os_name = os_name
    assert package_manager(ctx) == expected


def test_install_commands_use_sudo_unless_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "geteuid", lambda: 1000)
    assert install_commands("dnf", ["a", "b"]) == [["sudo", "dnf", "install", "-y", "a", "b"]]
    assert install_commands("brew", ["a"]) == [["brew", "install", "a"]]
    monkeypatch.setattr(os, "geteuid", lambda: 0)
    assert install_commands("apt", ["a"]) == [
        ["apt-get", "update"],
        ["env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", "a"],
    ]


@pytest.mark.usefixtures("apt")
def test_install_packages_installs_only_missing_ones(ctx: Context) -> None:
    ctx.dry_run = True
    assert install_packages(ctx)
    lines = output(ctx).splitlines()
    assert "[dry-run] sudo apt-get update" in lines
    install_line = next(line for line in lines if "apt-get install" in line)
    assert install_line.startswith("[dry-run] sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y ")
    assert " unzip " in install_line + " "
    assert " git " not in install_line + " "
    assert " curl " not in install_line + " "


@pytest.mark.usefixtures("apt")
def test_install_packages_does_nothing_when_all_are_installed(
    ctx: Context, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(packages, "is_installed", lambda manager, name: True)
    assert install_packages(ctx)
    assert output(ctx).startswith("ok: all ")


def test_install_packages_on_an_unknown_distribution(ctx: Context, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(packages, "detect_distro", lambda: "unknown")
    assert not install_packages(ctx)
    assert "unsupported distribution" in errors(ctx)


def test_install_packages_without_homebrew(ctx: Context, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    ctx.os_name = "mac"
    assert not install_packages(ctx)
    assert "https://brew.sh/" in errors(ctx)
