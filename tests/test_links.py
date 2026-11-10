from __future__ import annotations

import os
from pathlib import Path

import pytest
from helpers import REPO_ROOT, errors, output, snapshot

from installer.context import Context
from installer.links import Entry, Link, expand_home, link_all, load_entries, make_link, resolve


@pytest.fixture
def src(tmp_path: Path) -> Path:
    path = tmp_path / "src"
    path.write_text("new\n")
    return path


# --- expand_home ---


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("~", "/h"),
        ("~/.xonshrc", "/h/.xonshrc"),
        ("/etc/~x", "/etc/~x"),
        ("a~/b", "a~/b"),
        ("~user/x", "~user/x"),
    ],
)
def test_expand_home_expands_a_leading_tilde_only(given: str, expected: str) -> None:
    assert expand_home(given, Path("/h")) == Path(expected)


# --- Entry ---


@pytest.mark.parametrize(
    ("src", "dest", "message"),
    [
        ("", "~/a", "must not be empty"),
        ("a", "", "must not be empty"),
        ("/abs", "~/a", "relative to the repository"),
    ],
)
def test_entry_rejects_invalid_paths(src: str, dest: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        Entry(src, dest)


def test_entry_rejects_an_unknown_os_at_runtime() -> None:
    with pytest.raises(ValueError, match="unknown OS 'bsd'"):
        Entry("a", "~/a", os="bsd")  # type: ignore[arg-type]


# --- resolve ---


def test_resolve_filters_by_os_and_expands_paths() -> None:
    entries = [Entry("a", "~/a"), Entry("b", "~/b", os="linux"), Entry("c", "~/c", os="mac")]
    links = resolve(entries, os_name="linux", dotfiles=Path("/d"), home=Path("/h"))
    assert links == [Link(Path("/d/a"), Path("/h/a")), Link(Path("/d/b"), Path("/h/b"))]


def test_resolve_keeps_spaces_in_paths() -> None:
    entries = [Entry("apps/vscode.json", "~/Library/Application Support/Code/User/settings.json", os="mac")]
    links = resolve(entries, os_name="mac", dotfiles=Path("/d"), home=Path("/h"))
    assert links == [
        Link(Path("/d/apps/vscode.json"), Path("/h/Library/Application Support/Code/User/settings.json"))
    ]


# --- load_entries ---


def test_load_entries_reads_links(tmp_path: Path) -> None:
    path = tmp_path / "links.py"
    path.write_text('from installer.links import Entry\nLINKS = [Entry("a", "~/a", os="mac")]\n')
    assert load_entries(path) == [Entry("a", "~/a", os="mac")]


@pytest.mark.parametrize(
    "content",
    ["X = 1\n", "LINKS = ('a', 'b')\n", "LINKS = [('a', '~/a')]\n"],
)
def test_load_entries_rejects_a_wrong_links_variable(tmp_path: Path, content: str) -> None:
    path = tmp_path / "links.py"
    path.write_text(content)
    with pytest.raises(ValueError, match="LINKS must be a list of Entry"):
        load_entries(path)


def test_repository_links_py_is_valid() -> None:
    entries = load_entries(REPO_ROOT / "links.py")
    assert entries
    for os_name in ("linux", "mac"):
        for link in resolve(entries, os_name=os_name, dotfiles=REPO_ROOT, home=Path("/h")):
            assert link.src.exists(), link.src


# --- make_link ---


def test_make_link_creates_a_link_and_its_parent_directory(ctx: Context, home: Path, src: Path) -> None:
    dest = home / "a" / "b" / "file"
    assert make_link(Link(src, dest), ctx)
    assert os.readlink(dest) == str(src)


def test_make_link_does_nothing_when_the_link_is_already_correct(
    ctx: Context, home: Path, src: Path
) -> None:
    dest = home / "file"
    dest.symlink_to(src)
    assert make_link(Link(src, dest), ctx)
    assert output(ctx) == f"ok: {dest}\n"
    assert not ctx.backup_dir.exists()


def test_make_link_backs_up_an_existing_file(ctx: Context, home: Path, src: Path) -> None:
    dest = home / "file"
    dest.write_text("old\n")
    assert make_link(Link(src, dest), ctx)
    assert os.readlink(dest) == str(src)
    assert (ctx.backup_dir / "file").read_text() == "old\n"


def test_make_link_replaces_a_wrong_or_dangling_symlink(
    ctx: Context, home: Path, src: Path, tmp_path: Path
) -> None:
    dest = home / "file"
    dest.symlink_to(tmp_path / "nowhere")
    assert make_link(Link(src, dest), ctx)
    assert os.readlink(dest) == str(src)
    assert os.readlink(ctx.backup_dir / "file") == str(tmp_path / "nowhere")


def test_make_link_does_not_overwrite_an_earlier_backup(
    ctx: Context, home: Path, src: Path, tmp_path: Path
) -> None:
    dest = home / "file"
    dest.write_text("orig\n")
    other = tmp_path / "other"
    other.write_text("other\n")
    assert make_link(Link(src, dest), ctx)
    assert make_link(Link(other, dest), ctx)
    assert os.readlink(dest) == str(other)
    assert (ctx.backup_dir / "file").read_text() == "orig\n"
    assert os.readlink(ctx.backup_dir / "file.1") == str(src)


def test_make_link_fails_when_the_source_is_missing(ctx: Context, home: Path, tmp_path: Path) -> None:
    dest = home / "file"
    assert not make_link(Link(tmp_path / "missing", dest), ctx)
    assert not dest.exists() and not dest.is_symlink()
    assert "source not found" in errors(ctx)


def test_make_link_changes_nothing_in_dry_run(ctx: Context, home: Path, src: Path) -> None:
    (home / "file").write_text("old\n")
    before = snapshot(home)
    ctx.dry_run = True
    assert make_link(Link(src, home / "file"), ctx)
    assert "[dry-run] mv" in output(ctx)
    assert "[dry-run] ln -s" in output(ctx)
    assert snapshot(home) == before
    assert not ctx.backup_dir.exists()


@pytest.fixture
def repo(ctx: Context, tmp_path: Path) -> Path:
    """リポジトリの代わり。src/file をリンク元にする"""
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "file").write_text("new\n")
    ctx.dotfiles = repo
    return repo


