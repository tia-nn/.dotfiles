# dotfiles

xonsh をメインにした dotfiles と、その環境を作るインストーラ。

- 対象: Debian 系（Debian / Ubuntu）、Fedora、macOS
- 何度実行しても同じ結果になり、途中で質問しない。`--dry-run` で何をするかだけを確認できる。
- 既存のファイルは消さずに退避してから置き換える。

## インストール

git と python3（3.9 以上）があれば動く。mac では `xcode-select --install` で両方入る。

```sh
git clone https://github.com/tia-nn/.dotfiles.git ~/.dotfiles
cd ~/.dotfiles
./install.sh --dry-run all   # 何をするか確認する
./install.sh all
```

終わったらシェルを開き直す。`~/.dotfiles` 以外の場所に clone しても動く。

### コマンド

| コマンド | 内容 |
|---|---|
| `./install.sh` / `./install.sh link` | 設定ファイルのリンクを作り、シェルの rc に読み込みの設定を入れる |
| `./install.sh packages` | OS のパッケージを入れる（Linux では sudo を使う。mac は Homebrew が必要） |
| `./install.sh tools [NAME...]` | ツールを入れる。名前を省略するとすべて |
| `./install.sh all` | 上の3つを順に |

どのコマンドにも `-n` / `--dry-run` を付けられる。`./install.sh --help` で一覧を表示する。

### ツール（`./install.sh tools`）

