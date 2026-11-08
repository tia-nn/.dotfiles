"""npm のグローバルインストール先を ~/.npm にする（sudo なしで npm install -g できるように）。

ユーザーの設定（~/.npmrc）に書く。~/.npm/bin は shell/common/env.sh が PATH に入れる。
Node.js は asdf で入れる（install.sh tools asdf）ので、asdf の shims から npm を呼ぶ。
"""

from __future__ import annotations

import shutil
import subprocess

from ..context import Context
from .asdf import command_env


def install(ctx: Context) -> bool:
    env = command_env(ctx)
    prefix = str(ctx.home / ".npm")
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
