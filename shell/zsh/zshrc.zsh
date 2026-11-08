# zsh の rc。~/.zshrc に install.sh が挿入したブロックから読み込まれる。

# ログインしない対話シェルでも共通層を読む（何度読んでも同じ結果になる）
emulate sh -c '. "$DOTFILES/shell/common/env.sh"'

# asdf の補完（https://asdf-vm.com/guide/getting-started.html）。
# 補完ファイルは、ないときと asdf 本体のほうが新しいとき（更新したとき）だけ作る
if (( $+commands[asdf] )); then
    _dotfiles_asdf_completions="${ASDF_DATA_DIR:-$HOME/.asdf}/completions"
    if [[ ! -f $_dotfiles_asdf_completions/_asdf || $commands[asdf] -nt $_dotfiles_asdf_completions/_asdf ]]; then
        mkdir -p "$_dotfiles_asdf_completions"
        asdf completion zsh > "$_dotfiles_asdf_completions/_asdf"
    fi
    fpath=("$_dotfiles_asdf_completions" $fpath)
    unset _dotfiles_asdf_completions
fi

autoload -Uz compinit && compinit
