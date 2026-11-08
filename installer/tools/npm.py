"""npm のグローバルインストール先を ${XDG_DATA_HOME:-~/.local/share}/npm にする。

sudo なしで npm install -g できるようにするため。
~/.npm は npm のキャッシュの既定の場所なので、混ざらないように別の場所にする。
ユーザーの設定（~/.npmrc）に書く。<prefix>/bin は shell/common/env.sh が PATH に入れる。
Node.js は asdf で入れる（install.sh tools asdf）ので、asdf の shims から npm を呼ぶ。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from ..context import Context
from .asdf import command_env


def prefix_dir(ctx: Context) -> Path:
    data_home = Path(os.environ.get("XDG_DATA_HOME") or ctx.home / ".local" / "share")
    return data_home / "npm"


def install(ctx: Context) -> bool:
    env = command_env(ctx)
    prefix = str(prefix_dir(ctx))
    npm = shutil.which("npm", path=env["PATH"])

    if npm is None:
        if ctx.dry_run:
            # この前の asdf で Node.js を入れる予定のときは、npm がある前提で表示する
            return ctx.run("npm", "config", "set", "prefix", prefix)
        ctx.warn("npm is not found (run: install.sh tools asdf)")
        return False

    current = subprocess.run(
        [npm, "config", "get", "prefix"], capture_output=True, text=True, env=env, check=False
    )
    if current.returncode == 0 and current.stdout.strip() == prefix:
        ctx.info(f"ok: npm prefix {prefix}")
        return True
    return ctx.run(npm, "config", "set", "prefix", prefix, env=env)
