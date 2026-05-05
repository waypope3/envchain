"""Tests for envchain.exporter."""

import json
import os
import tempfile

import pytest

from envchain.exporter import (
    export_to_dict,
    export_to_dotenv,
    export_to_dotenv_file,
    export_to_env,
    export_to_json,
    export_to_json_file,
)

SAMPLE = {"APP_ENV": "production", "DB_HOST": "localhost", "SECRET": "abc123"}


class TestExportToDict:
    def test_returns_copy(self):
        result = export_to_dict(SAMPLE)
        assert result == SAMPLE
        assert result is not SAMPLE

    def test_empty_input(self):
        assert export_to_dict({}) == {}


class TestExportToJson:
    def test_valid_json(self):
        result = export_to_json(SAMPLE)
        parsed = json.loads(result)
        assert parsed == SAMPLE

    def test_keys_sorted(self):
        result = export_to_json(SAMPLE)
        keys = list(json.loads(result).keys())
        assert keys == sorted(keys)

    def test_custom_indent(self):
        result = export_to_json({"A": "1"}, indent=4)
        assert '    ' in result


class TestExportToDotenv:
    def test_simple_values(self):
        result = export_to_dotenv({"FOO": "bar", "BAZ": "qux"})
        assert "FOO=bar" in result
        assert "BAZ=qux" in result

    def test_value_with_space_is_quoted(self):
        result = export_to_dotenv({"MSG": "hello world"})
        assert 'MSG="hello world"' in result

    def test_value_with_newline_escaped(self):
        result = export_to_dotenv({"MULTI": "line1\nline2"})
        assert '\\n' in result

    def test_empty_dict_produces_empty_string(self):
        assert export_to_dotenv({}) == ""

    def test_keys_sorted(self):
        result = export_to_dotenv({"Z": "1", "A": "2"})
        lines = result.splitlines()
        assert lines[0].startswith("A=")
        assert lines[1].startswith("Z=")


class TestExportToEnv:
    def test_sets_os_environ(self, monkeypatch):
        monkeypatch.delenv("_TEST_KEY", raising=False)
        export_to_env({"_TEST_KEY": "myvalue"})
        assert os.environ["_TEST_KEY"] == "myvalue"

    def test_prefix_prepended(self, monkeypatch):
        monkeypatch.delenv("MYAPP_FOO", raising=False)
        export_to_env({"FOO": "bar"}, prefix="MYAPP_")
        assert os.environ["MYAPP_FOO"] == "bar"


class TestExportToFiles:
    def test_json_file_roundtrip(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        export_to_json_file(SAMPLE, path)
        with open(path) as f:
            data = json.load(f)
        assert data == SAMPLE

    def test_dotenv_file_written(self):
        with tempfile.NamedTemporaryFile(suffix='.env', mode='w', delete=False) as f:
            path = f.name
        export_to_dotenv_file({"KEY": "val"}, path)
        with open(path) as f:
            content = f.read()
        assert "KEY=val" in content
