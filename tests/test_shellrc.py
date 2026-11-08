from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from helpers import output

from installer.block import BEGIN, END
from installer.context import Context
from installer.shellrc import bash_login_file, dotfiles_expr, setup_shells


@pytest.fixture
def no_zsh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)


@pytest.fixture
def with_zsh(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")


def block_of(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    return lines[lines.index(BEGIN) + 1 : lines.index(END)]


# --- 小さな関数 ---


@pytest.mark.parametrize(
    ("dotfiles", "expected"),
    [
        ("/h/.dotfiles", '"$HOME/.dotfiles"'),
        ("/h/src/my dotfiles", "'/h/src/my dotfiles'"),
        ("/opt/dotfiles", "/opt/dotfiles"),
    ],
)
def test_dotfiles_expr(dotfiles: str, expected: str) -> None:
    assert dotfiles_expr(Path(dotfiles), Path("/h")) == expected


def test_bash_login_file_follows_bash_order(home: Path) -> None:
    assert bash_login_file(home) == home / ".profile"
    (home / ".profile").touch()
    assert bash_login_file(home) == home / ".profile"
    (home / ".bash_login").touch()
    assert bash_login_file(home) == home / ".bash_login"
    (home / ".bash_profile").touch()
    assert bash_login_file(home) == home / ".bash_profile"


# --- setup_shells ---


@pytest.mark.usefixtures("no_zsh")
def test_setup_shells_on_an_empty_home_uses_profile_not_bash_profile(ctx: Context, home: Path) -> None:
    assert setup_shells(ctx)
    assert block_of(home / ".profile") == [
        f"export DOTFILES={dotfiles_expr(ctx.dotfiles, home)}",
        '. "$DOTFILES/shell/bash/profile.sh"',
    ]
    assert block_of(home / ".bashrc")[-1] == '. "$DOTFILES/shell/bash/rc.sh"'
    assert not (home / ".bash_profile").exists()
    assert not (home / ".zshrc").exists()


@pytest.mark.usefixtures("no_zsh")
def test_setup_shells_keeps_distro_defaults(ctx: Context, home: Path) -> None:
    (home / ".bash_profile").write_text("# fedora default\n. ~/.bashrc\n")
    (home / ".bashrc").write_text("# fedora default\n")
    assert setup_shells(ctx)
    assert (home / ".bash_profile").read_text().startswith("# fedora default\n. ~/.bashrc\n\n" + BEGIN)
    assert (home / ".bashrc").read_text().startswith("# fedora default\n\n" + BEGIN)
    assert not (home / ".profile").exists()


@pytest.mark.usefixtures("with_zsh")
def test_setup_shells_sets_up_zsh_when_installed(ctx: Context, home: Path) -> None:
    assert setup_shells(ctx)
    assert block_of(home / ".zprofile")[-1] == '. "$DOTFILES/shell/zsh/zprofile.zsh"'
    assert block_of(home / ".zshrc")[-1] == '. "$DOTFILES/shell/zsh/zshrc.zsh"'


@pytest.mark.usefixtures("no_zsh")
def test_setup_shells_sets_up_zsh_on_mac_even_if_not_found(ctx: Context, home: Path) -> None:
    ctx.os_name = "mac"
    assert setup_shells(ctx)
    assert (home / ".zprofile").exists()


@pytest.mark.usefixtures("with_zsh")
def test_setup_shells_is_idempotent(ctx: Context, home: Path) -> None:
    assert setup_shells(ctx)
    before = {p.name: p.read_text() for p in home.iterdir()}
    ctx.out.seek(0)
    ctx.out.truncate()
    assert setup_shells(ctx)
    assert {p.name: p.read_text() for p in home.iterdir()} == before
    assert all(line.startswith("ok: ") for line in output(ctx).splitlines())


@pytest.mark.usefixtures("no_zsh")
def test_dry_run_changes_nothing(ctx: Context, home: Path) -> None:
    (home / ".profile").write_text("# debian default\n")
    before = {p.name: p.read_text() for p in home.iterdir()}
    ctx.dry_run = True
    assert setup_shells(ctx)
    assert {p.name: p.read_text() for p in home.iterdir()} == before
    assert f"[dry-run] update block in {home / '.profile'}" in output(ctx)
    assert f"[dry-run] update block in {home / '.bashrc'}" in output(ctx)
