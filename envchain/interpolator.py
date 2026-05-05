"""Variable interpolation for EnvChain resolved environments.

Supports ${VAR_NAME} and $VAR_NAME syntax for referencing other keys
within the same resolved environment.
"""

import re
from typing import Dict, Optional

_PATTERN = re.compile(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)')
_MAX_DEPTH = 10


class InterpolationError(Exception):
    """Raised when variable interpolation fails."""

    def __init__(self, message: str, key: Optional[str] = None):
        super().__init__(message)
        self.key = key


def interpolate(env: Dict[str, str], strict: bool = False) -> Dict[str, str]:
    """Interpolate variable references in env values.

    Args:
        env: Flat dict of resolved environment variables.
        strict: If True, raise InterpolationError for undefined references.
                If False, leave unresolved references as-is.

    Returns:
        New dict with interpolated values.

    Raises:
        InterpolationError: On circular reference or undefined var (strict mode).
    """
    result = dict(env)

    for key in result:
        result[key] = _resolve_value(key, result[key], result, strict, depth=0)

    return result


def _resolve_value(
    key: str,
    value: str,
    env: Dict[str, str],
    strict: bool,
    depth: int,
) -> str:
    if depth > _MAX_DEPTH:
        raise InterpolationError(
            f"Max interpolation depth exceeded for key '{key}'", key=key
        )

    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        if var_name in env:
            resolved = _resolve_value(var_name, env[var_name], env, strict, depth + 1)
            return resolved
        if strict:
            raise InterpolationError(
                f"Undefined variable '${var_name}' referenced in key '{key}'",
                key=key,
            )
        return match.group(0)

    return _PATTERN.sub(replacer, value)
