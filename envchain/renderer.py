"""Template renderer for env variable substitution into arbitrary string templates."""

import re
from typing import Dict, Any


class RenderError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_string(template: str, env: Dict[str, Any], strict: bool = True) -> str:
    """Render a template string by substituting {{ VAR }} placeholders with env values.

    Args:
        template: A string containing {{ VAR }} style placeholders.
        env: Dictionary of environment variables to substitute.
        strict: If True, raise RenderError for missing keys. If False, leave unresolved.

    Returns:
        The rendered string with placeholders replaced.

    Raises:
        RenderError: If strict=True and a referenced key is not found in env.
    """
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in env:
            return str(env[key])
        if strict:
            raise RenderError(f"Template references undefined variable: '{key}'")
        return match.group(0)

    return _PLACEHOLDER_RE.sub(replacer, template)


def render_dict(templates: Dict[str, str], env: Dict[str, Any], strict: bool = True) -> Dict[str, str]:
    """Render all values in a dict of templates against the given env.

    Args:
        templates: Dict mapping keys to template strings.
        env: Dictionary of environment variables to substitute.
        strict: Passed through to render_string.

    Returns:
        A new dict with all template values rendered.
    """
    return {k: render_string(v, env, strict=strict) for k, v in templates.items()}


def list_placeholders(template: str) -> list:
    """Return a list of all unique placeholder variable names in a template string."""
    return list(dict.fromkeys(_PLACEHOLDER_RE.findall(template)))
