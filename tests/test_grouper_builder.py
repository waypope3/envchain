"""Integration tests: grouper functions accessed via EnvChainBuilder."""

import pytest
from envchain.builder import EnvChainBuilder


def _build(*dicts):
    b = EnvChainBuilder()
    for d in dicts:
        b.add_dict(d)
    return b


class TestBuilderGrouperIntegration:
    def test_group_by_prefix_from_builder(self):
        b = _build({"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"})
        groups = b.group_by_prefix()
        assert groups["DB"] == {"HOST": "localhost", "PORT": "5432"}
        assert groups["APP"] == {"NAME": "myapp"}

    def test_group_by_prefix_lowercase(self):
        b = _build({"DB_HOST": "h", "APP_NAME": "a"})
        groups = b.group_by_prefix(lowercase_groups=True)
        assert "db" in groups
        assert "app" in groups

    def test_group_by_mapping_from_builder(self):
        b = _build({"HOST": "localhost", "PORT": "5432", "SECRET": "xyz"})
        mapping = {"database": ["HOST", "PORT"], "auth": ["SECRET"]}
        groups = b.group_by_mapping(mapping)
        assert groups["database"]["HOST"] == "localhost"
        assert groups["auth"]["SECRET"] == "xyz"

    def test_group_by_mapping_include_unmatched(self):
        b = _build({"HOST": "localhost", "ORPHAN": "val"})
        mapping = {"db": ["HOST"]}
        groups = b.group_by_mapping(mapping, include_unmatched=True)
        assert groups["__other__"] == {"ORPHAN": "val"}

    def test_group_by_predicate_from_builder(self):
        b = _build({"DB_HOST": "h", "APP_PORT": "80", "OTHER": "x"})
        preds = {
            "db": lambda k, v: k.startswith("DB_"),
            "app": lambda k, v: k.startswith("APP_"),
        }
        groups = b.group_by_predicate(preds, include_unmatched=True)
        assert "DB_HOST" in groups["db"]
        assert "APP_PORT" in groups["app"]
        assert groups["__other__"] == {"OTHER": "x"}

    def test_merged_layers_before_grouping(self):
        """Layers are resolved before grouping, so overrides apply."""
        b = _build(
            {"DB_HOST": "old", "APP_NAME": "app"},
            {"DB_HOST": "new"},
        )
        groups = b.group_by_prefix()
        assert groups["DB"]["HOST"] == "new"
