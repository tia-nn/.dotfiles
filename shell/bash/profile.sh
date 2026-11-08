# shellcheck shell=sh
# ログインシェルで読む。~/.bash_profile・~/.bash_login・~/.profile のうち bash が読むものに、
# install.sh が挿入したブロックから読み込まれる。
#
# ~/.profile は dash などの sh からも読まれる（Debian のディスプレイマネージャなど）ので POSIX sh で書く。

. "$DOTFILES/shell/common/env.sh"

# 対話的な bash なら ~/.bashrc も読む。
# Debian / Fedora の既定の profile はすでに ~/.bashrc を読んでいるので、読み込み済みなら飛ばす。
# shellcheck source=/dev/null
if [ -n "${BASH_VERSION:-}" ] && [ -z "${_DOTFILES_BASHRC_LOADED:-}" ] && [ -f "$HOME/.bashrc" ]; then
    case $- in
        *i*) . "$HOME/.bashrc" ;;
    esac
fi
