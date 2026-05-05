"""Integration tests for EnvChainBuilder export shortcuts."""

import json
import os
import tempfile

import pytest

from envchain.builder import EnvChainBuilder


class TestBuilderExportShortcuts:
    def _builder_with_data(self) -> EnvChainBuilder:
        return (
            EnvChainBuilder()
            .add_dict({"BASE": "base_val", "SHARED": "from_base"})
            .add_dict({"OVERRIDE": "new_val", "SHARED": "from_override"})
        )

    def test_to_dict_returns_merged(self):
        result = self._builder_with_data().to_dict()
        assert result["BASE"] == "base_val"
        assert result["OVERRIDE"] == "new_val"
        assert result["SHARED"] == "from_override"

    def test_to_json_valid(self):
        result = self._builder_with_data().to_json()
        parsed = json.loads(result)
        assert parsed["BASE"] == "base_val"

    def test_to_dotenv_contains_keys(self):
        result = self._builder_with_data().to_dotenv()
        assert "BASE=base_val" in result
        assert "OVERRIDE=new_val" in result

    def test_to_env_injects_into_os(self, monkeypatch):
        monkeypatch.delenv("BASE", raising=False)
        monkeypatch.delenv("OVERRIDE", raising=False)
        self._builder_with_data().to_env()
        assert os.environ["BASE"] == "base_val"
        assert os.environ["OVERRIDE"] == "new_val"

    def test_to_env_with_prefix(self, monkeypatch):
        monkeypatch.delenv("PFX_BASE", raising=False)
        self._builder_with_data().to_env(prefix="PFX_")
        assert os.environ["PFX_BASE"] == "base_val"

    def test_to_json_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        self._builder_with_data().to_json_file(path)
        with open(path) as f:
            data = json.load(f)
        assert data["SHARED"] == "from_override"

    def test_to_dotenv_file(self):
        with tempfile.NamedTemporaryFile(suffix='.env', mode='w', delete=False) as f:
            path = f.name
        self._builder_with_data().to_dotenv_file(path)
        with open(path) as f:
            content = f.read()
        assert "SHARED=from_override" in content

    def test_missing_dotenv_file_skipped(self):
        builder = EnvChainBuilder().add_dotenv('/nonexistent/.env').add_dict({"K": "v"})
        assert builder.resolve()["K"] == "v"

    def test_missing_json_file_skipped(self):
        builder = EnvChainBuilder().add_json('/nonexistent/config.json').add_dict({"K": "v"})
        assert builder.resolve()["K"] == "v"

    def test_build_returns_envchain(self):
        from envchain.chain import EnvChain
        chain = self._builder_with_data().build()
        assert isinstance(chain, EnvChain)
