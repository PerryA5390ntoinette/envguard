"""Tests for envguard.classification_reporter."""
import pytest
from envguard.classifier import classify_env, ClassificationReport
from envguard.classification_reporter import format_classification_report


def make_report(env: dict) -> ClassificationReport:
    return classify_env(env)


def test_header_present():
    report = make_report({"APP": "value"})
    output = format_classification_report(report, use_color=False)
    assert "Variable Classification" in output


def test_empty_env_shows_no_variables_message():
    report = make_report({})
    output = format_classification_report(report, use_color=False)
    assert "No variables to classify" in output


def test_key_present_in_output():
    report = make_report({"DATABASE_URL": "postgres://localhost/db"})
    output = format_classification_report(report, use_color=False)
    assert "DATABASE_URL" in output


def test_sensitive_label_shown_for_sensitive_key():
    report = make_report({"API_SECRET": "topsecret"})
    output = format_classification_report(report, use_color=False)
    assert "sensitive" in output


def test_sensitive_label_absent_for_plain_key():
    report = make_report({"APP_NAME": "myapp"})
    output = format_classification_report(report, use_color=False)
    assert "sensitive" not in output


def test_type_label_shown():
    report = make_report({"PORT": "8080"})
    output = format_classification_report(report, use_color=False)
    assert "integer" in output


def test_summary_total_shown():
    report = make_report({"A": "1", "B": "2"})
    output = format_classification_report(report, use_color=False)
    assert "Total: 2" in output


def test_summary_sensitive_count_shown():
    report = make_report({"DB_PASSWORD": "x", "HOST": "localhost"})
    output = format_classification_report(report, use_color=False)
    assert "Sensitive: 1" in output


def test_url_type_detected_and_shown():
    report = make_report({"CALLBACK_URL": "https://example.com/cb"})
    output = format_classification_report(report, use_color=False)
    assert "url" in output


def test_boolean_type_shown():
    report = make_report({"ENABLE_FEATURE": "true"})
    output = format_classification_report(report, use_color=False)
    assert "boolean" in output
