# zsh のログインシェルで読む。~/.zprofile に install.sh が挿入したブロックから読み込まれる。
#
# PATH は ~/.zshenv ではなくここで設定する。
# mac では /etc/zprofile の path_helper が、それより前に設定した PATH の順番を変えてしまうため。

# 共通層は POSIX sh で書かれているので、読む間だけ sh 互換モードにする
emulate sh -c '. "$DOTFILES/shell/common/env.sh"'
