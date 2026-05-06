"""Tests for envchain.snapshot module."""

import json
import os
import tempfile
import pytest

from envchain.snapshot import (
    create_snapshot,
    restore_snapshot,
    save_snapshot_to_file,
    load_snapshot_from_file,
    diff_with_snapshot,
    SnapshotError,
)


SAMPLE_ENV = {"APP_ENV": "production", "DB_HOST": "localhost", "PORT": "5432"}


class TestCreateSnapshot:
    def test_contains_data_key(self):
        snap = create_snapshot(SAMPLE_ENV)
        assert "data" in snap

    def test_data_equals_input(self):
        snap = create_snapshot(SAMPLE_ENV)
        assert snap["data"] == SAMPLE_ENV

    def test_data_is_deep_copy(self):
        env = {"KEY": "value"}
        snap = create_snapshot(env)
        env["KEY"] = "mutated"
        assert snap["data"]["KEY"] == "value"

    def test_label_stored(self):
        snap = create_snapshot(SAMPLE_ENV, label="v1")
        assert snap["label"] == "v1"

    def test_empty_label_default(self):
        snap = create_snapshot(SAMPLE_ENV)
        assert snap["label"] == ""

    def test_timestamp_present(self):
        snap = create_snapshot(SAMPLE_ENV)
        assert "timestamp" in snap and snap["timestamp"]


class TestRestoreSnapshot:
    def test_returns_env_data(self):
        snap = create_snapshot(SAMPLE_ENV)
        restored = restore_snapshot(snap)
        assert restored == SAMPLE_ENV

    def test_returns_deep_copy(self):
        snap = create_snapshot(SAMPLE_ENV)
        restored = restore_snapshot(snap)
        restored["APP_ENV"] = "changed"
        assert snap["data"]["APP_ENV"] == "production"

    def test_missing_data_raises(self):
        with pytest.raises(SnapshotError, match="missing 'data' key"):
            restore_snapshot({"label": "bad"})


class TestFilePersistence:
    def test_save_and_load_roundtrip(self):
        snap = create_snapshot(SAMPLE_ENV, label="roundtrip")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_snapshot_to_file(snap, path)
            loaded = load_snapshot_from_file(path)
            assert loaded["data"] == SAMPLE_ENV
            assert loaded["label"] == "roundtrip"
        finally:
            os.unlink(path)

    def test_load_missing_file_raises(self):
        with pytest.raises(SnapshotError, match="Failed to load snapshot"):
            load_snapshot_from_file("/nonexistent/path/snap.json")

    def test_load_invalid_json_raises(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("not json{{{")
            path = f.name
        try:
            with pytest.raises(SnapshotError):
                load_snapshot_from_file(path)
        finally:
            os.unlink(path)


class TestDiffWithSnapshot:
    def test_no_changes_empty_diff(self):
        snap = create_snapshot(SAMPLE_ENV)
        result = diff_with_snapshot(SAMPLE_ENV.copy(), snap)
        assert result == {"added": {}, "removed": {}, "changed": {}}

    def test_added_key_detected(self):
        snap = create_snapshot({"A": "1"})
        result = diff_with_snapshot({"A": "1", "B": "2"}, snap)
        assert result["added"] == {"B": "2"}

    def test_removed_key_detected(self):
        snap = create_snapshot({"A": "1", "B": "2"})
        result = diff_with_snapshot({"A": "1"}, snap)
        assert result["removed"] == {"B": "2"}

    def test_changed_value_detected(self):
        snap = create_snapshot({"A": "old"})
        result = diff_with_snapshot({"A": "new"}, snap)
        assert result["changed"] == {"A": {"before": "old", "after": "new"}}
