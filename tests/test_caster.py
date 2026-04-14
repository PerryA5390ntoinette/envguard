"""Tests for envguard.caster."""
import pytest
from envguard.caster import cast_env, CastReport, CastEntry


def run_cast(env, type_map=None):
    return cast_env(env, type_map or {})


# --- int casting ---

def test_int_valid_value():
    report = run_cast({"PORT": "8080"}, {"PORT": "int"})
    entry = report.entries[0]
    assert entry.success is True
    assert entry.cast_value == 8080


def test_int_invalid_value_produces_failure():
    report = run_cast({"PORT": "abc"}, {"PORT": "int"})
    entry = report.entries[0]
    assert entry.success is False
    assert entry.cast_value is None
    assert entry.error is not None


# --- float casting ---

def test_float_valid_value():
    report = run_cast({"RATIO": "3.14"}, {"RATIO": "float"})
    assert report.entries[0].cast_value == pytest.approx(3.14)


def test_float_invalid_produces_failure():
    report = run_cast({"RATIO": "not_a_float"}, {"RATIO": "float"})
    assert report.entries[0].success is False


# --- bool casting ---

@pytest.mark.parametrize("raw", ["true", "True", "1", "yes", "on"])
def test_bool_truthy_values(raw):
    report = run_cast({"FLAG": raw}, {"FLAG": "bool"})
    assert report.entries[0].cast_value is True


@pytest.mark.parametrize("raw", ["false", "False", "0", "no", "off"])
def test_bool_falsy_values(raw):
    report = run_cast({"FLAG": raw}, {"FLAG": "bool"})
    assert report.entries[0].cast_value is False


def test_bool_invalid_produces_failure():
    report = run_cast({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert report.entries[0].success is False


# --- str (default) casting ---

def test_str_type_always_succeeds():
    report = run_cast({"NAME": "hello"}, {"NAME": "str"})
    assert report.entries[0].success is True
    assert report.entries[0].cast_value == "hello"


def test_unknown_key_defaults_to_str():
    report = run_cast({"FOO": "bar"}, {})
    assert report.entries[0].cast_type == "str"
    assert report.entries[0].success is True


# --- unknown type ---

def test_unknown_type_produces_failure():
    report = run_cast({"X": "1"}, {"X": "uuid"})
    assert report.entries[0].success is False


# --- report aggregates ---

def test_success_count():
    report = run_cast({"A": "1", "B": "x"}, {"A": "int", "B": "int"})
    assert report.success_count() == 1
    assert report.failure_count() == 1


def test_has_failures_false_when_all_pass():
    report = run_cast({"A": "hello"}, {})
    assert report.has_failures() is False


def test_has_failures_true_when_any_fail():
    report = run_cast({"A": "bad"}, {"A": "int"})
    assert report.has_failures() is True


def test_cast_env_dict_contains_only_successes():
    report = run_cast({"PORT": "9000", "NAME": "bad"}, {"PORT": "int", "NAME": "int"})
    result = report.cast_env()
    assert "PORT" in result
    assert "NAME" not in result


def test_empty_env_returns_empty_report():
    report = run_cast({}, {})
    assert report.entries == []
    assert report.success_count() == 0
