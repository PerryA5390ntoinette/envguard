"""Tests for envguard.rotator."""
import pytest
from envguard.rotator import (
    RotationEntry,
    RotationReport,
    check_rotation,
    _is_rotation_candidate,
)


# ---------------------------------------------------------------------------
# _is_rotation_candidate
# ---------------------------------------------------------------------------

def test_no_candidate_for_plain_key():
    assert _is_rotation_candidate("APP_NAME", "myapp") is None


def test_candidate_for_empty_secret():
    reason = _is_rotation_candidate("DB_PASSWORD", "")
    assert reason is not None
    assert "empty" in reason


def test_candidate_for_placeholder_value():
    reason = _is_rotation_candidate("API_KEY", "changeme")
    assert reason is not None
    assert "placeholder" in reason


def test_candidate_for_short_secret():
    reason = _is_rotation_candidate("SECRET_KEY", "abc")
    assert reason is not None
    assert "short" in reason


def test_no_candidate_for_strong_secret():
    reason = _is_rotation_candidate("AUTH_TOKEN", "s3cur3-l0ng-v@lue-xyz!")
    assert reason is None


def test_case_insensitive_keyword_match():
    reason = _is_rotation_candidate("db_Password", "")
    assert reason is not None


# ---------------------------------------------------------------------------
# check_rotation
# ---------------------------------------------------------------------------

def test_empty_env_returns_empty_report():
    report = check_rotation({})
    assert isinstance(report, RotationReport)
    assert report.flagged_count == 0
    assert not report.has_candidates


def test_plain_keys_not_flagged():
    env = {"APP_ENV": "production", "LOG_LEVEL": "info"}
    report = check_rotation(env)
    assert report.flagged_count == 0


def test_placeholder_password_flagged():
    env = {"DB_PASSWORD": "placeholder"}
    report = check_rotation(env)
    assert report.flagged_count == 1
    assert report.flagged_keys == ["DB_PASSWORD"]


def test_multiple_candidates_all_flagged():
    env = {
        "APP_NAME": "envguard",
        "API_KEY": "todo",
        "AUTH_TOKEN": "",
        "DB_HOST": "localhost",
    }
    report = check_rotation(env)
    assert report.flagged_count == 2
    assert set(report.flagged_keys) == {"API_KEY", "AUTH_TOKEN"}


def test_entry_has_suggested_action():
    env = {"SECRET_KEY": "fixme"}
    report = check_rotation(env)
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert isinstance(entry, RotationEntry)
    assert entry.suggested_action != ""


def test_flagged_keys_list_order_matches_insertion():
    env = {"TOKEN_A": "", "TOKEN_B": "test", "TOKEN_C": "todo"}
    report = check_rotation(env)
    assert report.flagged_keys == ["TOKEN_A", "TOKEN_B", "TOKEN_C"]
