"""Tests for envguard.planner and envguard.plan_reporter."""
import pytest
from envguard.planner import plan_migration, PlanReport, PlanAction
from envguard.plan_reporter import format_plan_report, format_plan_action


def run_plan(current, target):
    return plan_migration(current, target)


# --- plan_migration core behaviour ---

def test_returns_plan_report_instance():
    assert isinstance(run_plan({}, {}), PlanReport)


def test_empty_envs_produce_no_actions():
    report = run_plan({}, {})
    assert report.actions == []


def test_new_key_in_target_is_add():
    report = run_plan({}, {"FOO": "bar"})
    assert report.add_count == 1
    assert report.actions[0].action == "add"
    assert report.actions[0].key == "FOO"
    assert report.actions[0].new_value == "bar"


def test_key_missing_from_target_is_remove():
    report = run_plan({"FOO": "bar"}, {})
    assert report.remove_count == 1
    assert report.actions[0].action == "remove"
    assert report.actions[0].old_value == "bar"


def test_differing_value_is_update():
    report = run_plan({"FOO": "old"}, {"FOO": "new"})
    assert report.update_count == 1
    action = report.actions[0]
    assert action.action == "update"
    assert action.old_value == "old"
    assert action.new_value == "new"


def test_identical_value_is_keep():
    report = run_plan({"FOO": "same"}, {"FOO": "same"})
    assert report.keep_count == 1
    assert report.actions[0].action == "keep"


def test_has_changes_false_when_all_kept():
    report = run_plan({"A": "1"}, {"A": "1"})
    assert not report.has_changes


def test_has_changes_true_when_add_present():
    report = run_plan({}, {"NEW": "val"})
    assert report.has_changes


def test_mixed_env_correct_counts():
    current = {"A": "1", "B": "old", "C": "gone"}
    target  = {"A": "1", "B": "new", "D": "fresh"}
    report = run_plan(current, target)
    assert report.add_count == 1
    assert report.remove_count == 1
    assert report.update_count == 1
    assert report.keep_count == 1


def test_actions_sorted_alphabetically():
    report = run_plan({"Z": "1"}, {"A": "2"})
    keys = [a.key for a in report.actions]
    assert keys == sorted(keys)


def test_add_action_old_value_is_none():
    report = run_plan({}, {"X": "v"})
    assert report.actions[0].old_value is None


def test_remove_action_new_value_is_none():
    report = run_plan({"X": "v"}, {})
    assert report.actions[0].new_value is None


# --- plan_reporter ---

def test_format_plan_report_contains_header():
    report = run_plan({}, {})
    out = format_plan_report(report, use_color=False)
    assert "Migration Plan" in out


def test_format_plan_report_shows_add_label():
    report = run_plan({}, {"FOO": "bar"})
    out = format_plan_report(report, use_color=False)
    assert "ADD" in out
    assert "FOO" in out


def test_format_plan_report_shows_remove_label():
    report = run_plan({"FOO": "bar"}, {})
    out = format_plan_report(report, use_color=False)
    assert "REMOVE" in out


def test_format_plan_report_shows_summary_counts():
    report = run_plan({"A": "1"}, {"A": "2", "B": "3"})
    out = format_plan_report(report, use_color=False)
    assert "1 add" in out
    assert "1 update" in out


def test_format_action_update_shows_old_and_new():
    action = PlanAction("update", "KEY", "old_val", "new_val")
    out = format_plan_action(action, use_color=False)
    assert "old_val" in out
    assert "new_val" in out
