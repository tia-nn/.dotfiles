from __future__ import annotations

import contextlib
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from installer.archive import extract_tar, extract_zip_files

# 新しい Python で、わざと自前の確認（filter なしの extractall）を通したときの警告
pytestmark = pytest.mark.filterwarnings("ignore:Python 3.14 will:DeprecationWarning")


def add_file(tar: tarfile.TarFile, name: str, data: bytes = b"x") -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


@pytest.mark.usefixtures("tar_mode")
def test_extract_tar(tmp_path: Path) -> None:
    archive = tmp_path / "a.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        add_file(tar, "top/bin/tool", b"hello")
    dest = tmp_path / "out"
    dest.mkdir()
    extract_tar(archive, dest)
    assert (dest / "top/bin/tool").read_bytes() == b"hello"


@pytest.fixture(params=["data_filter", "fallback"])
def tar_mode(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    """標準の filter="data" と、それがない古い Python 向けの自前の確認の両方を試す"""
    if request.param == "fallback":
        monkeypatch.delattr(tarfile, "data_filter", raising=False)
    elif not hasattr(tarfile, "data_filter"):
        pytest.skip("tarfile.data_filter is not available")
    return str(request.param)


@pytest.mark.usefixtures("tar_mode")
@pytest.mark.parametrize("name", ["../evil", "top/../../evil"])
def test_extract_tar_rejects_paths_outside(tmp_path: Path, name: str) -> None:
    archive = tmp_path / "a.tar"
    with tarfile.open(archive, "w") as tar:
        add_file(tar, name)
    dest = tmp_path / "out"
    dest.mkdir()
    with pytest.raises((ValueError, tarfile.TarError)):
        extract_tar(archive, dest)
    assert not (tmp_path / "evil").exists()


@pytest.mark.usefixtures("tar_mode")
def test_extract_tar_never_writes_absolute_paths(tmp_path: Path) -> None:
    """filter="data" は先頭の / を取って中に展開し、自前の確認はエラーにする。どちらも外には書かない"""
    outside = tmp_path / "outside" / "evil"
    archive = tmp_path / "a.tar"
    with tarfile.open(archive, "w") as tar:
        add_file(tar, str(outside))
    dest = tmp_path / "out"
    dest.mkdir()
    with contextlib.suppress(ValueError, tarfile.TarError):
        extract_tar(archive, dest)
    assert not outside.exists()


@pytest.mark.usefixtures("tar_mode")
def test_extract_tar_rejects_links_outside(tmp_path: Path) -> None:
    archive = tmp_path / "a.tar"
    with tarfile.open(archive, "w") as tar:
        info = tarfile.TarInfo("top/link")
        info.type = tarfile.SYMTYPE
        info.linkname = "../../outside"
        tar.addfile(info)
    dest = tmp_path / "out"
    dest.mkdir()
    with pytest.raises((ValueError, tarfile.TarError)):
        extract_tar(archive, dest)


@pytest.mark.usefixtures("tar_mode")
def test_extract_tar_rejects_hard_links_outside(tmp_path: Path) -> None:
    """dir/../outside のように、シンボリックリンクとして見ると内側に見えるものも拒む"""
    archive = tmp_path / "a.tar"
    with tarfile.open(archive, "w") as tar:
        info = tarfile.TarInfo("dir/x")
        info.type = tarfile.LNKTYPE
        info.linkname = "../outside"
        tar.addfile(info)
    dest = tmp_path / "out"
    dest.mkdir()
    with pytest.raises((ValueError, tarfile.TarError)):
        extract_tar(archive, dest)


@pytest.mark.usefixtures("tar_mode")
def test_extract_tar_keeps_hard_links_inside(tmp_path: Path) -> None:
    archive = tmp_path / "a.tar"
    with tarfile.open(archive, "w") as tar:
        add_file(tar, "top/file", b"hello")
        info = tarfile.TarInfo("top/sub/link")
        info.type = tarfile.LNKTYPE
        info.linkname = "top/file"
        tar.addfile(info)
    dest = tmp_path / "out"
    dest.mkdir()
    extract_tar(archive, dest)
    assert (dest / "top/sub/link").read_bytes() == b"hello"


def test_extract_zip_files_flattens_and_filters(tmp_path: Path) -> None:
    archive = tmp_path / "a.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("fonts/A.ttf", b"a")
        zf.writestr("B.ttf", b"b")
        zf.writestr("README.md", b"r")
        zf.writestr("../C.ttf", b"c")
    dest = tmp_path / "out"
    dest.mkdir()
    written = extract_zip_files(archive, dest, ".ttf")
    assert sorted(p.name for p in written) == ["A.ttf", "B.ttf", "C.ttf"]
    assert sorted(p.name for p in dest.iterdir()) == ["A.ttf", "B.ttf", "C.ttf"]
    assert not (tmp_path / "C.ttf").exists()
