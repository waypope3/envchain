"""Edge-case and boundary tests for envchain.grouper."""

import pytest
from envchain.grouper import (
    GroupError,
    group_by_prefix,
    group_by_mapping,
    group_by_predicate,
)


class TestGroupByPrefixEdgeCases:
    def test_multiple_separators_splits_on_first_only(self):
        env = {"A_B_C": "val"}
        result = group_by_prefix(env, separator="_")
        # 'A_B_C' -> group='A', remainder='B_C'
        assert result["A"] == {"B_C": "val"}

    def test_all_keys_share_same_prefix(self):
        env = {"X_ONE": "1", "X_TWO": "2"}
        result = group_by_prefix(env)
        assert len(result) == 1
        assert set(result["X"].keys()) == {"ONE", "TWO"}

    def test_all_keys_have_no_separator(self):
        env = {"FOO": "a", "BAR": "b"}
        result = group_by_prefix(env)
        assert list(result.keys()) == [""]
        assert result[""] == {"FOO": "a", "BAR": "b"}

    def test_non_string_separator_raises(self):
        with pytest.raises(GroupError):
            group_by_prefix({"A_B": "v"}, separator=None)  # type: ignore


class TestGroupByMappingEdgeCases:
    def test_empty_mapping_returns_empty_groups(self):
        env = {"HOST": "h"}
        result = group_by_mapping(env, {})
        assert result == {}

    def test_key_in_multiple_groups_assigned_to_first_match(self):
        """group_by_mapping assigns each key independently; duplicates allowed."""
        env = {"HOST": "h"}
        mapping = {"a": ["HOST"], "b": ["HOST"]}
        result = group_by_mapping(env, mapping)
        # Both groups receive the key because mapping is explicit
        assert result["a"]["HOST"] == "h"
        assert result["b"]["HOST"] == "h"

    def test_empty_env_all_groups_empty(self):
        mapping = {"db": ["HOST"], "auth": ["TOKEN"]}
        result = group_by_mapping({}, mapping)
        assert result == {"db": {}, "auth": {}}

    def test_no_unmatched_when_all_assigned(self):
        env = {"HOST": "h"}
        mapping = {"db": ["HOST"]}
        result = group_by_mapping(env, mapping, include_unmatched=True)
        assert "__other__" not in result


class TestGroupByPredicateEdgeCases:
    def test_first_matching_predicate_wins(self):
        """If multiple predicates match, only the first is applied."""
        env = {"DB_HOST": "h"}
        predicates = {
            "first": lambda k, v: k.startswith("DB_"),
            "second": lambda k, v: True,
        }
        result = group_by_predicate(env, predicates)
        assert "DB_HOST" in result["first"]
        assert "DB_HOST" not in result["second"]

    def test_value_based_predicate(self):
        env = {"PORT": "443", "DEBUG": "false"}
        predicates = {
            "secure": lambda k, v: v == "443",
            "flags": lambda k, v: v in ("true", "false"),
        }
        result = group_by_predicate(env, predicates)
        assert result["secure"] == {"PORT": "443"}
        assert result["flags"] == {"DEBUG": "false"}

    def test_empty_predicates_all_unmatched(self):
        env = {"A": "1"}
        result = group_by_predicate(env, {}, include_unmatched=True)
        assert result["__other__"] == {"A": "1"}
