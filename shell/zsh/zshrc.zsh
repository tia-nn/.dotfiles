# zsh の rc。~/.zshrc に install.sh が挿入したブロックから読み込まれる。

# ログインしない対話シェルでも共通層を読む（何度読んでも同じ結果になる）
emulate sh -c '. "$DOTFILES/shell/common/env.sh"'

if (( $+commands[pyenv] )); then
    eval "$(pyenv init - zsh)"
fi
