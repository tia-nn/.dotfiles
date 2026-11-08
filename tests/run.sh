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
        shellcheck) set -- shellcheck --shell=sh install.sh tests/run.sh ;;
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
