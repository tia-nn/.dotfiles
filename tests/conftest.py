"""テストの共通処理。HOME を一時ディレクトリに差し替える。"""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from helpers import REPO_ROOT

from installer.context import Context


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    return home


@pytest.fixture
def ctx(tmp_path: Path, home: Path) -> Context:
    """出力を StringIO に集める Context（helpers.output(ctx) で確認できる）"""
    return Context(
        dotfiles=REPO_ROOT,
        home=home,
        os_name="linux",
        backup_dir=tmp_path / "backup",
        out=io.StringIO(),
        err=io.StringIO(),
    )