def test_make_link_replaces_a_parent_linked_into_the_repository(ctx: Context, home: Path, repo: Path) -> None:
    """以前ディレクトリごとリンクしていた場所の中に、リポジトリを書き換えずにリンクを作る"""
    (home / "dir").symlink_to(repo / "src")
    assert make_link(Link(repo / "src" / "file", home / "dir" / "file"), ctx)
    assert not (home / "dir").is_symlink()
    assert os.readlink(home / "dir" / "file") == str(repo / "src" / "file")
    assert os.readlink(ctx.backup_dir / "dir") == str(repo / "src")
    assert sorted(p.name for p in (repo / "src").iterdir()) == ["file"]
    assert (repo / "src" / "file").read_text() == "new\n"


def test_make_link_keeps_a_parent_linked_outside_the_repository(
    ctx: Context, home: Path, repo: Path, tmp_path: Path
) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (home / "dir").symlink_to(elsewhere)
    assert make_link(Link(repo / "src" / "file", home / "dir" / "file"), ctx)
    assert os.readlink(home / "dir") == str(elsewhere)
    assert os.readlink(elsewhere / "file") == str(repo / "src" / "file")


def test_make_link_replacing_a_parent_changes_nothing_in_dry_run(
    ctx: Context, home: Path, repo: Path
) -> None:
    (home / "dir").symlink_to(repo / "src")
    before = snapshot(home), snapshot(repo)
    ctx.dry_run = True
    assert make_link(Link(repo / "src" / "file", home / "dir" / "file"), ctx)
    assert f"[dry-run] mv {home}/dir" in output(ctx)
    assert f"[dry-run] ln -s {repo}/src/file {home}/dir/file" in output(ctx)
    assert (snapshot(home), snapshot(repo)) == before


def test_commands_are_shown_quoted(ctx: Context, home: Path, src: Path) -> None:
    dest = home / "a b" / "it's"
    assert make_link(Link(src, dest), ctx)
    assert f"+ ln -s {src} '{home}/a b/it'\"'\"'s'" in output(ctx)


# --- link_all ---


def test_link_all_continues_after_a_failure_and_reports_it(
    ctx: Context, home: Path, tmp_path: Path, src: Path
) -> None:
    ctx.dotfiles = tmp_path
    entries = [Entry("missing", "~/missing"), Entry("src", "~/ok"), Entry("src", "~/mac-only", os="mac")]
    assert not link_all(entries, ctx)
    assert os.readlink(home / "ok") == str(src)
    assert not (home / "mac-only").is_symlink()
    assert "source not found" in errors(ctx)
