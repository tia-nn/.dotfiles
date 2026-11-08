"""GitHub のリリースからのダウンロード（asdf, Haxe）。"""

from __future__ import annotations

import json
import urllib.request
from typing import Any


def latest_release(repo: str) -> dict[str, Any]:
    """repo（"owner/name"）の最新リリースの情報"""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    with urllib.request.urlopen(url, timeout=30) as response:
        data: dict[str, Any] = json.load(response)
    return data


def find_asset(release: dict[str, Any], suffix: str) -> tuple[str, str] | None:
    """名前が suffix で終わるアセットの (ファイル名, URL)。なければ None"""
    for asset in release.get("assets", []):
        if asset["name"].endswith(suffix):
            return asset["name"], asset["browser_download_url"]
    return None
