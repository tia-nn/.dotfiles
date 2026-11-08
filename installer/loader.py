"""リポジトリ直下の設定ファイル（links.py, packages.py）の読み込み。"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_module(path: Path) -> ModuleType:
    """path の Python ファイルをモジュールとして読み込む"""
    spec = importlib.util.spec_from_file_location(f"dotfiles_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_str_dict(module: ModuleType, name: str) -> dict[str, str]:
    """module の name が文字列から文字列への dict であることを確かめて返す"""
    value = getattr(module, name, None)
    if not isinstance(value, dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    ):
        raise ValueError(f"{module.__file__}: {name} must be a dict of str to str")
    return value


def get_str_list(module: ModuleType, name: str) -> list[str]:
    """module の name が文字列のリストであることを確かめて返す"""
    value = getattr(module, name, None)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValueError(f"{module.__file__}: {name} must be a list of str")
    return value
