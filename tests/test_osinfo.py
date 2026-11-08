from __future__ import annotations

from pathlib import Path

import pytest

from installer.osinfo import detect_distro, detect_os


@pytest.mark.parametrize(
    ("system", "expected"),
    [("Linux", "linux"), ("Darwin", "mac"), ("Windows", "windows"), ("FreeBSD", "unknown")],
)
def test_detect_os(system: str, expected: str) -> None:
    assert detect_os(system) == expected


def test_detect_os_without_argument_returns_a_known_os() -> None:
    assert detect_os() in ("linux", "mac")


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("ID=debian\n", "debian"),
        ("ID=ubuntu\nID_LIKE=debian\n", "debian"),
        ('ID=linuxmint\nID_LIKE="ubuntu debian"\n', "debian"),
        ("ID=fedora\n", "fedora"),
        ('ID="rocky"\nID_LIKE="rhel centos fedora"\n', "fedora"),
        ("ID=arch\n", "unknown"),
    ],
)
def test_detect_distro(tmp_path: Path, content: str, expected: str) -> None:
    os_release = tmp_path / "os-release"
    os_release.write_text(content)
    assert detect_distro(os_release) == expected


def test_detect_distro_without_os_release(tmp_path: Path) -> None:
    assert detect_distro(tmp_path / "missing") == "unknown"
