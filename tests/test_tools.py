from __future__ import annotations

import io
import os
import platform
import shutil
import tarfile
from pathlib import Path
from typing import Any

import pytest
from helpers import errors, output, snapshot

from installer import tools
from installer.context import Context
from installer.github import find_asset
from installer.tools import Tool, asdf, fonts, git, npm, xonsh


@pytest.fixture
def no_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name, **kwargs: None)


@pytest.fixture
def all_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name, **kwargs: f"/usr/bin/{name}")


def record_runs(ctx: Context, monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """ctx.run を、実行せずに引数を記録するだけにする"""
    runs: list[list[str]] = []

    def fake_run(*args: object, env: object = None) -> bool:
        runs.append([str(a) for a in args])
        return True

    monkeypatch.setattr(ctx, "run", fake_run)
    return runs


def write_script(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)


# --- install_tools ---


def test_install_tools_rejects_unknown_names(ctx: Context) -> None:
    assert not tools.install_tools(["git", "bogus"], ctx)
    assert "unknown tools: bogus" in errors(ctx)


def test_install_tools_runs_default_tools_or_the_given_ones(
    ctx: Context, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[str] = []

    def fake(name: str) -> Tool:
        def install(c: Context) -> bool:
            called.append(name)
            return True

        return Tool(name, "", install, default=name != "c")

    monkeypatch.setattr(tools, "TOOLS", {name: fake(name) for name in ("a", "b", "c")})
    assert tools.install_tools([], ctx)
    assert called == ["a", "b"]
    called.clear()
    assert tools.install_tools(["c", "a"], ctx)
    assert called == ["c", "a"]


def test_asdf_runs_before_npm() -> None:
    names = list(tools.TOOLS)
    assert names.index("asdf") < names.index("npm")


# --- git ---


@pytest.mark.usefixtures("all_commands")
def test_git_sets_only_different_values(ctx: Context, monkeypatch: pytest.MonkeyPatch) -> None:
    current = dict(git.SETTINGS, **{"user.email": "old@example.com"})
    del current["diff.indentHeuristic"]
    monkeypatch.setattr(git, "current_value", current.get)
    ctx.dry_run = True
    assert git.install(ctx)
    commands = [line for line in output(ctx).splitlines() if line.startswith("[dry-run]")]
    assert commands == [
        f"[dry-run] git config --global user.email {git.SETTINGS['user.email']}",
        "[dry-run] git config --global diff.indentHeuristic true",
    ]


@pytest.mark.usefixtures("no_commands")
def test_git_requires_git(ctx: Context) -> None:
    assert not git.install(ctx)


# --- asdf ---


@pytest.mark.parametrize(
    ("os_name", "machine", "expected"),
    [
        ("linux", "x86_64", "-linux-amd64.tar.gz"),
        ("linux", "aarch64", "-linux-arm64.tar.gz"),
        ("mac", "arm64", "-darwin-arm64.tar.gz"),
        ("mac", "x86_64", "-darwin-amd64.tar.gz"),
        ("linux", "riscv64", None),
    ],
)
def test_asdf_asset_suffix(os_name: str, machine: str, expected: str | None) -> None:
    assert asdf.asset_suffix(os_name, machine) == expected


def test_find_asset_skips_checksum_files() -> None:
    assert find_asset(ASDF_RELEASE, "-linux-amd64.tar.gz") == (
        "asdf-v0.20.2-linux-amd64.tar.gz",
        "https://example.com/amd64",
    )
    assert find_asset({"assets": []}, "-linux-amd64.tar.gz") is None


def test_global_versions(ctx: Context, home: Path) -> None:
    assert asdf.global_versions(ctx) == {}
    (home / ".tool-versions").write_text("nodejs 22.13.1\n# comment\npython 3.13.0 system  # fallback\n\n")
    assert asdf.global_versions(ctx) == {"nodejs": "22.13.1", "python": "3.13.0"}


def test_resolve_version_keeps_exact_versions() -> None:
    assert asdf.resolve_version(Path("/nonexistent/asdf"), "haxe", "4.3.6", {}) == "4.3.6"


def test_latest_stable_skips_free_threaded_and_prereleases() -> None:
    versions = ["3.9.25", "3.14.2", "3.14.2t", "3.15.0a1", "3.15.2t", "3.13-dev", "pypy3.10-7.3", "3.14.10"]
    assert asdf.latest_stable(versions) == "3.14.10"
    assert asdf.latest_stable(["2.4.0", "2.4.1"]) == "2.4.1"
    assert asdf.latest_stable(["dev", "nightly"]) is None


def test_node_lts_picks_the_newest_lts() -> None:
    releases: list[dict[str, Any]] = [
        {"version": "v27.0.0", "lts": False},
        {"version": "v26.13.0", "lts": "Lithium"},
        {"version": "v24.22.2", "lts": "Krypton"},
    ]
    assert asdf.node_lts(releases) == "26.13.0"
    assert asdf.node_lts([{"version": "v27.0.0", "lts": False}]) is None


def test_resolve_version_latest_uses_asdf_list_all(tmp_path: Path) -> None:
    fake = tmp_path / "asdf"
    write_script(
        fake,
        'case "$*" in\n'
        '  "list all python") printf "%s\\n" 3.14.2 3.15.0a1 3.15.2t ;;\n'
        '  *) echo "unknown plugin" >&2; exit 1 ;;\n'
        "esac\n",
    )
    assert asdf.resolve_version(fake, "python", "latest", {}) == "3.14.2"
    with pytest.raises(asdf.ResolveError, match="unknown plugin"):
        asdf.resolve_version(fake, "neko", "latest", {})


def test_resolve_version_lts_uses_nodejs_org(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(asdf, "node_releases", lambda: [{"version": "v26.13.0", "lts": "Lithium"}])
    assert asdf.resolve_version(Path("/nonexistent/asdf"), "nodejs", "lts", {}) == "26.13.0"


def make_asdf_tarball(path: Path) -> None:
    with tarfile.open(path, "w:gz") as tar:
        data = b"#!/bin/sh\n"
        info = tarfile.TarInfo("asdf")
        info.size = len(data)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(data))


ASDF_RELEASE: dict[str, Any] = {
    "tag_name": "v0.20.2",
    "assets": [
        {"name": "asdf-v0.20.2-linux-amd64.tar.gz.md5", "browser_download_url": "https://example.com/md5"},
        {"name": "asdf-v0.20.2-linux-amd64.tar.gz", "browser_download_url": "https://example.com/amd64"},
        {"name": "asdf-v0.20.2-linux-arm64.tar.gz", "browser_download_url": "https://example.com/arm64"},
    ],
}


@pytest.mark.usefixtures("no_commands")
def test_asdf_installs_everything_on_a_new_machine(
    ctx: Context, home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    downloaded: list[str] = []

    def fake_download(url: str, dest: Path) -> None:
        downloaded.append(url)
        make_asdf_tarball(dest)

    monkeypatch.setattr(asdf, "latest_release", lambda repo: ASDF_RELEASE)
    monkeypatch.setattr(ctx, "download", fake_download)
    monkeypatch.setattr(platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(asdf, "installed_plugins", lambda path, env: set())
    monkeypatch.setattr(asdf, "resolve_version", lambda path, tool, spec, env: f"{tool}-{spec}")
    runs = record_runs(ctx, monkeypatch)

    assert asdf.install(ctx)
    binary = home / ".local/bin/asdf"
    assert binary.is_file()
    assert os.access(binary, os.X_OK)
    assert downloaded == ["https://example.com/amd64"]
    assert sorted(p.name for p in binary.parent.iterdir()) == ["asdf"]
    a = str(binary)
    assert runs == [
        [a, "plugin", "add", "python"],
        [a, "plugin", "add", "nodejs"],
        [a, "plugin", "add", "haxe"],
        [a, "plugin", "add", "neko"],
        [a, "install", "python", "python-latest"],
        [a, "set", "-u", "python", "python-latest"],
        [a, "install", "nodejs", "nodejs-lts"],
        [a, "set", "-u", "nodejs", "nodejs-lts"],
        [a, "install", "haxe", "haxe-latest"],
        [a, "set", "-u", "haxe", "haxe-latest"],
        [a, "install", "neko", "neko-latest"],
        [a, "set", "-u", "neko", "neko-latest"],
    ]


@pytest.mark.usefixtures("no_commands")
@pytest.mark.parametrize("error", [OSError("offline"), ValueError("Expecting value")])
def test_asdf_warns_when_the_release_cannot_be_fetched(
    ctx: Context, home: Path, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    def broken(repo: str) -> dict[str, Any]:
        raise error

    monkeypatch.setattr(asdf, "latest_release", broken)
    monkeypatch.setattr(platform, "machine", lambda: "x86_64")
    assert not asdf.install(ctx)
    assert "cannot get the latest" in errors(ctx)
    assert not (home / ".local/bin/asdf").exists()


@pytest.mark.usefixtures("no_commands")
def test_asdf_keeps_existing_global_versions(
    ctx: Context, home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_script(home / ".local/bin/asdf", "")
    (home / ".tool-versions").write_text("nodejs 20.0.0\nhaxe 4.3.6\n")
    monkeypatch.setattr(asdf, "latest_release", lambda repo: pytest.fail("should not download"))
    monkeypatch.setattr(asdf, "installed_plugins", lambda path, env: {"python", "nodejs", "haxe", "neko"})
    monkeypatch.setattr(asdf, "resolve_version", lambda path, tool, spec, env: "2.3.0")
    runs = record_runs(ctx, monkeypatch)

    assert asdf.install(ctx)
    a = str(home / ".local/bin/asdf")
    assert runs == [
        [a, "install", "python", "2.3.0"],
        [a, "set", "-u", "python", "2.3.0"],
        [a, "install", "neko", "2.3.0"],
        [a, "set", "-u", "neko", "2.3.0"],
    ]
    assert "ok: nodejs 20.0.0 (~/.tool-versions)" in output(ctx)
    assert "ok: asdf plugin haxe" in output(ctx)


@pytest.mark.usefixtures("no_commands")
def test_asdf_fails_when_a_version_cannot_be_resolved(
    ctx: Context, home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(asdf, "installed_plugins", lambda path, env: {"python", "nodejs", "haxe", "neko"})
    write_script(home / ".local/bin/asdf", 'echo "curl: command not found" >&2; exit 1\n')

    def offline() -> list[dict[str, Any]]:
        raise OSError("network is unreachable")

    monkeypatch.setattr(asdf, "node_releases", offline)
    record_runs(ctx, monkeypatch)
    assert not asdf.install(ctx)
    assert "cannot resolve python latest: curl: command not found" in errors(ctx)
    assert f"cannot resolve nodejs lts: {asdf.NODE_RELEASES}: network is unreachable" in errors(ctx)
    assert "cannot resolve haxe latest: curl: command not found" in errors(ctx)


@pytest.mark.usefixtures("no_commands")
def test_asdf_dry_run(ctx: Context, home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(asdf, "latest_release", lambda repo: pytest.fail("network access in dry-run"))
    monkeypatch.setattr(platform, "machine", lambda: "aarch64")
    ctx.dry_run = True
    assert asdf.install(ctx)
    out = output(ctx)
    a = f"{home}/.local/bin/asdf"
    assert "*-linux-arm64.tar.gz" in out
    assert f"[dry-run] {a} plugin add python" in out
    assert f"[dry-run] {a} install python '<latest>'" in out
    assert f"[dry-run] {a} install nodejs '<lts>'" in out
    assert f"[dry-run] {a} set -u haxe '<latest>'" in out
    assert snapshot(home) == []


def test_command_env_finds_asdf_and_shims(ctx: Context, home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", "/usr/bin")
    monkeypatch.delenv("ASDF_DATA_DIR", raising=False)
    assert asdf.command_env(ctx)["PATH"].split(os.pathsep) == [
        f"{home}/.local/bin",
        f"{home}/.asdf/shims",
        "/usr/bin",
    ]


# --- xonsh ---


def test_xonsh_creates_a_venv_and_links_it(ctx: Context, home: Path) -> None:
    ctx.dry_run = True
    assert xonsh.install(ctx)
    venv = home / ".local/share/dotfiles/venvs/xonsh"
    out = output(ctx)
    assert f"-m venv {venv}" in out
    assert f"{venv}/bin/python -m pip install 'xonsh[full]'" in out
    assert f"[dry-run] ln -s {venv}/bin/xonsh {home}/.local/bin/xonsh" in out
    assert snapshot(home) == []


def test_xonsh_only_links_when_already_installed(ctx: Context, home: Path) -> None:
    xonsh_bin = home / ".local/share/dotfiles/venvs/xonsh/bin/xonsh"
    xonsh_bin.parent.mkdir(parents=True)
    xonsh_bin.touch()
    assert xonsh.install(ctx)
    assert os.readlink(home / ".local/bin/xonsh") == str(xonsh_bin)
    assert "pip" not in output(ctx)


def test_xonsh_venv_follows_xdg_data_home(
    ctx: Context, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    assert xonsh.venv_dir(ctx) == tmp_path / "data/dotfiles/venvs/xonsh"


# --- npm ---


@pytest.fixture
def fake_npm(home: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """asdf の shims にある npm の代わり。config get prefix は prefix ファイルの中身を返す"""
    monkeypatch.setenv("PATH", "/usr/bin:/bin")
    monkeypatch.delenv("ASDF_DATA_DIR", raising=False)
    state = tmp_path / "prefix"
    state.write_text("/usr/local\n")
    write_script(
        home / ".asdf/shims/npm",
        f'case "$1 $2" in\n'
        f'    "config get") cat {state} ;;\n'
        f'    "config set") echo "$4" > {state} ;;\n'
        f"esac\n",
    )
    return state


def test_npm_sets_prefix_through_asdf_shims(ctx: Context, home: Path, fake_npm: Path) -> None:
    assert npm.install(ctx)
    assert fake_npm.read_text() == f"{home}/.npm\n"
    assert f"+ {home}/.asdf/shims/npm config set prefix {home}/.npm" in output(ctx)

    ctx.out.seek(0)
    ctx.out.truncate()
    assert npm.install(ctx)
    assert output(ctx) == f"ok: npm prefix {home}/.npm\n"


@pytest.mark.usefixtures("no_commands")
def test_npm_is_required(ctx: Context) -> None:
    assert not npm.install(ctx)
    assert "npm is not found (run: install.sh tools asdf)" in errors(ctx)


@pytest.mark.usefixtures("no_commands")
def test_npm_dry_run_before_node_is_installed(ctx: Context, home: Path) -> None:
    ctx.dry_run = True
    assert npm.install(ctx)
    assert output(ctx) == f"[dry-run] npm config set prefix {home}/.npm\n"


# --- fonts ---


def test_fonts_downloads_missing_fonts(ctx: Context, home: Path) -> None:
    ctx.dry_run = True
    assert fonts.install(ctx)
    font_dir = home / ".local/share/fonts/dotfiles"
    out = output(ctx)
    assert f"[dry-run] curl -fsSL -o {font_dir}/SourceHanCodeJP.ttc {fonts.SOURCE_HAN_CODE_JP}" in out
    assert "[dry-run] unzip NerdFontsSymbolsOnly.zip" in out
    assert snapshot(home) == []


@pytest.mark.usefixtures("all_commands")
def test_fonts_does_nothing_when_present(ctx: Context, home: Path) -> None:
    font_dir = home / ".local/share/fonts/dotfiles"
    font_dir.mkdir(parents=True)
    (font_dir / "SourceHanCodeJP.ttc").touch()
    (font_dir / "SymbolsNerdFontMono-Regular.ttf").touch()
    assert fonts.install(ctx)
    assert "fc-cache" not in output(ctx)
    assert "curl" not in output(ctx)


def test_fonts_on_mac_go_to_library_fonts(ctx: Context, home: Path) -> None:
    ctx.os_name = "mac"
    assert fonts.font_dir(ctx) == home / "Library/Fonts"
