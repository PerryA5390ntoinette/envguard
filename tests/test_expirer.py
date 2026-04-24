"""Tests for envguard.expirer."""
from datetime import datetime, timezone, timedelta

import pytest

from envguard.expirer import check_expiry, ExpiryReport, ExpiryEntry, _extract_date, _is_past


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def future_date() -> str:
    dt = datetime.now(timezone.utc) + timedelta(days=365)
    return dt.strftime("%Y-%m-%d")


def past_date() -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=365)
    return dt.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# _extract_date
# ---------------------------------------------------------------------------

def test_extract_date_finds_iso_date():
    assert _extract_date("token-2023-01-15-abc") == "2023-01-15"


def test_extract_date_returns_none_when_absent():
    assert _extract_date("mysecretvalue") is None


def test_extract_date_returns_first_match():
    result = _extract_date("2020-01-01 and 2025-06-30")
    assert result == "2020-01-01"


# ---------------------------------------------------------------------------
# _is_past
# ---------------------------------------------------------------------------

def test_is_past_old_date_returns_true():
    assert _is_past("2000-01-01") is True


def test_is_past_future_date_returns_false():
    assert _is_past(future_date()) is False


def test_is_past_invalid_string_returns_false():
    assert _is_past("not-a-date") is False


# ---------------------------------------------------------------------------
# check_expiry
# ---------------------------------------------------------------------------

def test_empty_env_returns_empty_report():
    report = check_expiry({})
    assert isinstance(report, ExpiryReport)
    assert report.entries == []


def test_plain_key_without_date_ignored():
    report = check_expiry({"DATABASE_URL": "postgres://localhost/db"})
    assert report.entries == []


def test_expired_date_in_value_detected():
    report = check_expiry({"API_TOKEN": f"tok-{past_date()}-xyz"})
    assert report.expired_count == 1
    assert report.entries[0].is_expired is True


def test_future_date_in_value_not_expired():
    report = check_expiry({"API_TOKEN": f"tok-{future_date()}-xyz"})
    assert report.expired_count == 0
    assert report.entries[0].is_expired is False


def test_has_expired_true_when_expired_entry_present():
    report = check_expiry({"SECRET": f"val-{past_date()}"})
    assert report.has_expired is True


def test_has_expired_false_when_no_expired_entries():
    report = check_expiry({"SECRET": f"val-{future_date()}"})
    assert report.has_expired is False


def test_temporal_key_without_date_gets_warning_entry():
    report = check_expiry({"TOKEN_EXPIRES": "some-opaque-value"})
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.is_expired is False
    assert entry.detected_date is None
    assert "no date detected" in entry.reason.lower()


def test_ok_count_reflects_non_expired_entries():
    env = {
        "GOOD_TOKEN": f"tok-{future_date()}",
        "BAD_TOKEN": f"tok-{past_date()}",
    }
    report = check_expiry(env)
    assert report.ok_count == 1
    assert report.expired_count == 1


def test_detected_date_stored_on_entry():
    d = past_date()
    report = check_expiry({"MY_KEY": f"value-{d}-suffix"})
    assert report.entries[0].detected_date == d
