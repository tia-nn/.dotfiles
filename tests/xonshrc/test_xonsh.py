"""shell/xonsh の設定のテスト。"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from helpers import REPO_ROOT

from installer.tools import xonsh as xonsh_tool
from xontrib.dotfiles import EXTERNAL, xontrib_names
from xontrib.dotfiles._changes import Changes
from xontrib.dotfiles._git import current_branch, default_branch, merged_branches
from xontrib.dotfiles._paths import dotfiles_dir, state_dir, xonsh_dir

XONSH_DIR = REPO_ROOT / "shell" / "xonsh"
INSTALL = REPO_ROOT / "install.sh"


# --- ファイルの形 ---


def test_rc_d_contains_only_the_entry() -> None:
    assert sorted(p.name for p in (XONSH_DIR / "rc.d").iterdir()) == ["50_dotfiles.py"]


def test_the_installer_installs_the_xontribs_loaded_by_the_rc() -> None:
    assert sorted(p for p in xonsh_tool.PACKAGES if p.startswith("xontrib-")) == sorted(
        f"xontrib-{name}" for name in EXTERNAL
    )


def test_every_xontrib_exists() -> None:
    for name in xontrib_names(interactive=True):
        assert (XONSH_DIR / "xontrib" / (name.replace(".", "/") + ".py")).is_file(), name


@pytest.mark.parametrize(
    "path",
    sorted(XONSH_DIR.rglob("*.py")),
    ids=lambda p: str(p.relative_to(XONSH_DIR)),
)
def test_every_file_is_valid_python(path: Path) -> None:
    """xonsh 独自の構文（$VAR や @(...)）を使っていない"""
    compile(path.read_text(encoding="utf-8"), str(path), "exec")


# --- xontrib/dotfiles/_paths.py ---


def test_paths_use_dotfiles_env(tmp_path: Path) -> None:
    env = {"DOTFILES": str(tmp_path)}
    assert dotfiles_dir(env) == tmp_path
    assert xonsh_dir(env) == tmp_path / "shell" / "xonsh"


def test_paths_fall_back_to_the_repository() -> None:
    assert dotfiles_dir({}) == REPO_ROOT


def test_state_dir(home: Path, tmp_path: Path) -> None:
    assert state_dir({"HOME": str(tmp_path)}) == tmp_path / ".local" / "state" / "xonsh"
    assert state_dir({}) == home / ".local" / "state" / "xonsh"
    assert state_dir({"XDG_STATE_HOME": str(tmp_path / "state")}) == tmp_path / "state" / "xonsh"


# --- xontrib/dotfiles/_git.py ---


@pytest.fixture
def env(home: Path) -> dict[str, str]:
    """git に渡す環境変数（xonsh の env の代わり）。ほかの git の設定を読まない"""
    if shutil.which("git") is None:
        pytest.skip("git is not installed")
    return {
        "HOME": str(home),
        "PATH": os.environ["PATH"],
        "GIT_CONFIG_GLOBAL": str(home / ".gitconfig"),
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def run_git(repo: Path, *args: str) -> None:
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run(["git", *identity, *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def git_repo(tmp_path: Path, env: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> Path:
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "topic", str(repo)], check=True)
    run_git(repo, "commit", "-q", "--allow-empty", "-m", "x")
    monkeypatch.chdir(repo)
    return repo


@pytest.mark.usefixtures("git_repo")
def test_default_branch(env: dict[str, str], home: Path) -> None:
    assert default_branch(env) is None
    (home / ".gitconfig").write_text("[init]\n\tdefaultBranch = trunk\n")
    assert default_branch(env) == "trunk"
    assert default_branch({**env, "GIT_DEFAULTBRANCH": "main"}) == "main"


@pytest.mark.usefixtures("git_repo")
def test_current_branch(env: dict[str, str]) -> None:
    assert current_branch(env) == "topic"


def test_current_branch_outside_a_repository(
    env: dict[str, str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert current_branch({**env, "GIT_CEILING_DIRECTORIES": str(tmp_path)}) is None


def test_git_helpers_use_the_path_in_env(tmp_path: Path) -> None:
    """os.environ ではなく、渡した env の PATH で git を探す"""
    env = {"PATH": str(tmp_path)}
    assert current_branch(env) is None
    assert default_branch(env) is None


def test_merged_branches_skip_protected_and_checked_out_branches(
    git_repo: Path, env: dict[str, str], tmp_path: Path
) -> None:
    for branch in ("main", "release/1.0", "maintenance", "feature/domain", "in-worktree"):
        run_git(git_repo, "branch", branch)
    run_git(git_repo, "switch", "-q", "-c", "unmerged")
    run_git(git_repo, "commit", "-q", "--allow-empty", "-m", "y")
    run_git(git_repo, "switch", "-q", "topic")
    run_git(git_repo, "worktree", "add", "-q", str(tmp_path / "wt"), "in-worktree")
    # 今のブランチ（topic）・守るブランチ・ほかの worktree のブランチ・マージしていないブランチは消さない。
    # 名前の一部に main などを含むだけのブランチは消す
    assert merged_branches(env) == ["feature/domain", "maintenance"]


def test_merged_branches_outside_a_repository(
    env: dict[str, str], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert merged_branches({**env, "GIT_CEILING_DIRECTORIES": str(tmp_path)}) is None


# --- xontrib/dotfiles/_changes.py ---


def test_changes_restores_old_values_and_removes_new_keys() -> None:
    mapping = {"a": 1}
    changes = Changes()
    changes.set(mapping, "a", 2)
    changes.set(mapping, "b", 3)
    changes.set(mapping, "a", 4)
    assert mapping == {"a": 4, "b": 3}
    changes.restore()
    assert mapping == {"a": 1}
    changes.restore()
    assert mapping == {"a": 1}


# --- 実際の xonsh で読み込む ---


@pytest.fixture
def xonsh() -> str:
    path = shutil.which("xonsh", path=os.path.dirname(sys.executable)) or shutil.which("xonsh")
    if path is None:
        pytest.skip("xonsh is not installed")
    return path


def test_rc_d_is_loaded_by_xonsh_after_install(xonsh: str, home: Path) -> None:
    """install.sh link で ~/.config/xonsh/rc.d に入口をリンクし、xonsh が自分で読み込むことを確認する。

    非対話（xonsh -c）なので、対話シェル専用の xontrib（prompt・abbrevs・envstack や vox）は読まれない。
    $DOTFILES は渡さず、入口のリンクから場所を決められることも確認する。
    """
    (home / ".local" / "bin").mkdir(parents=True)
    result = subprocess.run(["sh", str(INSTALL), "link"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr

    script = """
