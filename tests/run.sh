#!/bin/sh
# 静的チェックとテストをまとめて実行する。
#   sh tests/run.sh               # 全部（shellcheck, ruff, mypy, pytest）
#   sh tests/run.sh pytest mypy   # 指定したものだけ
set -eu

cd "$(CDPATH='' cd -- "$(dirname -- "$0")/.." >/dev/null && pwd -P)"

checks=${*:-shellcheck ruff mypy pytest}
status=0

for check in $checks; do
    echo "==> $check"
    case $check in
        # シェルの種類は各ファイルの shebang か `# shellcheck shell=...` で決まる（zsh は対象外）
        shellcheck) set -- shellcheck -x install.sh tests/run.sh shell/common/env.sh shell/bash/*.sh ;;
        ruff) set -- ruff check . ;;
        mypy) set -- mypy ;;
        pytest) set -- python3 -m pytest ;;
        *)
            echo "unknown check: $check" >&2
            status=1
            continue
            ;;
    esac
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "$1 not found" >&2
        status=1
        continue
    fi
    "$@" || status=1
done

exit "$status"
