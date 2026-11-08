from __future__ import annotations

from pathlib import Path

import pytest
from helpers import errors, output, snapshot

from installer.block import BEGIN, END, UnterminatedBlockError, apply_block, remove_block, render
from installer.context import Context


def lines(*items: str) -> str:
    return "".join(item + "\n" for item in items)


@pytest.fixture
def rc(home: Path) -> Path:
    return home / ".bashrc"


# --- render ---


def test_render_appends_to_empty_text() -> None:
    assert render("", "echo hi") == lines(BEGIN, "echo hi", END)


def test_render_appends_after_existing_content_with_a_blank_line() -> None:
    assert render("distro\n", "echo hi") == lines("distro", "", BEGIN, "echo hi", END)


def test_render_does_not_add_a_second_blank_line() -> None:
    assert render("distro\n\n", "x") == lines("distro", "", BEGIN, "x", END)


def test_render_replaces_the_block_in_place() -> None:
    text = lines("before", BEGIN, "old", END, "after")
    assert render(text, "new1\nnew2") == lines("before", BEGIN, "new1", "new2", END, "after")


def test_render_with_empty_body_removes_the_block() -> None:
    assert render(lines("before", BEGIN, "old", END, "after"), "") == lines("before", "after")


def test_render_with_empty_body_and_no_block_keeps_text_as_is() -> None:
    assert render("no newline at end", "") == "no newline at end"


def test_render_merges_duplicated_blocks_into_the_first() -> None:
    text = lines("a", BEGIN, "x", END, "b", BEGIN, "y", END, "c")
    assert render(text, "z") == lines("a", BEGIN, "z", END, "b", "c")


def test_render_rejects_an_unterminated_block() -> None:
    with pytest.raises(UnterminatedBlockError):
        render(lines("before", BEGIN, "keep-me"), "x")


# --- apply_block / remove_block ---


def test_apply_block_creates_a_missing_file(ctx: Context, rc: Path) -> None:
    assert apply_block(rc, "echo hi", ctx)
    assert rc.read_text() == lines(BEGIN, "echo hi", END)


def test_apply_block_backs_up_the_file_before_changing_it(ctx: Context, rc: Path) -> None:
    rc.write_text("distro\n")
    assert apply_block(rc, "echo hi", ctx)
    assert rc.read_text() == lines("distro", "", BEGIN, "echo hi", END)
    assert (ctx.backup_dir / ".bashrc").read_text() == "distro\n"


def test_apply_block_is_idempotent(ctx: Context, rc: Path) -> None:
    rc.write_text("distro\n")
    assert apply_block(rc, "echo hi", ctx)
    first = rc.read_text()
    backups = snapshot(ctx.backup_dir)

    ctx.out.seek(0)
    ctx.out.truncate()
    assert apply_block(rc, "echo hi", ctx)
    assert output(ctx).endswith(f"ok: {rc}\n")
    assert rc.read_text() == first
    assert snapshot(ctx.backup_dir) == backups


def test_remove_block_on_a_missing_file_does_nothing(ctx: Context, rc: Path) -> None:
    assert remove_block(rc, ctx)
    assert not rc.exists()


def test_apply_block_leaves_an_unterminated_block_untouched(ctx: Context, rc: Path) -> None:
    original = lines("before", BEGIN, "keep-me")
    rc.write_text(original)
    assert not apply_block(rc, "echo hi", ctx)
    assert rc.read_text() == original
    assert "not modified" in errors(ctx)


def test_apply_block_keeps_a_symlinked_rc_as_a_symlink(ctx: Context, rc: Path, tmp_path: Path) -> None:
    real = tmp_path / "real_bashrc"
    real.write_text("x\n")
    rc.symlink_to(real)
    assert apply_block(rc, "echo hi", ctx)
    assert rc.is_symlink()
    assert "echo hi\n" in real.read_text()


def test_apply_block_shows_a_diff_and_changes_nothing_in_dry_run(ctx: Context, rc: Path, home: Path) -> None:
    rc.write_text("distro\n")
    before = snapshot(home)
    ctx.dry_run = True
    assert apply_block(rc, "echo hi", ctx)
    assert f"[dry-run] update block in {rc}" in output(ctx)
    assert "    +echo hi" in output(ctx)
    assert snapshot(home) == before
    assert not ctx.backup_dir.exists()
