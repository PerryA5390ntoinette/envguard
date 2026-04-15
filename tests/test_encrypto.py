"""Tests for envguard.encrypto."""
import pytest
from envguard.encrypto import (
    _is_sensitive,
    _looks_encrypted,
    check_encryption,
    EncryptionReport,
    EncryptionEntry,
)


# --- _is_sensitive ---

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True

def test_is_sensitive_token():
    assert _is_sensitive("GITHUB_TOKEN") is True

def test_is_sensitive_api_key():
    assert _is_sensitive("API_KEY") is True

def test_is_sensitive_plain_name():
    assert _is_sensitive("APP_NAME") is False

def test_is_sensitive_case_insensitive():
    assert _is_sensitive("db_secret") is True


# --- _looks_encrypted ---

def test_empty_value_not_encrypted():
    ok, reason = _looks_encrypted("")
    assert ok is False

def test_enc_prefix_detected():
    ok, reason = _looks_encrypted("enc:abc123")
    assert ok is True
    assert "prefix" in reason

def test_vault_prefix_detected():
    ok, reason = _looks_encrypted("vault:secret/data")
    assert ok is True

def test_hex_value_detected():
    ok, reason = _looks_encrypted("a" * 32)
    assert ok is True
    assert "hex" in reason

def test_base64_value_detected():
    # 24-char base64-like string
    ok, reason = _looks_encrypted("dGhpcyBpcyBhIHRlc3Q=")
    assert ok is True

def test_short_value_not_encrypted():
    ok, reason = _looks_encrypted("hello")
    assert ok is False
    assert reason == "plaintext"


# --- check_encryption ---

def test_returns_report_instance():
    report = check_encryption({"APP_NAME": "myapp"})
    assert isinstance(report, EncryptionReport)

def test_total_matches_input():
    env = {"A": "1", "B": "2", "C": "3"}
    report = check_encryption(env)
    assert report.total() == 3

def test_sensitive_plaintext_flagged():
    report = check_encryption({"DB_PASSWORD": "hunter2"})
    assert report.plaintext_sensitive_count() == 1
    assert report.encrypted_count() == 0

def test_encrypted_value_not_counted_as_plaintext_sensitive():
    report = check_encryption({"DB_PASSWORD": "enc:supersecret"})
    assert report.plaintext_sensitive_count() == 0
    assert report.encrypted_count() == 1

def test_non_sensitive_plaintext_not_flagged():
    report = check_encryption({"APP_NAME": "myapp"})
    assert report.plaintext_sensitive_count() == 0

def test_entry_fields_populated():
    report = check_encryption({"SECRET_KEY": "enc:abc"})
    entry = report.entries[0]
    assert entry.key == "SECRET_KEY"
    assert entry.is_sensitive is True
    assert entry.looks_encrypted is True
