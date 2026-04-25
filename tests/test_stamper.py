"""Tests for envguard.stamper."""
from __future__ import annotations

import re

import pytest

from envguard.stamper import StampEntry, StampReport, stamp_env


def run_stamp(env=None, **kwargs):
    if env is None:
        env = {}
    return stamp_env(env, **kwargs)


# --- StampReport helpers ---

def test_injected_count_zero_for_empty_report():
    assert StampReport().injected_count == 0


def test_skipped_count_zero_for_empty_report():
    assert StampReport().skipped_count == 0


def test_injected_keys_empty_for_empty_report():
    assert StampReport().injected_keys == []


# --- stamp_env: timestamp ---

def test_stamp_env_returns_tuple():
    result = run_stamp()
    assert isinstance(result, tuple) and len(result) == 2


def test_timestamp_key_injected_by_default():
    env, report = run_stamp()
    assert "ENVGUARD_STAMPED_AT" in env


def test_timestamp_value_matches_iso_format():
    env, _ = run_stamp()
    ts = env["ENVGUARD_STAMPED_AT"]
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ts)


def test_timestamp_key_custom_name():
    env, _ = run_stamp(timestamp_key="DEPLOYED_AT")
    assert "DEPLOYED_AT" in env


def test_timestamp_key_none_skips_injection():
    env, report = run_stamp(timestamp_key=None)
    assert "ENVGUARD_STAMPED_AT" not in env
    assert report.injected_count == 0


# --- stamp_env: version ---

def test_version_injected_when_provided():
    env, report = run_stamp(version="1.2.3")
    assert env.get("ENVGUARD_VERSION") == "1.2.3"
    assert "ENVGUARD_VERSION" in report.injected_keys


def test_version_not_injected_when_none():
    env, _ = run_stamp(version=None)
    assert "ENVGUARD_VERSION" not in env


# --- stamp_env: env_name ---

def test_env_name_injected_when_provided():
    env, _ = run_stamp(env_name="production")
    assert env["ENVGUARD_ENV"] == "production"


def test_env_name_not_injected_when_none():
    env, _ = run_stamp(env_name=None)
    assert "ENVGUARD_ENV" not in env


# --- overwrite behaviour ---

def test_existing_key_skipped_without_overwrite():
    existing = {"ENVGUARD_ENV": "staging"}
    env, report = run_stamp(existing, env_name="production", overwrite=False)
    assert env["ENVGUARD_ENV"] == "staging"
    skipped = [e for e in report.entries if not e.injected and e.key == "ENVGUARD_ENV"]
    assert len(skipped) == 1


def test_existing_key_overwritten_with_overwrite_true():
    existing = {"ENVGUARD_ENV": "staging"}
    env, report = run_stamp(existing, env_name="production", overwrite=True)
    assert env["ENVGUARD_ENV"] == "production"


def test_original_env_not_mutated():
    original = {"FOO": "bar"}
    run_stamp(original, version="0.1")
    assert "ENVGUARD_VERSION" not in original


# --- counts ---

def test_injected_count_reflects_new_keys():
    _, report = run_stamp(version="2", env_name="dev")
    # timestamp + version + env_name = 3 injected
    assert report.injected_count == 3


def test_skipped_count_reflects_pre_existing_keys():
    existing = {"ENVGUARD_STAMPED_AT": "old"}
    _, report = run_stamp(existing, overwrite=False)
    assert report.skipped_count == 1
