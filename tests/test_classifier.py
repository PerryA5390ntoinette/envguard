"""Tests for envguard.classifier."""
import pytest
from envguard.classifier import (
    ClassificationEntry,
    ClassificationReport,
    classify_env,
    _detect_sensitivity,
    _detect_type,
)


# --- _detect_sensitivity ---

def test_password_is_sensitive():
    assert _detect_sensitivity("DB_PASSWORD") is True

def test_token_is_sensitive():
    assert _detect_sensitivity("AUTH_TOKEN") is True

def test_api_key_is_sensitive():
    assert _detect_sensitivity("STRIPE_API_KEY") is True

def test_plain_name_not_sensitive():
    assert _detect_sensitivity("APP_NAME") is False

def test_sensitivity_case_insensitive():
    assert _detect_sensitivity("db_secret") is True


# --- _detect_type ---

def test_detect_boolean_true():
    assert _detect_type("true") == "boolean"

def test_detect_boolean_false():
    assert _detect_type("false") == "boolean"

def test_detect_boolean_yes():
    assert _detect_type("yes") == "boolean"

def test_detect_integer():
    assert _detect_type("42") == "integer"

def test_detect_negative_integer():
    assert _detect_type("-7") == "integer"

def test_detect_float():
    assert _detect_type("3.14") == "float"

def test_detect_url_https():
    assert _detect_type("https://example.com") == "url"

def test_detect_url_http():
    assert _detect_type("http://localhost:8080") == "url"

def test_detect_path_absolute():
    assert _detect_type("/var/log/app") == "path"

def test_detect_path_relative():
    assert _detect_type("./config") == "path"

def test_detect_string_fallback():
    assert _detect_type("hello_world") == "string"


# --- classify_env ---

def test_empty_env_returns_empty_report():
    report = classify_env({})
    assert report.total == 0
    assert report.sensitive_count == 0

def test_total_matches_input_size():
    env = {"A": "1", "B": "2", "C": "3"}
    report = classify_env(env)
    assert report.total == 3

def test_sensitive_count_correct():
    env = {"DB_PASSWORD": "secret123", "APP_NAME": "myapp", "API_TOKEN": "tok"}
    report = classify_env(env)
    assert report.sensitive_count == 2

def test_sensitive_keys_listed():
    env = {"DB_PASSWORD": "x", "HOST": "localhost"}
    report = classify_env(env)
    assert "DB_PASSWORD" in report.sensitive_keys()
    assert "HOST" not in report.sensitive_keys()

def test_by_type_groups_correctly():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
    report = classify_env(env)
    by_type = report.by_type()
    assert "PORT" in by_type.get("integer", [])
    assert "DEBUG" in by_type.get("boolean", [])
    assert "NAME" in by_type.get("string", [])

def test_entry_fields_populated():
    env = {"API_KEY": "abc123"}
    report = classify_env(env)
    entry = report.entries[0]
    assert entry.key == "API_KEY"
    assert entry.value == "abc123"
    assert entry.sensitive is True
    assert entry.inferred_type == "string"
