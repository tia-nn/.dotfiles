# shellcheck shell=bash
# bash の rc。~/.bashrc に install.sh が挿入したブロックから読み込まれる。

_DOTFILES_BASHRC_LOADED=1

# 端末エミュレータなど、ログインしない対話シェルでも共通層を読む（何度読んでも同じ結果になる）
. "$DOTFILES/shell/common/env.sh"

# ここから下は対話シェルだけ（Fedora の既定の ~/.bashrc は非対話でも読まれる）
case $- in
    *i*) ;;
    *) return 0 ;;
esac

# asdf の補完
if command -v asdf >/dev/null 2>&1; then
    # shellcheck source=/dev/null
    . <(asdf completion bash)
fi
