"""Tests for envchain.renderer module."""

import pytest
from envchain.renderer import render_string, render_dict, list_placeholders, RenderError


class TestRenderString:
    def test_no_placeholders_unchanged(self):
        assert render_string("hello world", {}) == "hello world"

    def test_single_placeholder_replaced(self):
        result = render_string("Hello, {{ NAME }}!", {"NAME": "Alice"})
        assert result == "Hello, Alice!"

    def test_multiple_placeholders_replaced(self):
        result = render_string("{{ GREETING }}, {{ NAME }}!", {"GREETING": "Hi", "NAME": "Bob"})
        assert result == "Hi, Bob!"

    def test_placeholder_with_spaces(self):
        result = render_string("{{  KEY  }}", {"KEY": "value"})
        assert result == "value"

    def test_numeric_value_converted_to_string(self):
        result = render_string("Port: {{ PORT }}", {"PORT": 8080})
        assert result == "Port: 8080"

    def test_strict_missing_key_raises(self):
        with pytest.raises(RenderError) as exc_info:
            render_string("{{ MISSING }}", {}, strict=True)
        assert "MISSING" in exc_info.value.message

    def test_non_strict_missing_key_leaves_placeholder(self):
        result = render_string("{{ MISSING }}", {}, strict=False)
        assert result == "{{ MISSING }}"

    def test_same_placeholder_twice(self):
        result = render_string("{{ X }} and {{ X }}", {"X": "foo"})
        assert result == "foo and foo"

    def test_empty_template(self):
        assert render_string("", {"KEY": "val"}) == ""

    def test_extra_env_keys_ignored(self):
        result = render_string("{{ A }}", {"A": "1", "B": "2"})
        assert result == "1"


class TestRenderDict:
    def test_all_values_rendered(self):
        templates = {"greeting": "Hello, {{ NAME }}!", "farewell": "Bye, {{ NAME }}!"}
        result = render_dict(templates, {"NAME": "Carol"})
        assert result == {"greeting": "Hello, Carol!", "farewell": "Bye, Carol!"}

    def test_empty_templates_returns_empty(self):
        assert render_dict({}, {"KEY": "val"}) == {}

    def test_returns_new_dict(self):
        templates = {"k": "{{ V }}"}
        result = render_dict(templates, {"V": "x"})
        assert result is not templates

    def test_strict_propagated(self):
        with pytest.raises(RenderError):
            render_dict({"k": "{{ MISSING }}"}, {}, strict=True)

    def test_non_strict_propagated(self):
        result = render_dict({"k": "{{ MISSING }}"}, {}, strict=False)
        assert result == {"k": "{{ MISSING }}"}


class TestListPlaceholders:
    def test_no_placeholders_returns_empty(self):
        assert list_placeholders("no placeholders here") == []

    def test_single_placeholder(self):
        assert list_placeholders("{{ FOO }}") == ["FOO"]

    def test_multiple_unique_placeholders(self):
        result = list_placeholders("{{ A }} and {{ B }}")
        assert result == ["A", "B"]

    def test_duplicate_placeholder_listed_once(self):
        result = list_placeholders("{{ X }} {{ X }} {{ X }}")
        assert result == ["X"]

    def test_order_preserved(self):
        result = list_placeholders("{{ C }} {{ A }} {{ B }}")
        assert result == ["C", "A", "B"]
