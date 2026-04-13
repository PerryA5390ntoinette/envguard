"""Tests for envguard.tagger."""

import pytest
from envguard.tagger import tag_env, _tags_for_name, TagReport, TagEntry


# ---------------------------------------------------------------------------
# _tags_for_name
# ---------------------------------------------------------------------------

def test_password_gets_secret_tag():
    assert "secret" in _tags_for_name("DB_PASSWORD")


def test_token_gets_secret_tag():
    assert "secret" in _tags_for_name("API_TOKEN")


def test_host_gets_network_tag():
    assert "network" in _tags_for_name("APP_HOST")


def test_port_gets_network_tag():
    assert "network" in _tags_for_name("SERVER_PORT")


def test_database_gets_database_tag():
    assert "database" in _tags_for_name("DATABASE_URL")


def test_log_level_gets_logging_tag():
    assert "logging" in _tags_for_name("LOG_LEVEL")


def test_feature_flag_gets_feature_flag_tag():
    assert "feature_flag" in _tags_for_name("ENABLE_DARK_MODE")


def test_plain_name_gets_no_tags():
    assert _tags_for_name("APP_NAME") == set()


def test_name_can_have_multiple_tags():
    # AUTH_TOKEN matches both 'auth' and 'secret'
    tags = _tags_for_name("AUTH_TOKEN")
    assert "auth" in tags
    assert "secret" in tags


# ---------------------------------------------------------------------------
# tag_env
# ---------------------------------------------------------------------------

def test_tag_env_returns_tag_report():
    report = tag_env({"DB_PASSWORD": "secret"})
    assert isinstance(report, TagReport)


def test_tag_env_creates_entry_per_variable():
    env = {"DB_HOST": "localhost", "APP_NAME": "myapp"}
    report = tag_env(env)
    assert len(report.entries) == 2


def test_tag_env_entry_has_correct_name_and_value():
    report = tag_env({"API_KEY": "abc123"})
    entry = report.entries[0]
    assert entry.name == "API_KEY"
    assert entry.value == "abc123"


def test_tag_env_entry_tagged_correctly():
    report = tag_env({"API_KEY": "abc123"})
    assert "secret" in report.entries[0].tags


def test_tag_index_populated():
    report = tag_env({"DB_PASSWORD": "x", "DB_HOST": "localhost"})
    assert "DB_PASSWORD" in report.tag_index.get("secret", [])
    assert "DB_HOST" in report.tag_index.get("network", [])


def test_by_tag_returns_matching_entries():
    report = tag_env({"DB_PASSWORD": "x", "APP_NAME": "myapp"})
    secrets = report.by_tag("secret")
    assert len(secrets) == 1
    assert secrets[0].name == "DB_PASSWORD"


def test_by_tag_returns_empty_for_unknown_tag():
    report = tag_env({"APP_NAME": "myapp"})
    assert report.by_tag("nonexistent") == []


def test_all_tags_aggregates_tags():
    report = tag_env({"DB_HOST": "localhost", "API_TOKEN": "tok"})
    tags = report.all_tags()
    assert "network" in tags
    assert "secret" in tags


def test_empty_env_produces_empty_report():
    report = tag_env({})
    assert report.entries == []
    assert report.tag_index == {}
    assert report.all_tags() == set()
