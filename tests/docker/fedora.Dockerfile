# Fedora 上でテストを実行するイメージ。/bin/sh は bash。
FROM fedora:42

# 日本語のコメントやメッセージを扱えるようにする
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    RUFF_CACHE_DIR=/tmp/ruff-cache \
    PATH=/opt/venv/bin:$PATH

RUN dnf install -y --setopt=install_weak_deps=False \
        python3 ShellCheck zsh diffutils findutils shadow-utils \
    && dnf clean all

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# 一般ユーザーで実行する（/etc/skel の既定の .bash_profile / .bashrc を持つ）
RUN useradd --create-home --shell /bin/bash tester
USER tester

WORKDIR /dotfiles
CMD ["sh", "tests/run.sh"]
