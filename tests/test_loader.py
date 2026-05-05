"""Tests for envchain.loader module."""

import json
import os
import textwrap
from pathlib import Path

import pytest

from envchain.loader import load_from_dotenv, load_from_env, load_from_json_file


# ---------------------------------------------------------------------------
# load_from_env
# ---------------------------------------------------------------------------

class TestLoadFromEnv:
    def test_returns_dict(self):
        result = load_from_env()
        assert isinstance(result, dict)

    def test_no_prefix_returns_all_env(self, monkeypatch):
        monkeypatch.setenv("TEST_ENVCHAIN_FOO", "bar")
        result = load_from_env()
        assert "TEST_ENVCHAIN_FOO" in result
        assert result["TEST_ENVCHAIN_FOO"] == "bar"

    def test_prefix_filters_and_strips(self, monkeypatch):
        monkeypatch.setenv("APP_HOST", "localhost")
        monkeypatch.setenv("APP_PORT", "8080")
        monkeypatch.setenv("OTHER_VAR", "ignored")
        result = load_from_env(prefix="APP_")
        assert "HOST" in result
        assert "PORT" in result
        assert "OTHER_VAR" not in result
        assert "APP_HOST" not in result

    def test_prefix_no_match_returns_empty(self, monkeypatch):
        result = load_from_env(prefix="ZZZNONEXISTENT_")
        assert result == {}


# ---------------------------------------------------------------------------
# load_from_json_file
# ---------------------------------------------------------------------------

class TestLoadFromJsonFile:
    def test_loads_flat_object(self, tmp_path):
        data = {"KEY": "value", "NUM": 42}
        f = tmp_path / "env.json"
        f.write_text(json.dumps(data))
        result = load_from_json_file(f)
        assert result == {"KEY": "value", "NUM": "42"}

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_from_json_file(tmp_path / "missing.json")

    def test_non_object_raises(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text(json.dumps(["a", "b"]))
        with pytest.raises(ValueError, match="JSON object"):
            load_from_json_file(f)

    def test_non_string_key_raises(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text('{"valid": "ok"}')
        result = load_from_json_file(f)
        assert result["valid"] == "ok"


# ---------------------------------------------------------------------------
# load_from_dotenv
# ---------------------------------------------------------------------------

class TestLoadFromDotenv:
    def test_basic_key_value(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("FOO=bar\nBAZ=qux\n")
        result = load_from_dotenv(f)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_ignores_comments_and_blank_lines(self, tmp_path):
        content = textwrap.dedent("""\
            # this is a comment

            KEY=value
        """)
        f = tmp_path / ".env"
        f.write_text(content)
        result = load_from_dotenv(f)
        assert result == {"KEY": "value"}

    def test_quoted_values_stripped(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text('SINGLE=\'hello world\'\nDOUBLE="hello world"\n')
        result = load_from_dotenv(f)
        assert result["SINGLE"] == "hello world"
        assert result["DOUBLE"] == "hello world"

    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_from_dotenv(tmp_path / "missing.env")

    def test_line_without_equals_ignored(self, tmp_path):
        f = tmp_path / ".env"
        f.write_text("NOEQUALS\nKEY=val\n")
        result = load_from_dotenv(f)
        assert result == {"KEY": "val"}
