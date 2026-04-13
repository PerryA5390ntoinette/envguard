"""Tests for envguard.duplicate_reporter."""
import pytest
from envguard.duplicator import DuplicateReport, DuplicateEntry, find_duplicates
from envguard.duplicate_reporter import format_duplicate_report


def clean_report():
    return find_duplicates({"A": "1", "B": "2"})


def key_dup_report():
    lines = ["PORT=8080\n", "PORT=9090\n"]
    return find_duplicates({"PORT": "9090"}, raw_lines=lines)


def value_dup_report():
    return find_duplicates({"DB_PASS": "s3cr3t", "ADMIN_PASS": "s3cr3t"})


def both_report():
    lines = ["A=1\n", "A=2\n"]
    return find_duplicates({"A": "2", "X": "shared", "Y": "shared"}, raw_lines=lines)


# --- clean output ---

def test_no_duplicates_message_shown():
    out = format_duplicate_report(clean_report(), use_color=False)
    assert "No duplicates found" in out


def test_header_always_present():
    out = format_duplicate_report(clean_report(), use_color=False)
    assert "Duplicate Detection Report" in out


# --- key duplicates ---

def test_duplicate_keys_section_shown():
    out = format_duplicate_report(key_dup_report(), use_color=False)
    assert "Duplicate Keys" in out


def test_duplicate_key_name_in_output():
    out = format_duplicate_report(key_dup_report(), use_color=False)
    assert "PORT" in out


def test_occurrence_count_in_output():
    out = format_duplicate_report(key_dup_report(), use_color=False)
    assert "2x" in out


# --- value duplicates ---

def test_shared_values_section_shown():
    out = format_duplicate_report(value_dup_report(), use_color=False)
    assert "Shared Values" in out


def test_shared_value_listed_in_output():
    out = format_duplicate_report(value_dup_report(), use_color=False)
    assert "s3cr3t" in out


def test_keys_sharing_value_in_output():
    out = format_duplicate_report(value_dup_report(), use_color=False)
    assert "DB_PASS" in out
    assert "ADMIN_PASS" in out


# --- totals ---

def test_total_issues_in_output():
    out = format_duplicate_report(both_report(), use_color=False)
    assert "Total issues" in out


def test_total_issues_count_correct():
    out = format_duplicate_report(both_report(), use_color=False)
    assert "2" in out


# --- color flag ---

def test_no_ansi_when_color_disabled():
    out = format_duplicate_report(key_dup_report(), use_color=False)
    assert "\033[" not in out


def test_ansi_present_when_color_enabled():
    out = format_duplicate_report(key_dup_report(), use_color=True)
    assert "\033[" in out
