"""Tests for envguard.redactor."""
import pytest
from envguard.redactor import redact_env, _is_sensitive, _REDACTED


# --- _is_sensitive ---

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True


def test_is_sensitive_api_key():
    assert _is_sensitive("STRIPE_API_KEY") is True


def test_is_sensitive_plain_name():
    assert _is_sensitive("APP_PORT") is False


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("db_Secret") is True


# --- redact_env ---

def test_non_sensitive_value_unchanged():
    report = redact_env({"APP_ENV": "production"})
    assert report.redacted["APP_ENV"] == "production"


def test_sensitive_value_redacted():
    report = redact_env({"DB_PASSWORD": "s3cr3t"})
    assert report.redacted["DB_PASSWORD"] == _REDACTED


def test_redacted_keys_list_populated():
    report = redact_env({"API_KEY": "abc", "HOST": "localhost"})
    assert "API_KEY" in report.redacted_keys
    assert "HOST" not in report.redacted_keys


def test_redaction_count():
    env = {"SECRET_KEY": "x", "TOKEN": "y", "PORT": "8080"}
    report = redact_env(env)
    assert report.redaction_count == 2


def test_original_preserved():
    env = {"DB_PASSWORD": "hunter2", "APP_ENV": "dev"}
    report = redact_env(env)
    assert report.original == env


def test_extra_keys_redacted():
    report = redact_env({"MY_VAR": "value"}, extra_keys=["MY_VAR"])
    assert report.redacted["MY_VAR"] == _REDACTED


def test_extra_keys_case_insensitive():
    report = redact_env({"MY_VAR": "value"}, extra_keys=["my_var"])
    assert report.redacted["MY_VAR"] == _REDACTED


def test_empty_env_returns_empty_report():
    report = redact_env({})
    assert report.redacted == {}
    assert report.redaction_count == 0


def test_mixed_env():
    env = {"PORT": "3000", "JWT_SECRET": "topsecret", "HOST": "example.com"}
    report = redact_env(env)
    assert report.redacted["PORT"] == "3000"
    assert report.redacted["HOST"] == "example.com"
    assert report.redacted["JWT_SECRET"] == _REDACTED
