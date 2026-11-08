"""git のグローバル設定（git config --global）。値が違うものだけを設定する。"""

from __future__ import annotations

import shutil
import subprocess

from ..context import Context

# 公開しているメールアドレスなので直書きする
SETTINGS = {
    "user.name": "tia-nn",
    "user.email": "yknms3533642@yahoo.co.jp",
    "init.defaultBranch": "master",
    "diff.indentHeuristic": "true",
}


def current_value(key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "--global", "--get", key], capture_output=True, text=True, check=False
    )
    return result.stdout.rstrip("\n") if result.returncode == 0 else None


def install(ctx: Context) -> bool:
    if shutil.which("git") is None:
        ctx.warn("git is not installed (run: install.sh packages)")
        return False
    ok = True
    for key, value in SETTINGS.items():
        if current_value(key) == value:
            ctx.info(f"ok: git config {key}")
        else:
            ok = ctx.run("git", "config", "--global", key, value) and ok
    return ok
