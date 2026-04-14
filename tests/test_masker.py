"""Tests for envguard.masker."""
import pytest
from envguard.masker import (
    MaskEntry,
    MaskReport,
    _is_sensitive,
    _mask_value,
    mask_env,
)


# ---------------------------------------------------------------------------
# _is_sensitive
# ---------------------------------------------------------------------------

def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD") is True

def test_is_sensitive_token():
    assert _is_sensitive("AUTH_TOKEN") is True

def test_is_sensitive_key():
    assert _is_sensitive("API_KEY") is True

def test_is_sensitive_secret():
    assert _is_sensitive("APP_SECRET") is True

def test_is_sensitive_plain_name():
    assert _is_sensitive("APP_NAME") is False

def test_is_sensitive_case_insensitive():
    assert _is_sensitive("db_password") is True


# ---------------------------------------------------------------------------
# _mask_value
# ---------------------------------------------------------------------------

def test_mask_value_full():
    assert _mask_value("supersecret") == "***"

def test_mask_value_empty_string():
    assert _mask_value("") == "***"

def test_mask_value_partial_reveals_suffix():
    result = _mask_value("supersecret", partial=True)
    assert result.endswith("cret")
    assert result.startswith("***")

def test_mask_value_partial_short_value_still_masks():
    # value shorter than PARTIAL_VISIBLE → full mask
    result = _mask_value("ab", partial=True)
    assert result == "***"


# ---------------------------------------------------------------------------
# mask_env
# ---------------------------------------------------------------------------

def run_mask(env, partial=False):
    return mask_env(env, partial=partial)


def test_mask_env_returns_report_instance():
    report = run_mask({})
    assert isinstance(report, MaskReport)

def test_empty_env_zero_counts():
    report = run_mask({})
    assert report.masked_count == 0
    assert report.plain_count == 0

def test_sensitive_variable_is_masked():
    report = run_mask({"DB_PASSWORD": "s3cr3t"})
    assert report.masked_count == 1
    assert report.entries[0].masked == "***"

def test_plain_variable_not_masked():
    report = run_mask({"APP_NAME": "myapp"})
    assert report.plain_count == 1
    assert report.entries[0].masked == "myapp"

def test_mixed_env_correct_counts():
    env = {"APP_NAME": "myapp", "API_KEY": "abc123", "PORT": "8080"}
    report = run_mask(env)
    assert report.masked_count == 1
    assert report.plain_count == 2

def test_masked_env_dict_replaces_sensitive():
    env = {"API_KEY": "secret", "HOST": "localhost"}
    result = run_mask(env).masked_env()
    assert result["API_KEY"] == "***"
    assert result["HOST"] == "localhost"

def test_original_value_preserved_in_entry():
    report = run_mask({"AUTH_TOKEN": "tok_abc"})
    assert report.entries[0].original == "tok_abc"

def test_partial_mask_applied_when_flag_set():
    report = run_mask({"DB_PASSWORD": "supersecret"}, partial=True)
    assert report.entries[0].masked == "***cret"

def test_was_masked_flag_correct():
    report = run_mask({"SECRET_KEY": "xyz", "DEBUG": "true"})
    by_name = {e.name: e for e in report.entries}
    assert by_name["SECRET_KEY"].was_masked is True
    assert by_name["DEBUG"].was_masked is False
