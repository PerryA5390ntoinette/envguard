"""Tests for envguard.encrypto_reporter."""
from envguard.encrypto import check_encryption, EncryptionReport, EncryptionEntry
from envguard.encrypto_reporter import format_encryption_report


def make_report(*pairs) -> EncryptionReport:
    env = dict(pairs)
    return check_encryption(env)


def test_header_present():
    report = make_report(("APP", "val"))
    out = format_encryption_report(report, use_color=False)
    assert "Encryption Check Report" in out


def test_empty_env_message():
    report = EncryptionReport()
    out = format_encryption_report(report, use_color=False)
    assert "No variables found" in out


def test_encrypted_label_shown():
    report = make_report(("DB_PASSWORD", "enc:topsecret"))
    out = format_encryption_report(report, use_color=False)
    assert "ENCRYPTED" in out


def test_plaintext_label_shown_for_sensitive():
    report = make_report(("DB_PASSWORD", "hunter2"))
    out = format_encryption_report(report, use_color=False)
    assert "PLAINTEXT!" in out


def test_plain_label_shown_for_non_sensitive():
    report = make_report(("APP_NAME", "myapp"))
    out = format_encryption_report(report, use_color=False)
    assert "plaintext" in out.lower()


def test_summary_counts_present():
    report = make_report(("DB_PASSWORD", "hunter2"), ("APP", "myapp"))
    out = format_encryption_report(report, use_color=False)
    assert "Total: 2" in out


def test_warning_shown_for_plaintext_sensitive():
    report = make_report(("API_KEY", "raw-key-value"))
    out = format_encryption_report(report, use_color=False)
    assert "WARNING" in out


def test_no_warning_when_all_encrypted():
    report = make_report(("API_KEY", "enc:safeval"))
    out = format_encryption_report(report, use_color=False)
    assert "WARNING" not in out


def test_sensitive_flag_shown():
    report = make_report(("DB_PASSWORD", "enc:x"))
    out = format_encryption_report(report, use_color=False)
    assert "[sensitive]" in out


def test_non_sensitive_no_sensitive_flag():
    report = make_report(("APP_ENV", "production"))
    out = format_encryption_report(report, use_color=False)
    assert "[sensitive]" not in out
