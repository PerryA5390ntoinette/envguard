"""Tests for envguard.sorter."""

import pytest
from envguard.sorter import sort_env, SortReport, _extract_prefix


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_sort(env, mode="alpha"):
    return sort_env(env, mode=mode)


# ---------------------------------------------------------------------------
# _extract_prefix
# ---------------------------------------------------------------------------

def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_underscore():
    assert _extract_prefix("PORT") == "PORT"


def test_extract_prefix_multiple_underscores():
    assert _extract_prefix("AWS_S3_BUCKET") == "AWS"


# ---------------------------------------------------------------------------
# Alpha mode
# ---------------------------------------------------------------------------

def test_alpha_sort_returns_report_instance():
    report = run_sort({"Z": "1", "A": "2"})
    assert isinstance(report, SortReport)


def test_alpha_sort_orders_keys():
    report = run_sort({"Z": "1", "M": "2", "A": "3"})
    assert report.sorted_order == ["A", "M", "Z"]


def test_alpha_sort_is_case_insensitive():
    report = run_sort({"b": "1", "A": "2"})
    assert report.sorted_order[0].lower() == "a"


def test_alpha_sorted_env_contains_all_keys():
    env = {"Z": "z", "A": "a", "M": "m"}
    report = run_sort(env)
    assert set(report.sorted_env.keys()) == set(env.keys())


def test_alpha_sorted_env_preserves_values():
    env = {"Z": "zval", "A": "aval"}
    report = run_sort(env)
    assert report.sorted_env["Z"] == "zval"
    assert report.sorted_env["A"] == "aval"


def test_already_sorted_flag_true():
    report = run_sort({"A": "1", "B": "2", "C": "3"})
    assert report.is_already_sorted is True


def test_already_sorted_flag_false():
    report = run_sort({"C": "3", "A": "1"})
    assert report.is_already_sorted is False


def test_mode_recorded_as_alpha():
    report = run_sort({"A": "1"}, mode="alpha")
    assert report.mode == "alpha"


# ---------------------------------------------------------------------------
# Group mode
# ---------------------------------------------------------------------------

def test_group_sort_clusters_by_prefix():
    env = {"DB_PORT": "5432", "AWS_KEY": "k", "DB_HOST": "localhost", "AWS_SECRET": "s"}
    report = run_sort(env, mode="group")
    keys = report.sorted_order
    aws_indices = [keys.index(k) for k in keys if k.startswith("AWS")]
    db_indices = [keys.index(k) for k in keys if k.startswith("DB")]
    assert max(aws_indices) < min(db_indices) or max(db_indices) < min(aws_indices)


def test_group_mode_recorded():
    report = run_sort({"A": "1"}, mode="group")
    assert report.mode == "group"


def test_group_sort_within_prefix_is_alphabetical():
    env = {"DB_PORT": "5432", "DB_HOST": "localhost", "DB_NAME": "mydb"}
    report = run_sort(env, mode="group")
    db_keys = [k for k in report.sorted_order if k.startswith("DB")]
    assert db_keys == sorted(db_keys)


# ---------------------------------------------------------------------------
# moved_count
# ---------------------------------------------------------------------------

def test_moved_count_zero_when_already_sorted():
    report = run_sort({"A": "1", "B": "2"})
    assert report.moved_count == 0


def test_moved_count_nonzero_when_reordered():
    report = run_sort({"Z": "1", "A": "2"})
    assert report.moved_count > 0
