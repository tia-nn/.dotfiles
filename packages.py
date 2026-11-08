"""インストールするものの一覧。install.sh packages / install.sh tools asdf が使う。

すでに入っているものは飛ばすので、何度実行しても同じ結果になる。
"""

# --- OS のパッケージ（install.sh packages）---
# asdf-python は内部で pyenv の python-build を使うので、Python のビルドに必要なものは
# https://github.com/pyenv/pyenv/wiki#suggested-build-environment に従う

APT = [
    # 基本
    "curl", "git", "unzip", "zsh", "fontconfig",
    # asdf-nodejs が使う（https://asdf-vm.com/guide/getting-started.html）
    "dirmngr", "gpg", "gawk",
    # asdf で Python をビルドする
    "build-essential", "libssl-dev", "zlib1g-dev", "libbz2-dev", "libreadline-dev", "libsqlite3-dev",
    "libncurses-dev", "xz-utils", "tk-dev", "libxml2-dev", "libxmlsec1-dev", "libffi-dev", "liblzma-dev",
]  # fmt: skip

DNF = [
    # 基本
    "curl", "git", "unzip", "zsh", "fontconfig",
    # asdf-nodejs が使う
    "gnupg2", "gawk",
    # asdf で Python をビルドする
    "make", "gcc", "patch", "zlib-devel", "bzip2", "bzip2-devel", "readline-devel", "sqlite", "sqlite-devel",
    "openssl-devel", "tk-devel", "libffi-devel", "xz-devel", "libuuid-devel", "gdbm-devel", "libnsl2-devel",
]  # fmt: skip

BREW = [
    # asdf が使う（https://asdf-vm.com/guide/getting-started.html）
    "coreutils",
    # asdf で Python をビルドする
    "openssl", "readline", "sqlite3", "xz", "zlib", "tcl-tk",
]  # fmt: skip

# --- asdf（install.sh tools asdf）---
# プラグインの名前は https://github.com/asdf-vm/asdf-plugins の短縮名。

ASDF_PLUGINS = [
    "python",
    "nodejs",
    "haxe",
    # haxelib が Neko のライブラリを使う
    "neko",
]

# インストールして、全体の既定のバージョン（~/.tool-versions）にするもの。
# すでに ~/.tool-versions にあるものは変えない。
# バージョンを上げるときは asdf install と asdf set -u を手で行う。
# "latest" は最新の安定版（3.14.2 のような数字だけのもの）、
# "lts" は Node.js の最新の LTS（nodejs.org の一覧）。
# Python はソースからビルドするので数分〜10分ほどかかる（ビルドに必要なものは install.sh packages で入る）。
ASDF_GLOBAL = {
    "python": "latest",
    "nodejs": "lts",
    "haxe": "latest",
    "neko": "latest",
}
