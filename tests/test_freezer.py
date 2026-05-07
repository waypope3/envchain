"""Tests for envchain.freezer."""

import pytest

from envchain.freezer import FreezeError, FrozenEnv, freeze, unfreeze


class TestFrozenEnv:
    def test_getitem_returns_value(self):
        fe = FrozenEnv({"KEY": "val"})
        assert fe["KEY"] == "val"

    def test_missing_key_raises_keyerror(self):
        fe = FrozenEnv({"A": "1"})
        with pytest.raises(KeyError):
            _ = fe["MISSING"]

    def test_contains(self):
        fe = FrozenEnv({"X": "y"})
        assert "X" in fe
        assert "Z" not in fe

    def test_len(self):
        fe = FrozenEnv({"A": "1", "B": "2"})
        assert len(fe) == 2

    def test_iter(self):
        fe = FrozenEnv({"A": "1", "B": "2"})
        assert set(fe) == {"A", "B"}

    def test_get_with_default(self):
        fe = FrozenEnv({"A": "1"})
        assert fe.get("A") == "1"
        assert fe.get("MISSING", "default") == "default"

    def test_keys_values_items(self):
        fe = FrozenEnv({"A": "1"})
        assert list(fe.keys()) == ["A"]
        assert list(fe.values()) == ["1"]
        assert list(fe.items()) == [("A", "1")]

    def test_setattr_raises_freeze_error(self):
        fe = FrozenEnv({"A": "1"})
        with pytest.raises(FreezeError, match="immutable"):
            fe.new_attr = "oops"

    def test_delattr_raises_freeze_error(self):
        fe = FrozenEnv({"A": "1"})
        with pytest.raises(FreezeError, match="immutable"):
            del fe._data

    def test_repr_contains_data(self):
        fe = FrozenEnv({"K": "V"})
        assert "K" in repr(fe)
        assert "V" in repr(fe)

    def test_non_dict_raises_freeze_error(self):
        with pytest.raises(FreezeError):
            FrozenEnv(["not", "a", "dict"])  # type: ignore


class TestFreeze:
    def test_returns_frozen_env(self):
        result = freeze({"A": "1"})
        assert isinstance(result, FrozenEnv)

    def test_data_preserved(self):
        result = freeze({"ENV": "prod", "DEBUG": "false"})
        assert result["ENV"] == "prod"
        assert result["DEBUG"] == "false"

    def test_original_dict_not_shared(self):
        original = {"A": "1"}
        fe = freeze(original)
        original["A"] = "mutated"
        assert fe["A"] == "1"

    def test_non_dict_raises(self):
        with pytest.raises(FreezeError):
            freeze("not a dict")  # type: ignore


class TestUnfreeze:
    def test_returns_plain_dict(self):
        fe = freeze({"A": "1"})
        result = unfreeze(fe)
        assert isinstance(result, dict)

    def test_values_preserved(self):
        fe = freeze({"X": "10", "Y": "20"})
        result = unfreeze(fe)
        assert result == {"X": "10", "Y": "20"}

    def test_mutation_does_not_affect_frozen(self):
        fe = freeze({"A": "1"})
        result = unfreeze(fe)
        result["A"] = "mutated"
        assert fe["A"] == "1"

    def test_non_frozen_raises(self):
        with pytest.raises(FreezeError):
            unfreeze({"plain": "dict"})  # type: ignore
