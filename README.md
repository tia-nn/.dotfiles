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
| `xonsh` | xonsh を専用の venv に入れ、`~/.local/bin/xonsh` にリンクする |
| `npm` | npm のグローバルインストール先を `~/.npm` にする（sudo なしで `npm install -g` できる） |
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

`shell/xonsh/rc.d/` を `~/.config/xonsh/rc.d` にリンクする。xonsh はここにある `*.py` を名前の順に読む（xonsh の標準の仕組み）。

- `~/.xonshrc` は使っていないので、その PC だけの設定を書く場所にできる。
- rc.d は `xonsh -c` やスクリプトの実行でも読まれるので、xontrib・abbrevs などの対話用の設定は対話シェルでだけ読む。
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
| xonsh の設定 | [`shell/xonsh/rc.d/`](shell/xonsh/rc.d/)（`.py` で書く） |
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
│   └── xonsh/          # rc.d/ と、そこから使う lib/
└── tests/              # pytest のテストと Docker のファイル
```

## テスト

Docker（Docker Desktop など）で、Debian・Fedora・Python 3.9 のコンテナを使う。テストはネットワークを使わない。

```sh
docker compose run --rm debian    # shellcheck, ruff, mypy, pytest
docker compose run --rm fedora
docker compose run --rm py39      # 対応する最も古い Python で pytest
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
