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

# --- asdf（Python などのバージョン管理。asdf 本体は ~/.local/bin、各ツールは shims から呼ぶ）---
# https://asdf-vm.com/guide/getting-started.html
_dotfiles_path_prepend "${ASDF_DATA_DIR:-$HOME/.asdf}/shims"

# --- Neko のライブラリ（haxelib が使う）---
# TODO: 暫定の対応。asdf の Neko（~/.tool-versions のバージョン）の場所を LD_LIBRARY_PATH に入れる。
#   - Linux 版の haxelib は libneko.so.2 を探す場所（RUNPATH）を持っていないので、このままでは起動しない。
#   - asdf-haxe の対策（asdf cmd haxe neko dylibs link）は asdf v0.20 では呼べず、
#     スクリプトを直接実行してリンクを作っても Linux では効かない。
#   - OS の neko パッケージでは libneko は見つかるが、std.ndll が見つからずに失敗する。
#   asdf-haxe 側で直ったら消す。mac（@rpath/libneko.2.dylib）では未確認。
#   https://github.com/asdf-community/asdf-haxe#troubleshooting
if [ -f "$HOME/${ASDF_DEFAULT_TOOL_VERSIONS_FILENAME:-.tool-versions}" ]; then
    while read -r _dotfiles_tool _dotfiles_version _dotfiles_rest || [ -n "${_dotfiles_tool:-}" ]; do
        [ "${_dotfiles_tool:-}" = neko ] || continue
        _dotfiles_neko="${ASDF_DATA_DIR:-$HOME/.asdf}/installs/neko/${_dotfiles_version:-}/bin"
        if [ -d "$_dotfiles_neko" ]; then
            case ":${LD_LIBRARY_PATH:-}:" in
                *":$_dotfiles_neko:"*) ;;
                *) export LD_LIBRARY_PATH="$_dotfiles_neko${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;;
            esac
        fi
        break
    done <"$HOME/${ASDF_DEFAULT_TOOL_VERSIONS_FILENAME:-.tool-versions}"
    unset _dotfiles_tool _dotfiles_version _dotfiles_rest _dotfiles_neko
fi

# --- HashLink（asdf のプラグインがないので手で ~/.haxe-versions/hashlink に置く）---
_dotfiles_path_prepend "$HOME/.haxe-versions/hashlink"

# --- npm（グローバルインストール先。install.sh tools npm が prefix を ~/.npm にする）---
if [ -d "$HOME/.npm" ]; then
    export NPM_BIN="$HOME/.npm/bin"
    _dotfiles_path_prepend "$NPM_BIN"
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
