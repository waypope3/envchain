"""Tests for envchain.flattener — flatten/unflatten nested env dicts."""

import pytest
from envchain.flattener import flatten_dict, unflatten_dict, FlattenError


class TestFlattenDict:
    def test_flat_dict_unchanged(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        assert flatten_dict(env) == {"HOST": "localhost", "PORT": "5432"}

    def test_one_level_nesting(self):
        nested = {"DB": {"HOST": "localhost", "PORT": "5432"}}
        result = flatten_dict(nested)
        assert result == {"DB__HOST": "localhost", "DB__PORT": "5432"}

    def test_two_level_nesting(self):
        nested = {"APP": {"DB": {"HOST": "localhost"}}}
        result = flatten_dict(nested)
        assert result == {"APP__DB__HOST": "localhost"}

    def test_custom_delimiter(self):
        nested = {"DB": {"HOST": "localhost"}}
        result = flatten_dict(nested, delimiter=".")
        assert result == {"DB.HOST": "localhost"}

    def test_non_string_leaf_converted(self):
        nested = {"RETRIES": 3, "ENABLED": True}
        result = flatten_dict(nested)
        assert result == {"RETRIES": "3", "ENABLED": "True"}

    def test_empty_dict_returns_empty(self):
        assert flatten_dict({}) == {}

    def test_non_dict_input_raises(self):
        with pytest.raises(FlattenError, match="Expected a dict"):
            flatten_dict(["not", "a", "dict"])  # type: ignore

    def test_empty_delimiter_raises(self):
        with pytest.raises(FlattenError, match="Delimiter"):
            flatten_dict({"A": "1"}, delimiter="")

    def test_non_string_key_raises(self):
        with pytest.raises(FlattenError, match="keys must be strings"):
            flatten_dict({1: "value"})  # type: ignore

    def test_mixed_nested_and_flat_keys(self):
        nested = {"DB": {"HOST": "localhost"}, "DEBUG": "true"}
        result = flatten_dict(nested)
        assert result["DB__HOST"] == "localhost"
        assert result["DEBUG"] == "true"


class TestUnflattenDict:
    def test_single_level_keys_unchanged(self):
        flat = {"HOST": "localhost", "PORT": "5432"}
        assert unflatten_dict(flat) == {"HOST": "localhost", "PORT": "5432"}

    def test_one_level_nesting_restored(self):
        flat = {"DB__HOST": "localhost", "DB__PORT": "5432"}
        result = unflatten_dict(flat)
        assert result == {"DB": {"HOST": "localhost", "PORT": "5432"}}

    def test_two_level_nesting_restored(self):
        flat = {"APP__DB__HOST": "localhost"}
        result = unflatten_dict(flat)
        assert result == {"APP": {"DB": {"HOST": "localhost"}}}

    def test_custom_delimiter(self):
        flat = {"DB.HOST": "localhost"}
        result = unflatten_dict(flat, delimiter=".")
        assert result == {"DB": {"HOST": "localhost"}}

    def test_empty_dict_returns_empty(self):
        assert unflatten_dict({}) == {}

    def test_non_dict_input_raises(self):
        with pytest.raises(FlattenError, match="Expected a dict"):
            unflatten_dict("not a dict")  # type: ignore

    def test_empty_delimiter_raises(self):
        with pytest.raises(FlattenError, match="Delimiter"):
            unflatten_dict({"A": "1"}, delimiter="")

    def test_leaf_branch_conflict_raises(self):
        flat = {"A__B": "value1", "A__B__C": "value2"}
        with pytest.raises(FlattenError, match="conflict"):
            unflatten_dict(flat)

    def test_roundtrip_flatten_unflatten(self):
        original = {"DB": {"HOST": "localhost", "PORT": "5432"}, "DEBUG": "true"}
        flat = flatten_dict(original)
        restored = unflatten_dict(flat)
        assert restored == original
