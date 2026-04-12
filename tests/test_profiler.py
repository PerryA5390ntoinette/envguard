"""Tests for envguard.profiler."""

import pytest
from envguard.profiler import (
    profile_env,
    ProfileReport,
    VariableProfile,
    _profile_variable,
    _categorize,
)


def test_empty_env_returns_zero_totals():
    report = profile_env({})
    assert report.total == 0
    assert report.empty_count == 0
    assert report.secret_like_count == 0
    assert report.url_like_count == 0


def test_total_count_matches_input_size():
    env = {"FOO": "bar", "BAZ": "qux", "X": "y"}
    report = profile_env(env)
    assert report.total == 3


def test_empty_value_increments_empty_count():
    report = profile_env({"EMPTY_VAR": ""})
    assert report.empty_count == 1


def test_non_empty_value_does_not_increment_empty_count():
    report = profile_env({"FOO": "bar"})
    assert report.empty_count == 0


def test_secret_keyword_in_name_detected():
    report = profile_env({"DB_PASSWORD": "s3cr3t", "API_KEY": "abc"})
    assert report.secret_like_count == 2


def test_non_secret_name_not_counted():
    report = profile_env({"APP_NAME": "myapp"})
    assert report.secret_like_count == 0


def test_url_value_detected():
    report = profile_env({"DATABASE_URL": "postgres://localhost/db"})
    assert report.url_like_count == 1


def test_non_url_value_not_counted():
    report = profile_env({"HOST": "localhost"})
    assert report.url_like_count == 0


def test_profiles_list_length_matches_total():
    env = {"A": "1", "B": "2"}
    report = profile_env(env)
    assert len(report.profiles) == report.total


def test_profile_variable_name_preserved():
    vp = _profile_variable("MY_VAR", "hello")
    assert vp.name == "MY_VAR"


def test_profile_value_length():
    vp = _profile_variable("X", "hello")
    assert vp.value_length == 5


def test_profile_special_chars_detected():
    vp = _profile_variable("X", "p@ssw0rd!")
    assert vp.has_special_chars is True


def test_profile_no_special_chars():
    vp = _profile_variable("X", "simplevalue")
    assert vp.has_special_chars is False


def test_category_counts_populated():
    env = {
        "DATABASE_URL": "postgres://localhost/db",
        "APP_SECRET": "abc123",
        "APP_NAME": "myapp",
        "EMPTY": "",
    }
    report = profile_env(env)
    assert "url" in report.category_counts
    assert "secret" in report.category_counts
    assert "general" in report.category_counts
    assert "empty" in report.category_counts


def test_categorize_url_takes_precedence():
    vp = _profile_variable("DB_SECRET_URL", "https://example.com")
    assert _categorize(vp) == "url"


def test_categorize_secret():
    vp = _profile_variable("API_TOKEN", "xyz")
    assert _categorize(vp) == "secret"


def test_categorize_empty():
    vp = _profile_variable("PLAIN", "")
    assert _categorize(vp) == "empty"


def test_categorize_general():
    vp = _profile_variable("APP_ENV", "production")
    assert _categorize(vp) == "general"
