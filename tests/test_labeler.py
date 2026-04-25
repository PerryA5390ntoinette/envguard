"""Tests for envguard.labeler."""
import pytest
from envguard.labeler import (
    LabelEntry,
    LabelReport,
    label_env,
    DEFAULT_RULES,
)


def run_label(env, rules=None):
    return label_env(env, rules=rules)


# ---------------------------------------------------------------------------
# LabelEntry
# ---------------------------------------------------------------------------

def test_label_entry_has_labels_true_when_labels_present():
    entry = LabelEntry(key="DB_PASSWORD", value="s3cr3t", labels=["secret"])
    assert entry.has_labels is True


def test_label_entry_has_labels_false_when_empty():
    entry = LabelEntry(key="APP_NAME", value="myapp", labels=[])
    assert entry.has_labels is False


# ---------------------------------------------------------------------------
# LabelReport counts
# ---------------------------------------------------------------------------

def test_labeled_count_correct():
    report = run_label({"DB_PASSWORD": "x", "APP_NAME": "myapp"})
    assert report.labeled_count >= 1


def test_unlabeled_count_correct():
    report = run_label({"APP_NAME": "myapp"})
    assert report.unlabeled_count == 1


def test_empty_env_produces_empty_report():
    report = run_label({})
    assert report.entries == []
    assert report.labeled_count == 0
    assert report.unlabeled_count == 0


# ---------------------------------------------------------------------------
# Default rule matching
# ---------------------------------------------------------------------------

def test_password_key_gets_secret_label():
    report = run_label({"DB_PASSWORD": "hunter2"})
    entry = report.entries[0]
    assert "secret" in entry.labels


def test_token_key_gets_secret_label():
    report = run_label({"AUTH_TOKEN": "abc123"})
    entry = report.entries[0]
    assert "secret" in entry.labels


def test_host_key_gets_network_label():
    report = run_label({"DB_HOST": "localhost"})
    entry = report.entries[0]
    assert "network" in entry.labels


def test_port_key_gets_network_label():
    report = run_label({"APP_PORT": "8080"})
    entry = report.entries[0]
    assert "network" in entry.labels


def test_database_key_gets_database_label():
    report = run_label({"DATABASE_URL": "postgres://..."})
    entry = report.entries[0]
    assert "database" in entry.labels


def test_feature_flag_key_gets_feature_flag_label():
    report = run_label({"ENABLE_DARK_MODE": "true"})
    entry = report.entries[0]
    assert "feature_flag" in entry.labels


def test_plain_key_gets_no_labels():
    report = run_label({"APP_NAME": "envguard"})
    entry = report.entries[0]
    assert entry.labels == []


# ---------------------------------------------------------------------------
# all_labels and entries_for_label
# ---------------------------------------------------------------------------

def test_all_labels_returns_unique_labels():
    report = run_label({
        "DB_PASSWORD": "s",
        "AUTH_TOKEN": "t",
        "APP_NAME": "n",
    })
    labels = report.all_labels
    assert labels.count("secret") == 1


def test_entries_for_label_filters_correctly():
    report = run_label({"DB_PASSWORD": "s", "APP_HOST": "localhost", "APP_NAME": "n"})
    secrets = report.entries_for_label("secret")
    assert all("secret" in e.labels for e in secrets)


# ---------------------------------------------------------------------------
# Custom rules
# ---------------------------------------------------------------------------

def test_custom_rules_override_defaults():
    custom = {"internal": [r"INTERNAL"]}
    report = run_label({"INTERNAL_FLAG": "1", "DB_PASSWORD": "x"}, rules=custom)
    labeled = {e.key: e.labels for e in report.entries}
    assert "internal" in labeled["INTERNAL_FLAG"]
    # default secret rule should NOT apply when custom rules provided
    assert "secret" not in labeled.get("DB_PASSWORD", [])


def test_all_entries_present_in_report():
    env = {"A": "1", "B": "2", "C": "3"}
    report = run_label(env)
    assert len(report.entries) == 3