print('@@', $DOTFILES, $XONSH_TRACEBACK_LOGFILE, $shell_type, sep='|')
print('@@', 'git-prune-localbranch' in aliases, 'dotfiles-reload' in aliases, sep='|')
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

    # 対話シェル専用の xontrib（envstack の loadenv など）は読まれていない
    assert lines[3] == ["False", "False"]


def test_interactive_xontribs_can_be_reloaded_and_unloaded(xonsh: str, home: Path) -> None:
    """対話シェル（xonsh -i）では対話用の xontrib も読み、dotfiles-reload と unload ができる。

    PC ごとの設定（rc.d/90_local.xsh）は dotfiles の後に読まれ、xonsh で設定した変数を abbrevs が使う。
    """
    (home / ".local" / "bin").mkdir(parents=True)
    result = subprocess.run(["sh", str(INSTALL), "link"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    (home / ".config/xonsh/rc.d/90_local.xsh").write_text("$GIT_DEFAULTBRANCH = 'trunk'\n")

    script = """
from types import SimpleNamespace
from xonsh.xontribs import xontribs_unload
print('@@', abbrevs['grstrm']('grstrm', SimpleNamespace(text='grstrm')), 'vox' in aliases, sep='|')
def state():
    return $RIGHT_PROMPT, 'loadenv' in aliases, 'dotfiles-reload' in aliases
print('@@', *state(), sep='|')
dotfiles-reload
print('@@', *state(), sep='|')
xontribs_unload(['dotfiles.prompt', 'dotfiles.envstack', 'dotfiles.aliases'])
print('@@', *state(), sep='|')
"""
    result = subprocess.run(
        [xonsh, "-i", "--shell-type=readline", "-c", script],
        env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    lines = [line.split("|")[1:] for line in result.stdout.splitlines() if line.startswith("@@|")]
    loaded = ["{curr_branch} {env_name}", "True", "True"]
    assert lines == [
        ["git restore --source=trunk", "True"],
        loaded,
        loaded,
        ["", "False", "False"],
    ], result.stdout + result.stderr
    # 外部の xontrib も入っているので、案内も警告も出ない
    assert result.stderr == ""