| 名前 | 内容 |
|---|---|
| `git` | `git config --global` の設定（ユーザー名など） |
| `asdf` | [asdf](https://asdf-vm.com/) を `~/.local/bin` に入れ、Python・Node.js・Haxe・Neko を入れて既定のバージョンにする |
| `xonsh` | xonsh と xontrib（abbrevs・vox）を、asdf の Python（`~/.tool-versions`）で作った専用の venv に入れ、`~/.local/bin/xonsh` にリンクする。足りないものだけを入れる |
| `npm` | npm のグローバルインストール先を `${XDG_DATA_HOME:-~/.local/share}/npm` にする（sudo なしで `npm install -g` できる） |
| `fonts` | 源ノ角ゴシック Code と Nerd Fonts Symbols を入れる |

Python はソースからビルドするので、初回は数分〜10分ほどかかる。

## インストールされるもの

### シェルの設定

ファイルごと置き換えず、次のブロックだけを挿入・更新する。ディストリビューションの既定の設定はそのまま残る。

```sh
# >>> dotfiles >>>
export DOTFILES="$HOME/.dotfiles"
. "$DOTFILES/shell/bash/profile.sh"
# <<< dotfiles <<<
```

| シェル | 挿入するファイル | 読み込むもの |
|---|---|---|
| bash（ログイン） | `~/.bash_profile`・`~/.bash_login`・`~/.profile` のうち bash が読むもの（どれもなければ `~/.profile`） | `shell/bash/profile.sh` |
| bash（対話） | `~/.bashrc` | `shell/bash/rc.sh` |
| zsh（ログイン） | `~/.zprofile` | `shell/zsh/zprofile.zsh` |
| zsh（対話） | `~/.zshrc` | `shell/zsh/zshrc.zsh` |

zsh は、mac では常に、Linux では zsh が入っているときだけ設定する。

PATH と環境変数は [`shell/common/env.sh`](shell/common/env.sh) にまとめてあり、どのシェルからも読み込む。

### xonsh

入口の [`shell/xonsh/rc.d/50_dotfiles.py`](shell/xonsh/rc.d/50_dotfiles.py) を `~/.config/xonsh/rc.d/50_dotfiles.py` にリンクする。xonsh は `~/.config/xonsh/rc.d` にある `*.py` / `*.xsh` を名前の順に読む（xonsh の標準の仕組み）。設定の本体は [`shell/xonsh/xontrib/dotfiles/`](shell/xonsh/xontrib/dotfiles/) にあり、入口から読む。

- その PC だけの設定は、`~/.config/xonsh/rc.d` に入口より後ろの名前（`90_local.xsh` など）で置く。dotfiles の設定の後に読まれるので、上書きできる。`~/.xonshrc` は rc.d より先に読まれるため、上書きには使えない。
- 以前のように `~/.config/xonsh/rc.d` がリポジトリへのリンクになっていたら、`install.sh link` がそのリンクを退避して、普通のディレクトリにする。
- 設定は xontrib に分けてある。rc.d は `xonsh -c` やスクリプトの実行でも読まれるので、対話用のものは対話シェルでだけ読む。読む順番は [`xontrib/dotfiles/__init__.py`](shell/xonsh/xontrib/dotfiles/__init__.py) にある。

  | xontrib | 読むとき | 中身 |
  |---|---|---|
  | `dotfiles.env` | 常に | `$DOTFILES`、`shell/common/env.sh`、traceback のログ |
  | `dotfiles.aliases` | 常に | `git-prune-localbranch`、`dotfiles-reload` |
  | `abbrevs`・`vox`（外部） | 対話 | `install.sh tools xonsh` で入れる。入っていなければ案内が出て、ほかは読む |
  | `dotfiles.prompt` | 対話 | プロンプト・入力・履歴・補完の `$変数` |
  | `dotfiles.abbrevs` | 対話 | abbrevs（xontrib abbrevs が入っているときだけ） |
  | `dotfiles.envstack` | 対話 | `loadenv`、`pushe`、`pope`、`push-and-loadenv` |

- 設定を変えたら `dotfiles-reload`（abbrev では `sx`）で読み込み直せる。1つだけなら `xontrib reload dotfiles.prompt` のようにする。
- xontrib を足すときは、`_load_xontrib_` で `Changes`（[`_changes.py`](shell/xonsh/xontrib/dotfiles/_changes.py)）を通して値を変え、`_unload_xontrib_` で元に戻す。`__init__.py` の一覧にも足す。
- 環境変数
  - `$DOCKER_COMMAND`: abbrevs で使う Docker 互換のコマンド（未設定なら docker、なければ podman）
  - `$GIT_DEFAULTBRANCH`: abbrevs などで使うデフォルトブランチ名（未設定なら git の `init.defaultBranch`）
- traceback のログは `~/.local/state/xonsh/traceback.log` に出る。

### 退避したファイル

置き換えたファイルは `~/.local/state/dotfiles/backup/<日時>/` に、`$HOME` からの相対パスのまま置かれる。

## 設定を変える

| 変えたいもの | 書く場所 |
|---|---|
| リンクする設定ファイル | [`links.py`](links.py) |
| OS のパッケージ、asdf のプラグインと既定のバージョン | [`packages.py`](packages.py) |
| PATH・環境変数 | [`shell/common/env.sh`](shell/common/env.sh)（POSIX sh で書く） |
| xonsh の設定 | [`shell/xonsh/xontrib/dotfiles/`](shell/xonsh/xontrib/dotfiles/)（`.py` で書く） |
| git の設定 | [`installer/tools/git.py`](installer/tools/git.py) |

asdf で入れたツールのバージョンを上げるときは手で行う（`~/.tool-versions` にあるものはインストーラが変えないため）。

```sh
asdf install nodejs <バージョン> && asdf set -u nodejs <バージョン>
```

## ディレクトリ構成

```
.
├── install.sh          # 入口。python3 を確認して install.py を呼ぶ
├── install.py
├── installer/          # インストーラ本体（Python 3.9 以上、標準ライブラリのみ）
├── links.py            # リンクの対応表
├── packages.py         # パッケージ・asdf の一覧
├── shell/
│   ├── common/         # どのシェルからも読む PATH・環境変数
│   ├── bash/
│   ├── zsh/
│   └── xonsh/          # rc.d/（入口）と xontrib/dotfiles/（設定の本体）
└── tests/              # pytest のテストと Docker のファイル
```

## テスト

Docker（Docker Desktop など）で、Debian・Fedora・Python 3.9 のコンテナを使う。テストはネットワークを使わない。

```sh
docker compose run --rm debian    # shellcheck, ruff, pytest
docker compose run --rm fedora
docker compose run --rm py39      # 対応する最も古い Python で mypy, pytest
```

一部だけ実行する例:

```sh
docker compose run --rm debian python3 -m pytest tests/test_links.py -k backup
```

実際にダウンロードしてインストールまで試すときは、ネットワークありでコンテナを使う（この PC には何もしない）。

```sh
docker compose build debian
docker run --rm -u root -v "$PWD:/dotfiles:ro" dotfiles-debian sh -c 'HOME=$(mktemp -d) sh install.sh all'
```

## 既知の問題

- **haxelib が libneko を見つけられない**（[#1](https://github.com/tia-nn/.dotfiles/issues/1)）: 暫定で `shell/common/env.sh` が asdf の Neko の場所を `LD_LIBRARY_PATH` に入れている。mac では未確認。
