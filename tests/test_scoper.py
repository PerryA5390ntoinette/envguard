"""Tests for envguard.scoper."""
import pytest
from envguard.scoper import _detect_scope, scope_env, ScopeReport, ScopeEntry


def test_detect_scope_global_for_plain_key():
    assert _detect_scope("DATABASE_URL") == "global"


def test_detect_scope_dev_prefix():
    assert _detect_scope("DEV_API_KEY") == "dev"


def test_detect_scope_development_normalizes_to_dev():
    assert _detect_scope("DEVELOPMENT_HOST") == "dev"


def test_detect_scope_prod_suffix():
    assert _detect_scope("API_KEY_PROD") == "prod"


def test_detect_scope_production_normalizes_to_prod():
    assert _detect_scope("DB_URL_PRODUCTION") == "prod"


def test_detect_scope_staging_prefix():
    assert _detect_scope("STAGING_SECRET") == "staging"


def test_detect_scope_test_prefix():
    assert _detect_scope("TEST_TOKEN") == "test"


def test_scope_env_returns_report_instance():
    report = scope_env({"FOO": "bar"})
    assert isinstance(report, ScopeReport)


def test_scope_env_empty_env():
    report = scope_env({})
    assert report.total() == 0


def test_scope_env_total_count():
    env = {"FOO": "1", "BAR": "2", "DEV_X": "3"}
    report = scope_env(env)
    assert report.total() == 3


def test_scope_env_global_count():
    env = {"FOO": "1", "BAR": "2", "DEV_X": "3"}
    report = scope_env(env)
    assert report.global_count() == 2


def test_scope_env_dev_entries():
    env = {"DEV_HOST": "localhost", "PROD_HOST": "example.com"}
    report = scope_env(env)
    dev_entries = report.entries_for("dev")
    assert len(dev_entries) == 1
    assert dev_entries[0].key == "DEV_HOST"


def test_scope_env_scopes_list():
    env = {"DEV_A": "1", "STAGING_B": "2", "PLAIN": "3"}
    report = scope_env(env)
    scopes = report.scopes()
    assert "dev" in scopes
    assert "staging" in scopes
    assert "global" in scopes


def test_entries_for_unknown_scope_returns_empty():
    report = scope_env({"FOO": "bar"})
    assert report.entries_for("nonexistent") == []


def test_scope_entry_value_preserved():
    report = scope_env({"DEV_TOKEN": "abc123"})
    entry = report.entries_for("dev")[0]
    assert entry.value == "abc123"
