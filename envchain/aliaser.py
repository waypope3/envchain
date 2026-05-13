"""Aliaser: map environment variable keys to alternate names."""

from typing import Dict, List, Optional


class AliasError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def apply_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
    *,
    keep_original: bool = True,
    missing_ok: bool = False,
) -> Dict[str, str]:
    """Return a new dict with alias keys added (or replacing originals).

    Args:
        env: Source environment dict.
        aliases: Mapping of {original_key: alias_key}.
        keep_original: If True, keep the original key alongside the alias.
        missing_ok: If False, raise AliasError when an original key is absent.

    Returns:
        New dict with aliases applied.
    """
    result = dict(env)
    for original, alias in aliases.items():
        if not isinstance(alias, str) or not alias:
            raise AliasError(f"Alias name must be a non-empty string, got: {alias!r}")
        if original not in env:
            if missing_ok:
                continue
            raise AliasError(f"Key {original!r} not found in env")
        result[alias] = env[original]
        if not keep_original:
            result.pop(original, None)
    return result


def invert_aliases(aliases: Dict[str, str]) -> Dict[str, str]:
    """Invert an alias mapping: {original: alias} -> {alias: original}.

    Raises AliasError on duplicate alias values.
    """
    inverted: Dict[str, str] = {}
    for original, alias in aliases.items():
        if alias in inverted:
            raise AliasError(
                f"Duplicate alias target {alias!r} for keys "
                f"{inverted[alias]!r} and {original!r}"
            )
        inverted[alias] = original
    return inverted


def list_aliases(aliases: Dict[str, str]) -> List[str]:
    """Return a sorted list of all alias (target) names."""
    return sorted(aliases.values())
