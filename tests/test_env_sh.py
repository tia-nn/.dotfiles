"""shell/common/env.sh を sh / bash / zsh で読み込むテスト。"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from helpers import REPO_ROOT

ENV_SH = REPO_ROOT / "shell" / "common" / "env.sh"
BASE_PATH = "/usr/local/bin:/usr/bin:/bin"

SHELLS = {
    "sh": ["sh", "-u", "-c", '. "$ENV_SH"; {cmd}'],
    "bash": ["bash", "--posix", "-u", "-c", '. "$ENV_SH"; {cmd}'],
    "zsh": ["zsh", "-u", "-c", "emulate sh -c '. \"$ENV_SH\"'; {cmd}"],
}


def run_in(shell: str, home: Path, cmd: str, path: str = BASE_PATH) -> subprocess.CompletedProcess[str]:
    if shutil.which(shell) is None:
        pytest.skip(f"{shell} is not installed")
    argv = [arg.replace("{cmd}", cmd) for arg in SHELLS[shell]]
    return subprocess.run(
        argv,
        env={"HOME": str(home), "PATH": path, "ENV_SH": str(ENV_SH)},
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture(params=list(SHELLS))
def shell(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture
def tools_home(home: Path) -> Path:
    for d in [".local/bin", ".asdf/shims", ".local/share/npm/bin"]:
        (home / d).mkdir(parents=True)
    return home


def test_nothing_is_added_without_tool_directories(shell: str, home: Path) -> None:
    result = run_in(shell, home, 'printf "%s" "$PATH"')
    assert result.stdout == BASE_PATH
    assert result.stderr == ""


def test_tool_directories_are_prepended_in_order(shell: str, tools_home: Path) -> None:
    result = run_in(shell, tools_home, 'printf "%s" "$PATH"')
    h = tools_home
    assert result.stdout.split(":") == [
        f"{h}/.local/share/npm/bin",
        f"{h}/.asdf/shims",
        f"{h}/.local/bin",
        *BASE_PATH.split(":"),
    ]
    assert result.stderr == ""


def test_asdf_shims_follow_asdf_data_dir(shell: str, home: Path, tmp_path: Path) -> None:
    (tmp_path / "asdf" / "shims").mkdir(parents=True)
    result = run_in(shell, home, f'ASDF_DATA_DIR={tmp_path}/asdf; . "$ENV_SH"; printf "%s" "$PATH"')
    assert result.stdout.split(":")[0] == f"{tmp_path}/asdf/shims"


def test_npm_bin_follows_xdg_data_home(shell: str, home: Path, tmp_path: Path) -> None:
    (tmp_path / "data" / "npm" / "bin").mkdir(parents=True)
    result = run_in(shell, home, f'XDG_DATA_HOME={tmp_path}/data; . "$ENV_SH"; printf "%s" "$PATH"')
    assert result.stdout.split(":")[0] == f"{tmp_path}/data/npm/bin"


def test_npm_cache_alone_does_not_add_npm_bin(shell: str, home: Path) -> None:
    """~/.npm は npm のキャッシュなので、あっても PATH には何も足さない"""
    (home / ".npm" / "_cacache").mkdir(parents=True)
    (home / ".npm" / "bin").mkdir()
    result = run_in(shell, home, 'printf "%s" "$PATH"')
    assert result.stdout == BASE_PATH


def test_sourcing_twice_gives_the_same_path(shell: str, tools_home: Path) -> None:
    once = run_in(shell, tools_home, 'printf "%s" "$PATH"').stdout
    twice = run_in(shell, tools_home, '. "$ENV_SH"; printf "%s" "$PATH"').stdout
    assert twice == once


def test_inherited_entries_are_moved_to_the_front(shell: str, tools_home: Path) -> None:
    """mac の path_helper のように、引き継いだ PATH の後ろに回された場合も先頭に戻す"""
    inherited = f"{BASE_PATH}:{tools_home}/.local/bin:{tools_home}/.local/share/npm/bin"
    path = run_in(shell, tools_home, 'printf "%s" "$PATH"', path=inherited).stdout.split(":")
    assert path[:3] == [
        f"{tools_home}/.local/share/npm/bin",
        f"{tools_home}/.asdf/shims",
        f"{tools_home}/.local/bin",
    ]
    assert len(path) == len(set(path))


def test_no_helper_variables_or_functions_are_left(shell: str, tools_home: Path) -> None:
    result = run_in(
        shell,
        tools_home,
        'set | grep "^_dotfiles" || true; command -v _dotfiles_path_prepend || true',
    )
    assert result.stdout == ""


def test_license_files_are_joined_with_colons(shell: str, home: Path) -> None:
    fpga = home / ".local/apps/intelFPGA_lite"
    (fpga / "22.1std/questa_fse/bin").mkdir(parents=True)
    (fpga / "a.dat").touch()
    (fpga / "b.dat").touch()
    result = run_in(shell, home, 'printf "%s" "$LM_LICENSE_FILE"')
    assert result.stdout == f"{fpga}/a.dat:{fpga}/b.dat"


def test_no_license_variable_without_license_files(shell: str, home: Path) -> None:
    (home / ".local/apps/intelFPGA_lite/22.1std/questa_fse/bin").mkdir(parents=True)
    result = run_in(shell, home, 'printf "%s" "${LM_LICENSE_FILE-unset}"')
    assert result.stdout == "unset"


# --- Neko のライブラリ（haxelib のための暫定の対応）---


def neko_home(home: Path, tool_versions: str, version: str = "2.4.1") -> Path:
    (home / ".asdf/installs/neko" / version / "bin").mkdir(parents=True)
    (home / ".tool-versions").write_text(tool_versions)
    return home / ".asdf/installs/neko" / version / "bin"


def test_neko_library_path_is_added_from_tool_versions(shell: str, home: Path) -> None:
    neko = neko_home(home, "nodejs 24.22.2\nneko 2.4.1\nhaxe 4.3.7\n")
    result = run_in(shell, home, 'printf "%s" "${LD_LIBRARY_PATH-unset}"')
    assert result.stdout == str(neko)
    assert result.stderr == ""


def test_neko_library_path_is_not_duplicated(shell: str, home: Path) -> None:
    neko = neko_home(home, "neko 2.4.1")  # 最終行に改行がなくても読む
    result = run_in(shell, home, '. "$ENV_SH"; printf "%s" "${LD_LIBRARY_PATH-unset}"')
    assert result.stdout == str(neko)


@pytest.mark.parametrize(
    "tool_versions",
    ["nodejs 24.22.2\n", "neko 9.9.9\n"],
    ids=["no-neko", "not-installed"],
)
def test_no_library_path_without_installed_neko(shell: str, home: Path, tool_versions: str) -> None:
    neko_home(home, tool_versions)
    result = run_in(shell, home, 'printf "%s" "${LD_LIBRARY_PATH-unset}"')
    assert result.stdout == "unset"
