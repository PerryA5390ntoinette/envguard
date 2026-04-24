"""Tests for envguard.rotation_reporter."""
import pytest
from envguard.rotator import RotationEntry, RotationReport, check_rotation
from envguard.rotation_reporter import format_rotation_report


def make_report(*pairs) -> RotationReport:
    """Build a RotationReport from (key, value) pairs."""
    return check_rotation(dict(pairs))


def make_manual_report(*entries: RotationEntry) -> RotationReport:
    r = RotationReport()
    for e in entries:
        r.add(e)
    return r


# ---------------------------------------------------------------------------
# No-candidate output
# ---------------------------------------------------------------------------

def test_no_candidates_message_shown():
    report = make_report(("APP_NAME", "envguard"))
    output = format_rotation_report(report, use_color=False)
    assert "No rotation candidates detected" in output


def test_header_present():
    report = make_report()
    output = format_rotation_report(report, use_color=False)
    assert "Rotation Candidates" in output


# ---------------------------------------------------------------------------
# Candidate output
# ---------------------------------------------------------------------------

def test_flagged_key_present_in_output():
    report = make_report(("DB_PASSWORD", "changeme"))
    output = format_rotation_report(report, use_color=False)
    assert "DB_PASSWORD" in output


def test_reason_present_in_output():
    report = make_report(("API_KEY", "todo"))
    output = format_rotation_report(report, use_color=False)
    assert "placeholder" in output


def test_action_present_in_output():
    report = make_report(("AUTH_TOKEN", ""))
    output = format_rotation_report(report, use_color=False)
    assert "Replace" in output


def test_summary_count_present():
    report = make_report(("SECRET", "abc"), ("TOKEN", "test"))
    output = format_rotation_report(report, use_color=False)
    assert "2 variable(s) flagged" in output


def test_no_color_strips_ansi():
    report = make_report(("DB_PASSWORD", "fixme"))
    output = format_rotation_report(report, use_color=False)
    assert "\033[" not in output


def test_color_includes_ansi():
    report = make_report(("DB_PASSWORD", "fixme"))
    output = format_rotation_report(report, use_color=True)
    assert "\033[" in output
