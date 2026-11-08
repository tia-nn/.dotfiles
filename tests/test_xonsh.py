"""shell/xonsh の設定のテスト。"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from helpers import REPO_ROOT

from xontrib.dotfiles._git import current_branch, default_branch
from xontrib.dotfiles._paths import dotfiles_dir, rc_files, state_dir, xonsh_dir

XONSH_DIR = REPO_ROOT / "shell" / "xonsh"
INSTALL = REPO_ROOT / "install.sh"


# --- ファイルの形 ---


def test_rc_d_contains_only_python_files() -> None:
    files = sorted(p.name for p in (XONSH_DIR / "rc.d").iterdir())
    assert files
    assert all(name.endswith(".py") for name in files), files


@pytest.mark.parametrize(
    "path",
    sorted(XONSH_DIR.rglob("*.py")),
    ids=lambda p: str(p.relative_to(XONSH_DIR)),
)
def test_every_file_is_valid_python(path: Path) -> None:
    """xonsh 独自の構文（$VAR や @(...)）を使っていない"""
    compile(path.read_text(encoding="utf-8"), str(path), "exec")


# --- lib/paths.py ---


def test_paths_use_dotfiles_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DOTFILES", str(tmp_path))
    assert dotfiles_dir() == tmp_path
    assert xonsh_dir() == tmp_path / "shell" / "xonsh"


def test_paths_fall_back_to_the_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DOTFILES", raising=False)
    assert dotfiles_dir() == REPO_ROOT


def test_rc_files_are_sorted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOTFILES", str(REPO_ROOT))
    names = [p.name for p in rc_files()]
    assert names == sorted(names)
    assert "50_dotfiles.py" in names


def test_state_dir(monkeypatch: pytest.MonkeyPatch, home: Path, tmp_path: Path) -> None:
    assert state_dir() == home / ".local" / "state" / "xonsh"
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    assert state_dir() == tmp_path / "state" / "xonsh"


# --- lib/git.py ---


@pytest.fixture
def git_repo(tmp_path: Path, home: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(home / ".gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.delenv("GIT_DEFAULTBRANCH", raising=False)
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "topic", str(repo)], check=True)
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run(["git", *identity, "commit", "-q", "--allow-empty", "-m", "x"], cwd=repo, check=True)
    monkeypatch.chdir(repo)
    return repo


@pytest.mark.usefixtures("git_repo")
def test_default_branch(monkeypatch: pytest.MonkeyPatch, home: Path) -> None:
    assert default_branch() is None
    (home / ".gitconfig").write_text("[init]\n\tdefaultBranch = trunk\n")
    assert default_branch() == "trunk"
    monkeypatch.setenv("GIT_DEFAULTBRANCH", "main")
    assert default_branch() == "main"


@pytest.mark.usefixtures("git_repo")
def test_current_branch() -> None:
    assert current_branch() == "topic"


def test_current_branch_outside_a_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    assert current_branch() is None


def test_git_helpers_without_git(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.delenv("GIT_DEFAULTBRANCH", raising=False)
    assert current_branch() is None
    assert default_branch() is None


# --- 実際の xonsh で読み込む ---


@pytest.fixture
def xonsh() -> str:
    path = shutil.which("xonsh", path=os.path.dirname(sys.executable)) or shutil.which("xonsh")
    if path is None:
        pytest.skip("xonsh is not installed")
    return path


def test_rc_d_is_loaded_by_xonsh_after_install(xonsh: str, home: Path) -> None:
    """install.sh link で ~/.config/xonsh/rc.d に入口をリンクし、xonsh が自分で読み込むことを確認する。

    非対話（xonsh -c）なので、対話シェル専用の rc（xontrib のインストールや vox）は読まれない。
    $DOTFILES は渡さず、入口のリンクから場所を決められることも確認する。
    """
    (home / ".local" / "bin").mkdir(parents=True)
    result = subprocess.run(["sh", str(INSTALL), "link"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr

    script = """
print('@@', $DOTFILES, $XONSH_TRACEBACK_LOGFILE, $shell_type, sep='|')
print('@@', 'git-prune-localbranch' in aliases, 'measure-xonshrc-time-performance' in aliases, sep='|')
print('@@', ':'.join($PATH), sep='|')
print('@@', $XONSH_INTERACTIVE, 'loadenv' in aliases, sep='|')
"""
    result = subprocess.run(
        [xonsh, "-c", script],
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == ""
    lines = [line.split("|")[1:] for line in result.stdout.splitlines() if line.startswith("@@|")]
    assert len(lines) == 4, result.stdout + result.stderr

    dotfiles, logfile, shell_type = lines[0]
    assert dotfiles == str(REPO_ROOT)
    assert logfile == str(home / ".local" / "state" / "xonsh" / "traceback.log")
    assert Path(logfile).is_file()
    assert shell_type.startswith("xonsh/")

    assert lines[1] == ["True", "True"]
    path = lines[2][0].split(":")
    local_bin = str(home / ".local" / "bin")
    assert path.count(local_bin) == 1
    assert path.index(local_bin) < path.index("/usr/bin")

    # 対話シェル専用の rc（30_tools の loadenv など）は読まれていない
    assert lines[3] == ["False", "False"]
    assert not (home / ".local" / "share" / "xonsh" / "vox").exists()
