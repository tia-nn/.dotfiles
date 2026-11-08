#!/bin/sh
# dotfiles のインストーラの入口。python3 があるか確認して install.py を実行する。
# 使い方は ./install.sh --help を参照。
set -eu

# CDPATH が設定されていると cd がパスを出力するので、空にして出力も捨てる
DOTFILES=$(CDPATH='' cd -- "$(dirname -- "$0")" >/dev/null && pwd -P)
PYTHON=${DOTFILES_PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    cat >&2 <<'EOF'
error: python3 (3.9 or later) is required.
  Debian/Ubuntu: sudo apt install python3
  Fedora:        sudo dnf install python3
  macOS:         xcode-select --install
EOF
    exit 1
fi

if ! "$PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 9))'; then
    echo "error: python3 3.9 or later is required (found: $("$PYTHON" -V 2>&1))" >&2
    exit 1
fi

# -s: ユーザーの site-packages を読まない  -B: リポジトリに __pycache__ を作らない
exec "$PYTHON" -s -B "$DOTFILES/install.py" "$@"
