"""EnvReporter — human-readable report generation from CompareResult."""

from __future__ import annotations

from typing import List

from envchain.comparator import CompareResult


class ReportError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def _fmt_line(symbol: str, key: str, value: str) -> str:
    return f"  {symbol} {key}={value}"


def render_text_report(result: CompareResult, *, show_unchanged: bool = False) -> str:
    """Render a CompareResult as a human-readable text report."""
    if not isinstance(result, CompareResult):
        raise ReportError("Expected a CompareResult instance.")

    lines: List[str] = []

    if result.added:
        lines.append("Added:")
        for k, v in sorted(result.added.items()):
            lines.append(_fmt_line("+", k, v))

    if result.removed:
        lines.append("Removed:")
        for k, v in sorted(result.removed.items()):
            lines.append(_fmt_line("-", k, v))

    if result.changed:
        lines.append("Changed:")
        for k, (before, after) in sorted(result.changed.items()):
            lines.append(f"  ~ {k}: {before!r} -> {after!r}")

    if show_unchanged and result.unchanged:
        lines.append("Unchanged:")
        for k, v in sorted(result.unchanged.items()):
            lines.append(_fmt_line("=", k, v))

    if not lines:
        return "No differences."

    return "\n".join(lines)


def render_json_report(result: CompareResult) -> str:
    """Render a CompareResult as a JSON string."""
    import json

    if not isinstance(result, CompareResult):
        raise ReportError("Expected a CompareResult instance.")

    return json.dumps(result.to_dict(), indent=2)
