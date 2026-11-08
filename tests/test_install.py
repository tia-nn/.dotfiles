"""install.sh を /bin/sh（Debian では dash）から実行する結合テスト。"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from helpers import REPO_ROOT, snapshot

from installer.links import load_entries, resolve
from installer.osinfo import detect_os

INSTALL = REPO_ROOT / "install.sh"


def install(
    *args: str, script: str = str(INSTALL), cwd: Path | None = None, **env: str
) -> subprocess.CompletedProcess[str]:
    """sh install.sh ARGS... を実行する。env は環境変数に追加する"""
    return subprocess.run(
        ["sh", script, *args],
        cwd=cwd,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_link_creates_every_link_for_this_os(home: Path) -> None:
    result = install("link")
    assert result.returncode == 0, result.stderr
    links = resolve(load_entries(REPO_ROOT / "links.py"), os_name=detect_os(), dotfiles=REPO_ROOT, home=home)
    assert links
    for link in links:
        assert os.readlink(link.dest) == str(link.src)


def test_link_is_the_default_command(home: Path) -> None:
    assert install().returncode == 0
    assert (home / ".xonshrc").is_symlink()


def test_running_link_twice_changes_nothing_the_second_time(home: Path) -> None:
    assert install("link").returncode == 0
    before = snapshot(home)
    result = install("link")
    assert result.returncode == 0
    assert "\n+ " not in "\n" + result.stdout
    assert snapshot(home) == before


def test_dry_run_changes_nothing(home: Path) -> None:
    (home / ".xonshrc").write_text("old\n")
    before = snapshot(home)
    result = install("--dry-run", "link")
    assert result.returncode == 0
    assert "[dry-run]" in result.stdout
    assert snapshot(home) == before


def test_an_existing_file_is_backed_up_under_xdg_state_home(home: Path) -> None:
    (home / ".xonshrc").write_text("old\n")
    assert install("link").returncode == 0
    assert os.readlink(home / ".xonshrc") == str(REPO_ROOT / ".xonshrc")
    backups = list((home / ".local/state/dotfiles/backup").glob("*/.xonshrc"))
    assert len(backups) == 1
    assert backups[0].read_text() == "old\n"


def test_works_when_the_repository_is_not_at_home_dotfiles(home: Path) -> None:
    assert not (home / ".dotfiles").exists()
    assert install("link").returncode == 0
    assert os.readlink(home / ".xonshrc") == str(REPO_ROOT / ".xonshrc")


def test_works_with_cdpath_and_a_relative_path(home: Path) -> None:
    parent = REPO_ROOT.parent
    result = install("link", script=f"{REPO_ROOT.name}/install.sh", cwd=parent, CDPATH=str(parent))
    assert result.returncode == 0, result.stderr
    assert os.readlink(home / ".xonshrc") == str(REPO_ROOT / ".xonshrc")


def test_unknown_command_and_option_fail(home: Path) -> None:
    assert install("bogus").returncode != 0
    assert install("--bogus").returncode != 0
    assert snapshot(home) == []


def test_help_prints_usage(home: Path) -> None:
    result = install("--help")
    assert result.returncode == 0
    assert result.stdout.startswith("usage: install.sh")
    assert "packages" in result.stdout


def test_missing_python_is_reported(home: Path, tmp_path: Path) -> None:
    result = install("link", DOTFILES_PYTHON=str(tmp_path / "no-python"))
    assert result.returncode == 1
    assert "python3 (3.9 or later) is required" in result.stderr
    assert snapshot(home) == []


def test_repository_is_not_written(home: Path) -> None:
    """__pycache__ などをリポジトリに作らない（compose では読み取り専用でマウントしている）"""
    before = sorted(p.name for p in (REPO_ROOT / "installer").iterdir())
    assert install("link").returncode == 0
    assert sorted(p.name for p in (REPO_ROOT / "installer").iterdir()) == before
