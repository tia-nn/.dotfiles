"""shell/xonsh/xontrib/dotfiles の各 xontrib のテスト。

xonsh の代わりに、env・aliases・abbrevs を dict で持つ FakeSession を渡して _load_xontrib_ を呼ぶ。
"""

import importlib
import stat
from collections.abc import Callable
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, cast

import pytest

from xontrib.dotfiles import xontrib_names
from xontrib.dotfiles.abbrevs import Abbrev, after, head_only


class FakeEnv(dict[str, Any]):
    """xonsh の Env の代わり"""

    def detype(self) -> dict[str, str]:
        return {k: v for k, v in self.items() if isinstance(v, str)}


class FakeSession:
    """xonsh の XonshSession の代わり。source-bash は渡された引数を覚えておくだけ"""

    def __init__(self, *, abbrevs: bool = True) -> None:
        self.sourced: list[list[str]] = []
        self.env = FakeEnv(PATH=[], PROMPT_FIELDS={"user": "u"}, KEEP="x")
        self.aliases: dict[str, Any] = {"source-bash": self.sourced.append}
        self.builtins = SimpleNamespace(**({"abbrevs": {}} if abbrevs else {}))

    def state(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None]:
        """変更があったかを比べるための写し"""
        abbrevs = getattr(self.builtins, "abbrevs", None)
        return (
            {k: v for k, v in self.env.items() if k != "PROMPT_FIELDS"},
            dict(self.env["PROMPT_FIELDS"]),
            dict(self.aliases),
            None if abbrevs is None else dict(abbrevs),
        )


def load(name: str) -> ModuleType:
    """dotfiles.NAME のモジュール。xonsh が必要なもの（env）は、xonsh がなければ飛ばす"""
    if name == "dotfiles.env":
        pytest.importorskip("xonsh")
    return importlib.import_module(f"xontrib.{name}")


@pytest.fixture
def xsh(home: Path) -> FakeSession:
    return FakeSession()


# --- すべての xontrib ---


@pytest.mark.parametrize("name", xontrib_names(interactive=True))
def test_unload_restores_everything_load_changed(name: str, xsh: FakeSession) -> None:
    module = load(name)
    before = xsh.state()
    module._load_xontrib_(xsh)
    assert xsh.state() != before
    module._unload_xontrib_(xsh)
    assert xsh.state() == before


@pytest.mark.parametrize("name", xontrib_names(interactive=True))
def test_loading_twice_then_unloading_restores_everything(name: str, xsh: FakeSession) -> None:
    """xontrib load を2回してから unload しても元に戻る"""
    module = load(name)
    before = xsh.state()
    module._load_xontrib_(xsh)
    module._load_xontrib_(xsh)
    module._unload_xontrib_(xsh)
    assert xsh.state() == before


@pytest.mark.parametrize("name", ["dotfiles.env", "dotfiles.prompt"])
def test_only_current_xonsh_variables_are_set(name: str, xsh: FakeSession) -> None:
    """xonsh で廃止・非推奨になった変数を設定していない（設定しても何も起きず、警告も出ないことがある）"""
    from xonsh.environ import DEFAULT_VARS

    before = set(xsh.env)
    load(name)._load_xontrib_(xsh)
    ours = {"DOTFILES", "shell_type"}
    for var in sorted(set(xsh.env) - before - ours):
        assert var in DEFAULT_VARS, f"${var} is not a xonsh variable"
        assert not DEFAULT_VARS[var].deprecated, f"${var} is deprecated"


# --- env ---


def test_env_sets_dotfiles_and_sources_env_sh(xsh: FakeSession, home: Path) -> None:
    load("dotfiles.env")._load_xontrib_(xsh)
    dotfiles = Path(xsh.env["DOTFILES"])
    assert xsh.sourced == [["--suppress-skip-message", str(dotfiles / "shell/common/env.sh")]]
    logfile = home / ".local/state/xonsh/traceback.log"
    assert xsh.env["XONSH_TRACEBACK_LOGFILE"] == str(logfile)
    assert logfile.is_file()


# --- prompt ---


def test_prompt_adds_prompt_fields_and_keeps_the_others(xsh: FakeSession) -> None:
    load("dotfiles.prompt")._load_xontrib_(xsh)
    assert xsh.env["PROMPT_FIELDS"] == {"user": "u", "env_prefix": "[", "env_postfix": "]"}
    assert xsh.env["BASH_COMPLETIONS"].endswith("shell/xonsh/bash_completions.bash")


# --- abbrevs ---


def expand(abbrev: Abbrev, word: str, text: str) -> str:
    # prompt_toolkit の Buffer の代わり（abbrevs は text しか見ない）
    return abbrev(word, cast(Any, SimpleNamespace(text=text)))


