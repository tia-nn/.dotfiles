# xonsh の設定（shell/xonsh）をテストするイメージ。xonsh は最新の Python で動かすので、それに合わせる。
FROM python:3.14-slim-trixie

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/venv/bin:$PATH

# git: abbrevs などが使う。テストで install.sh link を実行するので sh（dash）と bash（env.sh を読む）も使う
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-xonsh.txt /tmp/requirements-xonsh.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements-xonsh.txt

RUN useradd --create-home --shell /bin/bash tester
USER tester

WORKDIR /dotfiles
CMD ["sh", "tests/run.sh", "mypy-xonsh", "pytest-xonsh"]
