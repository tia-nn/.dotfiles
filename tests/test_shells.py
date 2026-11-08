"""install.sh link のあと、実際にシェルを起動して設定が読み込まれることを確認する結合テスト。

ディストリビューション既定の rc（/etc/skel）を HOME に置いた状態から始める。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from helpers import REPO_ROOT

from installer.shellrc import bash_login_file

INSTALL = REPO_ROOT / "install.sh"
MARKER = "@@RESULT@@"

# 結果は MARKER の後ろに出す（対話シェルは他にも何か出力することがあるため）
REPORT = f'printf "{MARKER}%s|%s\\n" "${{DOTFILES-unset}}" "$PATH"'

FAKE_ASDF = """#!/bin/sh
case "$1 $2" in
    "completion bash") echo "complete -W 'install plugin' asdf" ;;
    "completion zsh") printf '%s\\n' '#compdef asdf' '_asdf() { compadd install plugin }' ;;
esac
"""


@pytest.fixture
def skel_home(home: Path) -> Path:
    skel = Path("/etc/skel")
    if skel.is_dir():
        shutil.copytree(skel, home, symlinks=True, dirs_exist_ok=True)
    (home / ".local" / "bin").mkdir(parents=True)
    (home / ".asdf" / "shims").mkdir(parents=True)
    # rc の asdf の補完の設定も通るように、補完スクリプトだけを出す偽の asdf を置く
    fake_asdf = home / ".local" / "bin" / "asdf"
    fake_asdf.write_text(FAKE_ASDF)
    fake_asdf.chmod(0o755)
    result = subprocess.run(["sh", str(INSTALL), "link"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return home


def report(argv: list[str], home: Path) -> tuple[str, list[str]]:
    """シェルを起動して (DOTFILES, PATH の一覧) を返す"""
    if shutil.which(argv[0]) is None:
        pytest.skip(f"{argv[0]} is not installed")
    result = subprocess.run(
        [*argv, REPORT],
        env={"HOME": str(home), "PATH": "/usr/bin:/bin", "TERM": "dumb", "LANG": os.environ.get("LANG", "C")},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.startswith(MARKER)]
    assert len(lines) == 1, result.stdout + result.stderr
    dotfiles, path = lines[0][len(MARKER) :].split("|")
    return dotfiles, path.split(":")


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["bash", "-l", "-c"], id="bash-login"),
        pytest.param(["bash", "-i", "-c"], id="bash-interactive"),
        pytest.param(["bash", "-l", "-i", "-c"], id="bash-login-interactive"),
        pytest.param(["sh", "-l", "-c"], id="sh-login"),
        pytest.param(["zsh", "-l", "-c"], id="zsh-login"),
        pytest.param(["zsh", "-i", "-c"], id="zsh-interactive"),
        pytest.param(["zsh", "-l", "-i", "-c"], id="zsh-login-interactive"),
    ],
)
def test_shell_loads_dotfiles(argv: list[str], skel_home: Path) -> None:
    if argv[0] == "zsh" and not (skel_home / ".zshrc").exists():
        pytest.skip("zsh was not set up (zsh is not installed)")
    if argv[0] == "sh" and bash_login_file(skel_home) != skel_home / ".profile":
        # Fedora などは ~/.bash_profile を使うので、~/.profile しか読まない sh には入らない（既定と同じ）
        pytest.skip("the bash login file is not ~/.profile")
    dotfiles, path = report(argv, skel_home)
    assert dotfiles == str(REPO_ROOT)
    assert path[:2] == [f"{skel_home}/.asdf/shims", f"{skel_home}/.local/bin"]
    assert len(path) == len(set(path)), path


def test_zsh_generates_asdf_completion_once(skel_home: Path) -> None:
    if not (skel_home / ".zshrc").exists():
        pytest.skip("zsh was not set up (zsh is not installed)")
    report(["zsh", "-i", "-c"], skel_home)
    completion = skel_home / ".asdf" / "completions" / "_asdf"
    assert completion.read_text().startswith("#compdef asdf")


def test_bashrc_is_read_once_in_a_login_interactive_bash(skel_home: Path) -> None:
    """既定の profile が ~/.bashrc を読む環境でも、profile.sh がもう一度読まない"""
    rc = skel_home / ".bashrc"
    rc.write_text(rc.read_text() + "\nCOUNT=$((${COUNT:-0} + 1))\n")
    result = subprocess.run(
        ["bash", "-l", "-i", "-c", f'printf "{MARKER}%s\\n" "$COUNT"'],
        env={"HOME": str(skel_home), "PATH": "/usr/bin:/bin", "TERM": "dumb"},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert f"{MARKER}1" in result.stdout.splitlines(), result.stdout + result.stderr
