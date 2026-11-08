"""OS 判定。OS ごとの分岐はこのモジュールの関数だけを使う。"""

from __future__ import annotations

import platform
import shlex
from pathlib import Path


def detect_os(system: str | None = None) -> str:
    """linux / mac / windows / unknown のいずれかを返す"""
    if system is None:
        system = platform.system()
    return {"Linux": "linux", "Darwin": "mac", "Windows": "windows"}.get(system, "unknown")


def detect_distro(os_release: Path = Path("/etc/os-release")) -> str:
    """debian / fedora / unknown のいずれかを返す（Linux 用）"""
    try:
        text = os_release.read_text(encoding="utf-8")
    except OSError:
        return "unknown"

    values: dict[str, str] = {}
    for line in text.splitlines():
        key, sep, value = line.partition("=")
        if sep:
            values[key.strip()] = " ".join(shlex.split(value))

    ids = [values.get("ID", ""), *values.get("ID_LIKE", "").split()]
    for distro_id in ids:
        if distro_id in ("debian", "ubuntu"):
            return "debian"
        if distro_id in ("fedora", "rhel"):
            return "fedora"
    return "unknown"
