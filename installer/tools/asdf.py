"""asdf（Python・Node.js・Haxe などのバージョン管理）を入れる。

1. asdf 本体を ~/.local/bin/asdf に置く。v0.16 以降は1つのバイナリなので、GitHub のリリースから
   OS と CPU に合うものを置くだけでよい。すでにあれば入れ直さない。
2. packages.py の ASDF_PLUGINS のプラグインを追加する。
3. packages.py の ASDF_GLOBAL のバージョンを入れて、全体の既定（~/.tool-versions）にする。
   すでに ~/.tool-versions にあるものは変えない。

shims（${ASDF_DATA_DIR:-~/.asdf}/shims）は shell/common/env.sh が PATH に入れる。
https://asdf-vm.com/guide/getting-started.html
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from ..archive import extract_tar
from ..context import Context
from ..github import find_asset, latest_release
from ..loader import get_str_dict, get_str_list, load_module

REPO = "asdf-vm/asdf"
OS_NAMES = {"linux": "linux", "mac": "darwin"}
ARCH_NAMES = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}


def asset_suffix(os_name: str, machine: str) -> str | None:
    """リリースのアセット名の末尾（例: -linux-amd64.tar.gz）。対応していなければ None"""
    arch = ARCH_NAMES.get(machine.lower())
    if arch is None or os_name not in OS_NAMES:
        return None
    return f"-{OS_NAMES[os_name]}-{arch}.tar.gz"


def data_dir(ctx: Context) -> Path:
    return Path(os.environ.get("ASDF_DATA_DIR") or ctx.home / ".asdf")


def command_env(ctx: Context) -> dict[str, str]:
    """asdf と、asdf で入れたコマンド（shims）を使える環境変数。

    インストールした直後は、シェルの PATH にまだ ~/.local/bin や shims が入っていないことがあるので足す。
    """
    env = dict(os.environ)
    paths = [str(ctx.home / ".local" / "bin"), str(data_dir(ctx) / "shims"), env.get("PATH", "")]
    env["PATH"] = os.pathsep.join(p for p in paths if p)
    return env


def global_versions(ctx: Context) -> dict[str, str]:
    """~/.tool-versions に書かれているツールとバージョン"""
    path = ctx.home / os.environ.get("ASDF_DEFAULT_TOOL_VERSIONS_FILENAME", ".tool-versions")
    if not path.is_file():
        return {}
    versions = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("#", 1)[0].split()
        if len(fields) >= 2:
            versions[fields[0]] = fields[1]
    return versions


def installed_plugins(asdf: Path, env: dict[str, str]) -> set[str]:
    result = subprocess.run(
        [str(asdf), "plugin", "list"], capture_output=True, text=True, env=env, check=False
    )
    if result.returncode != 0:
        return set()
    return {line.split()[0] for line in result.stdout.splitlines() if line.strip()}


class ResolveError(Exception):
    """バージョンを決められなかった"""


STABLE_VERSION = re.compile(r"\d+(\.\d+)*")
NODE_RELEASES = "https://nodejs.org/dist/index.json"


def latest_stable(versions: list[str]) -> str | None:
    """数字だけのバージョン（安定版）のうち最大のもの。

    asdf latest は Python の free-threaded 版（3.15.2t など）も最新として返すので使わない。
    """
    stable = [v for v in versions if STABLE_VERSION.fullmatch(v)]
    if not stable:
        return None
    return max(stable, key=lambda v: tuple(int(n) for n in v.split(".")))


def node_lts(releases: list[dict[str, Any]]) -> str | None:
    """Node.js の公式のリリース一覧（新しい順）から、最新の LTS のバージョン。

    asdf-nodejs の resolve lts は情報が古いことがある（v26 が LTS になっても v24 を返した）ので使わない。
    """
    for release in releases:
        if release.get("lts"):
            return str(release["version"]).lstrip("v")
    return None


def node_releases() -> list[dict[str, Any]]:
    with urllib.request.urlopen(NODE_RELEASES, timeout=30) as response:
        data: list[dict[str, Any]] = json.load(response)
    return data


def resolve_version(asdf: Path, tool: str, spec: str, env: dict[str, str]) -> str:
    """"latest"（最新の安定版）や "lts"（Node.js の最新の LTS）を実際のバージョン番号にする。

    それ以外はそのまま返す。決められなければ ResolveError（理由付き）を投げる。
    """
    if spec == "lts" and tool == "nodejs":
        try:
            releases = node_releases()
        except (OSError, ValueError) as e:
            raise ResolveError(f"{NODE_RELEASES}: {e}") from e
        version = node_lts(releases)
        if version is None:
            raise ResolveError(f"no LTS release in {NODE_RELEASES}")
        return version
    if spec != "latest":
        return spec

    result = subprocess.run(
        [str(asdf), "list", "all", tool], capture_output=True, text=True, env=env, check=False
    )
    if result.returncode != 0:
        raise ResolveError((result.stderr or result.stdout).strip() or f"exit code {result.returncode}")
    version = latest_stable(result.stdout.split())
    if version is None:
        raise ResolveError(f"no stable version in `asdf list all {tool}`")
    return version


def install_binary(ctx: Context, dest: Path) -> bool:
    suffix = asset_suffix(ctx.os_name, platform.machine())
    if suffix is None:
        ctx.warn(f"asdf: unsupported platform {ctx.os_name} {platform.machine()}")
        return False
    if ctx.dry_run:
        ctx.announce("download", f"latest {REPO} release (*{suffix})", "->", dest)
        return True

    release = latest_release(REPO)
    asset = find_asset(release, suffix)
    if asset is None:
        ctx.warn(f"asdf {release.get('tag_name')}: no asset *{suffix}")
        return False
    name, url = asset
    ctx.mkdir(dest.parent)
    # 同じファイルシステムの中で動かせるよう、置き場所の隣で展開する
    with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
        archive = Path(tmp) / name
        ctx.download(url, archive)
        ctx.announce("tar", "-xzf", archive, "-C", tmp)
        extract_tar(archive, Path(tmp))
        ctx.move(Path(tmp) / "asdf", dest)
    dest.chmod(0o755)
    return True


def install(ctx: Context) -> bool:
    # 1. asdf 本体
    binary = ctx.home / ".local" / "bin" / "asdf"
    found = shutil.which("asdf")
    if binary.exists() or found:
        asdf = binary if binary.exists() else Path(str(found))
        ctx.info(f"ok: {asdf}")
    else:
        if not install_binary(ctx, binary):
            return False
        asdf = binary

    try:
        module = load_module(ctx.dotfiles / "packages.py")
        plugins = get_str_list(module, "ASDF_PLUGINS")
        wanted_versions = get_str_dict(module, "ASDF_GLOBAL")
    except ValueError as e:
        ctx.warn(str(e))
        return False
    env = command_env(ctx)
    # dry-run でまだ asdf がないときは、何も入っていないものとして表示する
    exists = asdf.exists()

    # 2. プラグイン
    installed = installed_plugins(asdf, env) if exists else set()
    ok = True
    for plugin in plugins:
        if plugin in installed:
            ctx.info(f"ok: asdf plugin {plugin}")
        else:
            ok = ctx.run(asdf, "plugin", "add", plugin, env=env) and ok
    if not ok:
        return False

    # 3. 全体の既定のバージョン
    current = global_versions(ctx)
    for tool, spec in wanted_versions.items():
        if tool in current:
            ctx.info(f"ok: {tool} {current[tool]} (~/.tool-versions)")
            continue
        if not exists:
            # dry-run で、まだ asdf がないときは決められないので、指定をそのまま表示する
            version = f"<{spec}>"
        else:
            try:
                version = resolve_version(asdf, tool, spec, env)
            except ResolveError as e:
                ctx.warn(f"asdf: cannot resolve {tool} {spec}: {e}")
                ok = False
                continue
        ok = (
            ctx.run(asdf, "install", tool, version, env=env)
            and ctx.run(asdf, "set", "-u", tool, version, env=env)
            and ok
        )
    return ok
