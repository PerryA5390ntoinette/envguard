"""Tests for envguard.sanitizer."""
import pytest
from envguard.sanitizer import sanitize_env, SanitizeReport, SanitizeEntry, _sanitize_value


def run_sanitize(env):
    return sanitize_env(env)


def test_clean_value_unchanged():
    env, report = run_sanitize({"KEY": "hello"})
    assert env["KEY"] == "hello"
    assert report.entries[0].changed is False


def test_null_byte_removed():
    env, report = run_sanitize({"KEY": "hel\x00lo"})
    assert env["KEY"] == "hello"
    assert report.entries[0].changed is True


def test_control_character_removed():
    env, report = run_sanitize({"KEY": "val\x1bue"})
    assert env["KEY"] == "value"
    assert report.entries[0].changed is True


def test_newline_and_tab_preserved():
    # \n (0x0a) and \t (0x09) are NOT in the stripped range
    env, report = run_sanitize({"KEY": "line1\nline2"})
    assert env["KEY"] == "line1\nline2"
    assert report.entries[0].changed is False


def test_multiple_keys_all_processed():
    env, report = run_sanitize({"A": "ok", "B": "bad\x00", "C": "fine"})
    assert len(report.entries) == 3


def test_changed_count():
    _, report = run_sanitize({"A": "ok", "B": "bad\x00", "C": "al\x07so bad"})
    assert report.changed_count() == 2


def test_clean_count():
    _, report = run_sanitize({"A": "ok", "B": "bad\x00"})
    assert report.clean_count() == 1


def test_result_env_returns_sanitized_values():
    _, report = run_sanitize({"KEY": "v\x00al"})
    result = report.result_env()
    assert result["KEY"] == "val"


def test_empty_env_returns_empty_report():
    env, report = run_sanitize({})
    assert env == {}
    assert report.entries == []
    assert report.changed_count() == 0


def test_original_value_preserved_in_entry():
    _, report = run_sanitize({"KEY": "v\x00al"})
    assert report.entries[0].original == "v\x00al"


def test_sanitize_value_strips_del_char():
    assert _sanitize_value("ab\x7fcd") == "abcd"


def test_sanitize_value_multiple_control_chars():
    assert _sanitize_value("\x01\x02\x03") == ""
