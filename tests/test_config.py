"""Tests for configuration loading (src/config.py).

The important guarantee is that a missing or malformed helplines file never
crashes the program - it falls back to safe defaults.
"""

import json

import pytest

from src import config, paths


@pytest.fixture
def helplines_file(tmp_path, monkeypatch):
    """Redirect the helplines path to a temporary file and return a writer."""
    target = tmp_path / "helplines.json"

    def write(content):
        target.write_text(content, encoding="utf-8")

    monkeypatch.setattr(paths, "HELPLINES_FILE", target)
    return write


def test_valid_file_is_loaded(helplines_file):
    helplines_file(
        json.dumps(
            {
                "crisis_message": "Please get help.",
                "helplines": [{"region": "X", "name": "N", "number": "1"}],
            }
        )
    )
    data = config.load_helplines()
    assert data["crisis_message"] == "Please get help."
    assert len(data["helplines"]) == 1


def test_missing_file_returns_fallback(helplines_file):
    # Nothing written -> file does not exist.
    data = config.load_helplines()
    assert "helplines" in data and isinstance(data["helplines"], list)
    assert data["helplines"]  # fallback has at least one entry


def test_bad_json_returns_fallback(helplines_file):
    helplines_file("{ this is not valid json ")
    data = config.load_helplines()
    assert data["helplines"]


def test_helplines_null_returns_fallback(helplines_file):
    helplines_file(json.dumps({"crisis_message": "x", "helplines": None}))
    data = config.load_helplines()
    assert isinstance(data["helplines"], list)
    assert data["helplines"]


def test_helplines_not_a_list_returns_fallback(helplines_file):
    helplines_file(json.dumps({"helplines": "oops"}))
    data = config.load_helplines()
    assert isinstance(data["helplines"], list)
    assert data["helplines"]


def test_helplines_with_non_dict_entries_returns_fallback(helplines_file):
    helplines_file(json.dumps({"helplines": ["a", "b"]}))
    data = config.load_helplines()
    assert isinstance(data["helplines"], list)
    assert data["helplines"]


def test_empty_helplines_list_is_allowed(helplines_file):
    helplines_file(json.dumps({"crisis_message": "x", "helplines": []}))
    data = config.load_helplines()
    assert data["helplines"] == []
    assert data["crisis_message"] == "x"


def test_missing_crisis_message_is_filled(helplines_file):
    helplines_file(json.dumps({"helplines": []}))
    data = config.load_helplines()
    assert isinstance(data["crisis_message"], str)
    assert data["crisis_message"]
