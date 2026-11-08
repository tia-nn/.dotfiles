"""abbrevs（入力中の略語を展開する）。対話シェルだけで読む。

xontrib abbrevs（xontrib-abbrevs）を先に読んでおく必要がある。読まれていなければ何もしない。
展開した後の `<edit>` の位置にカーソルが移る。
"""

import os
import shutil
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from xontrib.dotfiles._changes import Changes
from xontrib.dotfiles._git import current_branch, default_branch

if TYPE_CHECKING:
    from collections.abc import MutableMapping

    from prompt_toolkit.buffer import Buffer
    from xonsh.built_ins import XonshSession

_changes = Changes()

type Expansion = str | Callable[[], str]
"""展開後の文字列。関数なら、展開するときに呼ぶ"""
type Abbrev = Callable[[str, Buffer], str]
"""xontrib abbrevs に渡す関数（word, buffer を受け取り、置き換える文字列を返す）"""


def _expand(expansion: Expansion) -> str:
    return expansion() if callable(expansion) else expansion


def head_only(expansion: Expansion) -> Abbrev:
    """行の先頭に書いたときだけ展開する"""

    def abbrev(word: str, buffer: Buffer) -> str:
        return _expand(expansion) if buffer.text.startswith(word) else word

    return abbrev


def after(command: str, expansion: Expansion) -> Abbrev:
    """command で始まる行の中でだけ展開する"""

    def abbrev(word: str, buffer: Buffer) -> str:
        return _expand(expansion) if buffer.text.startswith(command) else word

    return abbrev


def _docker_command(xsh: XonshSession) -> str | None:
    """Docker 互換のコマンド。$DOCKER_COMMAND、docker、podman の順に探す"""
    if command := xsh.env.get("DOCKER_COMMAND"):
        return str(command)
    path = os.pathsep.join(xsh.env.get("PATH", []))
    return next((c for c in ("docker", "podman") if shutil.which(c, path=path)), None)


def _abbrevs(xsh: XonshSession, docker: str | None) -> dict[str, Abbrev]:
    # 分からないときは、あとで書き換える目印（<edit>）を入れる
    def default() -> str:
        return default_branch(xsh.env.detype()) or "<edit>"

    def current() -> str:
        return current_branch(xsh.env.detype()) or "<edit>"

    abbrevs = {
        # tools
        "cp": head_only("cp -r"),
        "c": head_only("clear"),
        "l": head_only("ls -alh"),
        "la": head_only("ls -a"),
        "untar": head_only("tar xvf"),
        "unzips": head_only("unzip -O sjis"),
        # dotfiles
        "sx": head_only("dotfiles-reload"),
        "cx": head_only("code $DOTFILES"),
        # git
        "g": head_only("git"),
        "gcl": head_only("git clone"),
        "gini": head_only("git init"),
        "ga": head_only("git add"),
        "gaa": head_only("git add --all"),
        "gmv": head_only("git mv"),
        "grstr": head_only("git restore"),
        "grstrm": head_only(lambda: f"git restore --source={default()}"),
        "grstrh": head_only("git restore --source HEAD"),
        "grm": head_only("git rm"),
        "grmc": head_only("git rm --cached"),
        "gsch": head_only("git sparse-checkout"),
        "gbis": head_only("git bisect"),
        "gd": head_only("git diff"),
        "gg": head_only("git grep"),
        "gl": head_only("git log"),
        "glg": head_only("git log --graph --oneline --all"),
        "gln": head_only("git log --graph --oneline --all --max-count"),
        "glmn": head_only(lambda: f"git log --graph --oneline --branches={default()} --max-count"),
        "gsh": head_only("git show"),
        "gs": head_only("git status"),
        "gb": head_only("git branch"),
        "gc": head_only('git commit --message "<edit>"'),
        "gm": head_only("git merge"),
        "grb": head_only("git rebase"),
        "grst": head_only("git reset"),
        "gsw": head_only("git switch"),
        "gswc": head_only("git switch --create"),
        "gtag": head_only("git tag"),
        "gf": head_only("git fetch"),
        "gpl": head_only("git pull"),
        "gplo": head_only("git pull origin"),
        "gploh": head_only(lambda: f"git pull origin {current()}"),
        "gps": head_only("git push"),
        "gpso": head_only("git push origin"),
        "gpsoh": head_only(lambda: f"git push origin {current()}"),
        "gst": head_only("git stash"),
        "gsm": head_only("git submodule"),
        "grmt": head_only("git remote"),
        "gwt": head_only("git worktree"),
        "gcf": head_only("git config"),
        "ggc": head_only("git gc"),
        "@b": after("git", current),
    }
    if docker is not None:
        abbrevs.update(_docker_abbrevs(docker))
    return abbrevs


def _docker_abbrevs(docker: str) -> dict[str, Abbrev]:
    return {
        "dc": head_only(docker),
        "dimg": head_only(f"{docker} images"),
        "dlsi": head_only(f"{docker} image ls"),
        "dbld": head_only(f"{docker} build ./"),
        "drun": head_only(f"{docker} run"),
        "-itr": after(docker, "-it --rm"),
        "dexe": head_only(f"{docker} exec -it"),
        "drm": head_only(f"{docker} rm"),
        "drmi": head_only(f"{docker} rmi"),
        "diprn": head_only(f"{docker} image prune --force"),
        "dps": head_only(f"{docker} ps"),
        "dpsa": head_only(f"{docker} ps -a"),
        "dst": head_only(f"{docker} start"),
        "dstp": head_only(f"{docker} stop"),
        "restart": head_only(f"{docker} restart"),
        "dpl": head_only(f"{docker} pull"),
        "dvl": head_only(f"{docker} volume"),
        "dcc": head_only(f"{docker}-compose"),
        "dcu": head_only(f"{docker}-compose up"),
        "dcud": head_only(f"{docker}-compose up -d"),
        "dce": head_only(f"{docker}-compose exec"),
        "dcd": head_only(f"{docker}-compose down"),
        "dcdv": head_only(f"{docker}-compose down -v"),
        "dcs": head_only(f"{docker}-compose stop"),
        "dcr": head_only(f"{docker}-compose rm"),
        "dccc": head_only(f"{docker}-compose config"),
    }


def _load_xontrib_(xsh: XonshSession, **_: Any) -> None:
    target: MutableMapping[str, Any] | None = getattr(xsh.builtins, "abbrevs", None)
    if target is None:
        return
    for word, abbrev in _abbrevs(xsh, _docker_command(xsh)).items():
        _changes.set(target, word, abbrev)


def _unload_xontrib_(xsh: XonshSession, **_: Any) -> None:
    _changes.restore()
