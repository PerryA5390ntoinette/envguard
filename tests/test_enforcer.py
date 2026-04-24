"""Tests for envguard.enforcer."""
import pytest
from envguard.enforcer import enforce_naming, EnforcementReport, EnforcementEntry


def run_enforce(env, convention="upper_snake"):
    return enforce_naming(env, convention=convention)


# ---------------------------------------------------------------------------
# upper_snake (default)
# ---------------------------------------------------------------------------

def test_valid_upper_snake_passes():
    report = run_enforce({"DATABASE_URL": "postgres://localhost"})
    assert report.ok_count() == 1
    assert report.violation_count() == 0


def test_lowercase_key_violates_upper_snake():
    report = run_enforce({"database_url": "postgres://localhost"})
    assert report.violation_count() == 1
    assert not report.has_violations() is False


def test_mixed_case_key_violates_upper_snake():
    report = run_enforce({"Database_URL": "val"})
    assert report.violation_count() == 1


def test_multiple_keys_mixed_results():
    env = {"GOOD_KEY": "1", "badKey": "2", "ALSO_GOOD": "3"}
    report = run_enforce(env)
    assert report.ok_count() == 2
    assert report.violation_count() == 1


def test_violation_reason_populated():
    report = run_enforce({"bad": "val"})
    entry = report.violations()[0]
    assert entry.reason is not None
    assert "bad" in entry.reason


def test_empty_env_returns_empty_report():
    report = run_enforce({})
    assert len(report.entries) == 0
    assert not report.has_violations()


# ---------------------------------------------------------------------------
# lower_snake
# ---------------------------------------------------------------------------

def test_valid_lower_snake_passes():
    report = run_enforce({"app_host": "localhost"}, convention="lower_snake")
    assert report.ok_count() == 1
    assert report.violation_count() == 0


def test_upper_key_violates_lower_snake():
    report = run_enforce({"APP_HOST": "localhost"}, convention="lower_snake")
    assert report.violation_count() == 1


# ---------------------------------------------------------------------------
# screaming_snake
# ---------------------------------------------------------------------------

def test_screaming_snake_allows_leading_digit():
    report = run_enforce({"2FA_SECRET": "val"}, convention="screaming_snake")
    assert report.ok_count() == 1


def test_screaming_snake_rejects_lowercase():
    report = run_enforce({"secret_key": "val"}, convention="screaming_snake")
    assert report.violation_count() == 1


# ---------------------------------------------------------------------------
# report properties
# ---------------------------------------------------------------------------

def test_report_stores_convention_name():
    report = run_enforce({}, convention="lower_snake")
    assert report.convention == "lower_snake"


def test_violations_helper_returns_only_failed_entries():
    env = {"OK_KEY": "1", "bad": "2"}
    report = run_enforce(env)
    violations = report.violations()
    assert all(not e.passed for e in violations)


def test_entry_key_and_value_preserved():
    report = run_enforce({"MY_VAR": "hello"})
    entry = report.entries[0]
    assert entry.key == "MY_VAR"
    assert entry.value == "hello"


# ---------------------------------------------------------------------------
# unknown convention raises
# ---------------------------------------------------------------------------

def test_unknown_convention_raises_value_error():
    with pytest.raises(ValueError, match="Unknown convention"):
        run_enforce({"KEY": "val"}, convention="camelCase")
