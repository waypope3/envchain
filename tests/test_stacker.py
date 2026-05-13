"""Tests for envchain.stacker."""

import pytest

from envchain.stacker import EnvStack, StackError


class TestEnvStackInit:
    def test_default_name(self):
        s = EnvStack()
        assert s.name == "default"

    def test_custom_name(self):
        s = EnvStack(name="prod")
        assert s.name == "prod"

    def test_empty_name_raises(self):
        with pytest.raises(StackError):
            EnvStack(name="")

    def test_non_string_name_raises(self):
        with pytest.raises(StackError):
            EnvStack(name=123)  # type: ignore

    def test_initial_depth_zero(self):
        assert EnvStack().depth == 0


class TestPushPop:
    def test_push_increases_depth(self):
        s = EnvStack()
        s.push({"A": "1"})
        assert s.depth == 1

    def test_pop_returns_pushed_value(self):
        s = EnvStack()
        s.push({"A": "1"})
        result = s.pop()
        assert result == {"A": "1"}

    def test_pop_decreases_depth(self):
        s = EnvStack()
        s.push({"A": "1"})
        s.pop()
        assert s.depth == 0

    def test_pop_empty_raises(self):
        s = EnvStack()
        with pytest.raises(StackError):
            s.pop()

    def test_push_non_dict_raises(self):
        s = EnvStack()
        with pytest.raises(StackError):
            s.push("not a dict")  # type: ignore

    def test_push_stores_copy(self):
        s = EnvStack()
        env = {"A": "1"}
        s.push(env)
        env["A"] = "mutated"
        assert s.pop()["A"] == "1"


class TestPeek:
    def test_peek_returns_top(self):
        s = EnvStack()
        s.push({"X": "10"})
        assert s.peek() == {"X": "10"}

    def test_peek_does_not_remove(self):
        s = EnvStack()
        s.push({"X": "10"})
        s.peek()
        assert s.depth == 1

    def test_peek_returns_copy(self):
        s = EnvStack()
        s.push({"X": "10"})
        peeked = s.peek()
        peeked["X"] = "mutated"
        assert s.peek()["X"] == "10"

    def test_peek_empty_raises(self):
        s = EnvStack()
        with pytest.raises(StackError):
            s.peek()


class TestMerged:
    def test_single_layer(self):
        s = EnvStack()
        s.push({"A": "1"})
        assert s.merged() == {"A": "1"}

    def test_top_overrides_bottom(self):
        s = EnvStack()
        s.push({"A": "base", "B": "shared"})
        s.push({"B": "override", "C": "new"})
        merged = s.merged()
        assert merged["A"] == "base"
        assert merged["B"] == "override"
        assert merged["C"] == "new"

    def test_empty_stack_returns_empty(self):
        s = EnvStack()
        assert s.merged() == {}

    def test_three_layers_merged_in_order(self):
        s = EnvStack()
        s.push({"K": "1"})
        s.push({"K": "2"})
        s.push({"K": "3"})
        assert s.merged()["K"] == "3"


class TestClearAndLabels:
    def test_clear_empties_stack(self):
        s = EnvStack()
        s.push({"A": "1"})
        s.push({"B": "2"})
        s.clear()
        assert s.depth == 0

    def test_labels_returns_indices(self):
        s = EnvStack()
        s.push({"A": "1"})
        s.push({"B": "2"})
        assert s.labels() == [0, 1]

    def test_labels_empty_stack(self):
        s = EnvStack()
        assert s.labels() == []
