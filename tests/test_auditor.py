"""Tests for envchain.auditor module."""

import pytest
from envchain.auditor import AuditEntry, EnvAuditor


class TestAuditEntry:
    def test_to_dict_has_required_keys(self):
        entry = AuditEntry("add", "FOO", new_value="bar", source="test")
        d = entry.to_dict()
        assert set(d.keys()) == {"timestamp", "operation", "key", "old_value", "new_value", "source"}

    def test_to_dict_values_correct(self):
        entry = AuditEntry("override", "KEY", old_value="old", new_value="new", source="layer1")
        d = entry.to_dict()
        assert d["operation"] == "override"
        assert d["key"] == "KEY"
        assert d["old_value"] == "old"
        assert d["new_value"] == "new"
        assert d["source"] == "layer1"

    def test_timestamp_is_string(self):
        entry = AuditEntry("add", "X")
        assert isinstance(entry.to_dict()["timestamp"], str)

    def test_repr_contains_operation_and_key(self):
        entry = AuditEntry("add", "MY_KEY", source="env")
        r = repr(entry)
        assert "add" in r
        assert "MY_KEY" in r


class TestEnvAuditor:
    def test_initial_log_empty(self):
        auditor = EnvAuditor()
        assert len(auditor) == 0
        assert auditor.get_log() == []

    def test_record_adds_entry(self):
        auditor = EnvAuditor()
        auditor.record("add", "FOO", new_value="bar", source="env")
        assert len(auditor) == 1

    def test_get_log_returns_dicts(self):
        auditor = EnvAuditor()
        auditor.record("add", "A", new_value="1")
        log = auditor.get_log()
        assert isinstance(log[0], dict)
        assert log[0]["key"] == "A"

    def test_record_layer_detects_add(self):
        auditor = EnvAuditor()
        auditor.record_layer({}, {"NEW_KEY": "val"}, source="layer1")
        adds = auditor.filter_by_operation("add")
        assert len(adds) == 1
        assert adds[0]["key"] == "NEW_KEY"

    def test_record_layer_detects_override(self):
        auditor = EnvAuditor()
        auditor.record_layer({"KEY": "old"}, {"KEY": "new"}, source="layer2")
        overrides = auditor.filter_by_operation("override")
        assert len(overrides) == 1
        assert overrides[0]["old_value"] == "old"
        assert overrides[0]["new_value"] == "new"

    def test_record_layer_detects_unchanged(self):
        auditor = EnvAuditor()
        auditor.record_layer({"KEY": "same"}, {"KEY": "same"}, source="layer3")
        unchanged = auditor.filter_by_operation("unchanged")
        assert len(unchanged) == 1

    def test_filter_by_key(self):
        auditor = EnvAuditor()
        auditor.record("add", "FOO", new_value="1")
        auditor.record("add", "BAR", new_value="2")
        result = auditor.filter_by_key("FOO")
        assert len(result) == 1
        assert result[0]["key"] == "FOO"

    def test_clear_empties_log(self):
        auditor = EnvAuditor()
        auditor.record("add", "X", new_value="y")
        auditor.clear()
        assert len(auditor) == 0

    def test_multiple_layers_accumulated(self):
        auditor = EnvAuditor()
        auditor.record_layer({}, {"A": "1", "B": "2"}, source="base")
        auditor.record_layer({"A": "1", "B": "2"}, {"B": "99", "C": "3"}, source="override")
        assert len(auditor) == 4
