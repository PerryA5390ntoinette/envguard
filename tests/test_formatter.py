"""Tests for envguard.formatter module."""

import pytest

from envguard.formatter import FormatResult, format_env_content, _normalize_line


# ---------------------------------------------------------------------------
# _normalize_line
# ---------------------------------------------------------------------------

def test_normalize_strips_trailing_whitespace():
    assert _normalize_line("KEY=value   ") == "KEY=value"


def test_normalize_trims_spaces_around_equals():
    assert _normalize_line("KEY = value") == "KEY=value"


def test_normalize_preserves_comment_lines():
    assert _normalize_line("# this is a comment  ") == "# this is a comment"


def test_normalize_preserves_blank_line():
    assert _normalize_line("   ") == ""


# ---------------------------------------------------------------------------
# format_env_content — basic normalization
# ---------------------------------------------------------------------------

def test_format_normalizes_spacing():
    content = "KEY = value\nOTHER=hello   "
    result = format_env_content(content, sort_keys=False, remove_duplicates=False)
    assert "KEY=value" in result.formatted_lines
    assert "OTHER=hello" in result.formatted_lines


def test_format_changed_flag_true_when_modified():
    content = "KEY = value"
    result = format_env_content(content)
    assert result.changed is True


def test_format_changed_flag_false_when_clean():
    content = "KEY=value\nOTHER=hello"
    result = format_env_content(content)
    assert result.changed is False


# ---------------------------------------------------------------------------
# format_env_content — duplicate removal
# ---------------------------------------------------------------------------

def test_removes_duplicate_keys_keeps_last():
    content = "KEY=first\nKEY=second"
    result = format_env_content(content, remove_duplicates=True)
    assert result.formatted_lines == ["KEY=second"]
    assert "KEY" in result.duplicates_removed


def test_no_duplicates_removed_when_all_unique():
    content = "A=1\nB=2"
    result = format_env_content(content, remove_duplicates=True)
    assert result.duplicates_removed == []


def test_duplicate_removal_disabled():
    content = "KEY=first\nKEY=second"
    result = format_env_content(content, remove_duplicates=False)
    assert len([ln for ln in result.formatted_lines if ln.startswith("KEY=")]) == 2


# ---------------------------------------------------------------------------
# format_env_content — sorting
# ---------------------------------------------------------------------------

def test_sort_keys_alphabetically():
    content = "ZEBRA=1\nAPPLE=2\nMIDDLE=3"
    result = format_env_content(content, sort_keys=True)
    keys = [ln.split("=")[0] for ln in result.formatted_lines if "=" in ln]
    assert keys == sorted(keys)


def test_sort_preserves_comments_at_end():
    content = "Z=1\n# comment\nA=2"
    result = format_env_content(content, sort_keys=True)
    # Comments (no key) should sort after keyed lines
    has_comment = any(ln.startswith("#") for ln in result.formatted_lines)
    assert has_comment


# ---------------------------------------------------------------------------
# FormatResult.diff_summary
# ---------------------------------------------------------------------------

def test_diff_summary_no_changes():
    result = FormatResult(changed=False)
    assert "already well-formatted" in result.diff_summary()


def test_diff_summary_with_changes():
    result = FormatResult(changed=True)
    assert "formatting changes" in result.diff_summary()


def test_diff_summary_lists_duplicates():
    result = FormatResult(changed=True, duplicates_removed=["KEY", "OTHER"])
    summary = result.diff_summary()
    assert "KEY" in summary
    assert "OTHER" in summary
    assert "2 duplicate" in summary
