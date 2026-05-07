"""Tests for envchain.reporter."""

import json

import pytest

from envchain.comparator import compare_envs
from envchain.reporter import ReportError, render_json_report, render_text_report


class TestRenderTextReport:
    def test_no_differences_message(self):
        result = compare_envs({"A": "1"}, {"A": "1"})
        report = render_text_report(result)
        assert report == "No differences."

    def test_added_section_present(self):
        result = compare_envs({}, {"NEW": "val"})
        report = render_text_report(result)
        assert "Added:" in report
        assert "+ NEW=val" in report

    def test_removed_section_present(self):
        result = compare_envs({"OLD": "val"}, {})
        report = render_text_report(result)
        assert "Removed:" in report
        assert "- OLD=val" in report

    def test_changed_section_present(self):
        result = compare_envs({"K": "before"}, {"K": "after"})
        report = render_text_report(result)
        assert "Changed:" in report
        assert "'before'" in report
        assert "'after'" in report

    def test_unchanged_hidden_by_default(self):
        result = compare_envs({"A": "1"}, {"A": "1"})
        report = render_text_report(result)
        assert "Unchanged:" not in report

    def test_unchanged_shown_when_flag_set(self):
        result = compare_envs({"A": "1"}, {"A": "1"})
        report = render_text_report(result, show_unchanged=True)
        assert "Unchanged:" in report
        assert "= A=1" in report

    def test_invalid_input_raises(self):
        with pytest.raises(ReportError):
            render_text_report({"not": "a result"})

    def test_multiple_sections_ordering(self):
        result = compare_envs({"B": "old", "C": "gone"}, {"A": "new", "B": "new"})
        report = render_text_report(result)
        assert report.index("Added:") < report.index("Removed:") < report.index("Changed:")


class TestRenderJsonReport:
    def test_returns_valid_json(self):
        result = compare_envs({"A": "1"}, {"A": "2", "B": "3"})
        raw = render_json_report(result)
        parsed = json.loads(raw)
        assert "added" in parsed
        assert "changed" in parsed

    def test_added_key_in_json(self):
        result = compare_envs({}, {"X": "10"})
        parsed = json.loads(render_json_report(result))
        assert parsed["added"]["X"] == "10"

    def test_changed_has_before_after(self):
        result = compare_envs({"K": "old"}, {"K": "new"})
        parsed = json.loads(render_json_report(result))
        assert parsed["changed"]["K"] == {"before": "old", "after": "new"}

    def test_invalid_input_raises(self):
        with pytest.raises(ReportError):
            render_json_report("bad input")
