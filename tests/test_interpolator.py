"""Tests for envguard.interpolator."""
import pytest
from envguard.interpolator import interpolate, InterpolationReport


def test_simple_value_passes_through():
    report = interpolate({"HOST": "localhost"})
    assert report.resolved["HOST"] == "localhost"


def test_braced_reference_resolved():
    env = {"BASE": "http://example.com", "URL": "${BASE}/api"}
    report = interpolate(env)
    assert report.resolved["URL"] == "http://example.com/api"


def test_bare_dollar_reference_resolved():
    env = {"PORT": "8080", "ADDR": "localhost:$PORT"}
    report = interpolate(env)
    assert report.resolved["ADDR"] == "localhost:8080"


def test_chained_references_resolved():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    report = interpolate(env)
    assert report.resolved["C"] == "hello_world!"


def test_undefined_reference_produces_warning():
    env = {"URL": "${MISSING}/path"}
    report = interpolate(env)
    assert report.has_warnings
    assert report.warnings[0].reference == "MISSING"
    assert "URL" in report.warnings[0].message


def test_undefined_reference_keeps_original_token():
    env = {"URL": "${MISSING}/path"}
    report = interpolate(env)
    assert report.resolved["URL"] == "${MISSING}/path"


def test_no_warnings_for_clean_env():
    env = {"A": "1", "B": "${A}2"}
    report = interpolate(env)
    assert not report.has_warnings


def test_circular_reference_produces_warning():
    env = {"A": "${B}", "B": "${A}"}
    report = interpolate(env)
    assert report.has_warnings
    messages = [w.message for w in report.warnings]
    assert any("Circular" in m for m in messages)


def test_multiple_references_in_one_value():
    env = {"FIRST": "foo", "SECOND": "bar", "BOTH": "${FIRST}-${SECOND}"}
    report = interpolate(env)
    assert report.resolved["BOTH"] == "foo-bar"


def test_empty_env_returns_empty_resolved():
    report = interpolate({})
    assert report.resolved == {}
    assert not report.has_warnings


def test_value_without_reference_unchanged():
    env = {"KEY": "plain_value_123"}
    report = interpolate(env)
    assert report.resolved["KEY"] == "plain_value_123"


def test_report_resolved_contains_all_keys():
    env = {"X": "1", "Y": "2", "Z": "3"}
    report = interpolate(env)
    assert set(report.resolved.keys()) == {"X", "Y", "Z"}
