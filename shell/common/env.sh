# shellcheck shell=sh
# どのシェルからでも読み込む共通の環境変数と PATH。
#   bash:  . "$DOTFILES/shell/common/env.sh"
#   zsh:   emulate sh -c '. "$DOTFILES/shell/common/env.sh"'
#   xonsh: source-bash "$DOTFILES/shell/common/env.sh"
#
# 決まりごと:
#   - POSIX sh で書く（mac の /bin/sh は bash 3.2、Debian は dash）。
#   - 環境変数と PATH だけを書く。シェル関数の定義や `eval "$(xxx init -)"` はシェル別の rc に書く。
#   - 何度読み込んでも同じ結果になるようにする（PATH は _dotfiles_path_prepend で重複させない）。
#   - 何も出力しない。

# _dotfiles_path_prepend DIR: DIR が存在すれば PATH の先頭に置く
#   すでに PATH にあれば取り除いてから先頭に置く（重複させず、順番も保つ）。
#   mac では /etc/zprofile の path_helper が引き継いだ PATH を後ろに回すので、単に飛ばすだけでは足りない。
_dotfiles_path_prepend() {
    [ -d "$1" ] || return 0
    _dotfiles_rest=":${PATH:-}:"
    while :; do
        case $_dotfiles_rest in
            *":$1:"*) _dotfiles_rest="${_dotfiles_rest%%":$1:"*}:${_dotfiles_rest#*":$1:"}" ;;
            *) break ;;
        esac
    done
    _dotfiles_rest=${_dotfiles_rest#:}
    _dotfiles_rest=${_dotfiles_rest%:}
    PATH="$1${_dotfiles_rest:+:$_dotfiles_rest}"
    unset _dotfiles_rest
}

# --- 自分で入れたコマンド ---
_dotfiles_path_prepend "$HOME/.local/bin"

# --- pyenv（pyenv init は各シェルの rc で行う）---
if [ -d "$HOME/.pyenv" ]; then
    export PYENV_ROOT="$HOME/.pyenv"
    _dotfiles_path_prepend "$PYENV_ROOT/bin"
    _dotfiles_path_prepend "$PYENV_ROOT/shims"
fi

# --- Haxe ---
if [ -d "$HOME/.haxe-versions/default" ]; then
    export HAXE_PATH="$HOME/.haxe-versions/default"
    _dotfiles_path_prepend "$HAXE_PATH"
fi
_dotfiles_path_prepend "$HOME/.haxe-versions/hashlink"

# --- npm（npm config -g set prefix=$HOME/.npm）---
if [ -d "$HOME/.npm" ]; then
    export NPM_BIN="$HOME/.npm/bin"
    _dotfiles_path_prepend "$NPM_BIN"
fi

# --- n（Node.js のバージョン管理）---
if [ -d "$HOME/.local/apps/n" ]; then
    export N_PREFIX="$HOME/.local/apps/n"
    _dotfiles_path_prepend "$N_PREFIX/bin"
fi

# --- Intel FPGA（Quartus / Questa）---
_dotfiles_fpga="$HOME/.local/apps/intelFPGA_lite"
if [ -d "$_dotfiles_fpga/22.1std/quartus" ]; then
    _dotfiles_path_prepend "$_dotfiles_fpga/22.1std/quartus/bin"
    export QSYS_ROOTDIR="$_dotfiles_fpga/22.1std/quartus/sopc_builder/bin"
fi
if [ -d "$_dotfiles_fpga/22.1std/questa_fse" ]; then
    _dotfiles_path_prepend "$_dotfiles_fpga/22.1std/questa_fse/bin"
    # ライセンスファイル（*.dat）を : 区切りで並べる
    _dotfiles_license=''
    for _dotfiles_dat in "$_dotfiles_fpga"/*.dat; do
        [ -e "$_dotfiles_dat" ] || continue
        _dotfiles_license="${_dotfiles_license:+$_dotfiles_license:}$_dotfiles_dat"
    done
    [ -z "$_dotfiles_license" ] || export LM_LICENSE_FILE="$_dotfiles_license"
    unset _dotfiles_license _dotfiles_dat
fi
unset _dotfiles_fpga

export PATH
unset -f _dotfiles_path_prepend
