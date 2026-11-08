# 対応する最も古い Python（mac の Command Line Tools の python3 と同じ 3.9）でテストするイメージ。
FROM python:3.9-slim

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    RUFF_CACHE_DIR=/tmp/ruff-cache \
    PATH=/opt/venv/bin:$PATH

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd --create-home --shell /bin/bash tester
USER tester

WORKDIR /dotfiles
# mypy もここで回す（対応する一番古い Python で型を確認する）
CMD ["sh", "tests/run.sh", "mypy", "pytest"]
