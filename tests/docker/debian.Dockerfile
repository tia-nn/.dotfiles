# Debian 上でテストを実行するイメージ。/bin/sh は dash。
FROM debian:trixie-slim

# 日本語のコメントやメッセージを扱えるようにする
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    RUFF_CACHE_DIR=/tmp/ruff-cache \
    PATH=/opt/venv/bin:$PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv shellcheck zsh git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# 一般ユーザーで実行する（/etc/skel の既定の .bashrc / .profile を持つ）
RUN useradd --create-home --shell /bin/bash tester
USER tester

WORKDIR /dotfiles
# mypy は Python 3.9 として型を確認するので、py39 のイメージで回す（pytest 9 は 3.10 以降の構文を使う）
CMD ["sh", "tests/run.sh", "shellcheck", "ruff", "pytest"]