def test_head_only_expands_only_at_the_start_of_the_line() -> None:
    abbrev = head_only("git status")
    assert expand(abbrev, "gs", "gs") == "git status"
    assert expand(abbrev, "gs", "echo gs") == "gs"


def test_head_only_calls_a_function_when_expanding() -> None:
    calls: list[int] = []

    def branch() -> str:
        calls.append(1)
        return "topic"

    abbrev = head_only(branch)
    assert calls == []
    assert expand(abbrev, "b", "b") == "topic"
    assert calls == [1]


def test_after_expands_only_after_the_command() -> None:
    abbrev = after("docker", "-it --rm")
    assert expand(abbrev, "-itr", "docker run -itr") == "-it --rm"
    assert expand(abbrev, "-itr", "ls -itr") == "-itr"


def test_abbrevs_does_nothing_without_xontrib_abbrevs(home: Path) -> None:
    xsh = FakeSession(abbrevs=False)
    before = xsh.state()
    load("dotfiles.abbrevs")._load_xontrib_(xsh)
    assert xsh.state() == before


def test_abbrevs_use_git_defaultbranch_set_in_xonsh(xsh: FakeSession) -> None:
    """xonsh は os.environ を更新しないので、xonsh で設定した $GIT_DEFAULTBRANCH を見る"""
    xsh.env["GIT_DEFAULTBRANCH"] = "trunk"
    load("dotfiles.abbrevs")._load_xontrib_(xsh)
    abbrevs: dict[str, Abbrev] = xsh.builtins.abbrevs
    assert expand(abbrevs["grstrm"], "grstrm", "grstrm") == "git restore --source=trunk"


def fake_command(directory: Path, name: str) -> None:
    directory.mkdir(exist_ok=True)
    path = directory / name
    path.write_text("#!/bin/sh\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


@pytest.mark.parametrize(
    ("commands", "docker_command", "expected"),
    [
        (["docker", "podman"], None, "docker"),
        (["podman"], None, "podman"),
        (["docker"], "nerdctl", "nerdctl"),
        ([], None, None),
    ],
)
def test_abbrevs_for_docker_use_the_command_found(
    xsh: FakeSession, tmp_path: Path, commands: list[str], docker_command: str | None, expected: str | None
) -> None:
    for command in commands:
        fake_command(tmp_path / "bin", command)
    xsh.env["PATH"] = [str(tmp_path / "bin")]
    if docker_command is not None:
        xsh.env["DOCKER_COMMAND"] = docker_command
    load("dotfiles.abbrevs")._load_xontrib_(xsh)
    abbrevs: dict[str, Abbrev] = xsh.builtins.abbrevs
    if expected is None:
        assert "dps" not in abbrevs
    else:
        assert expand(abbrevs["dps"], "dps", "dps") == f"{expected} ps"


# --- envstack ---


@pytest.fixture
def envstack(xsh: FakeSession) -> Callable[..., Any]:
    """envstack を読み込み、alias を名前で呼ぶ関数を返す"""
    load("dotfiles.envstack")._load_xontrib_(xsh)

    def call(name: str, *args: str) -> Any:
        alias = xsh.aliases[name]
        return alias() if name == "pushe" else alias(list(args))

    return call


def test_pope_restores_the_pushed_environment(
    xsh: FakeSession, envstack: Callable[..., Any], capsys: pytest.CaptureFixture[str]
) -> None:
    envstack("pushe")
    xsh.env["NEW"] = "1"
    xsh.env["KEEP"] = "changed"
    assert envstack("pope", "-v") == 0
    assert "NEW" not in xsh.env
    assert xsh.env["KEEP"] == "x"
    out = capsys.readouterr().out
    assert "$KEEP = 'x'  # was 'changed'" in out
    assert "del $NEW  # was '1'" in out


def test_pope_fails_when_nothing_was_pushed(
    envstack: Callable[..., Any], capsys: pytest.CaptureFixture[str]
) -> None:
    assert envstack("pope") == 1
    assert "nothing was pushed" in capsys.readouterr().err


def test_loadenv_sources_the_files_with_allexport(
    xsh: FakeSession,
    envstack: Callable[..., Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("A=1\n")
    (tmp_path / "other.env").write_text("B=2\n")
    assert envstack("loadenv") == 0
    assert envstack("loadenv", "other.env", "missing.env", ".env") == 0
    assert xsh.sourced == [
        ["--suppress-skip-message", "set -a\nA=1\n\nset +a"],
        ["--suppress-skip-message", "set -a\nB=2\n\nA=1\n\nset +a"],
    ]
    assert "ignore missing.env" in capsys.readouterr().err


def test_push_and_loadenv_pushes_first(
    envstack: Callable[..., Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("A=1\n")
    envstack("push-and-loadenv")
    assert envstack("pope") == 0
