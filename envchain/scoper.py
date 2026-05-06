"""Scope-based env variable namespacing for envchain."""


class ScopeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def scope_env(env: dict, scope: str, separator: str = "__") -> dict:
    """Prefix all keys in env with the given scope."""
    if not scope:
        raise ScopeError("Scope name must not be empty.")
    if not isinstance(env, dict):
        raise ScopeError("env must be a dict.")
    prefix = scope.upper() + separator
    return {prefix + k: v for k, v in env.items()}


def unscope_env(env: dict, scope: str, separator: str = "__") -> dict:
    """Strip scope prefix from matching keys; non-matching keys are dropped."""
    if not scope:
        raise ScopeError("Scope name must not be empty.")
    if not isinstance(env, dict):
        raise ScopeError("env must be a dict.")
    prefix = scope.upper() + separator
    return {k[len(prefix):]: v for k, v in env.items() if k.startswith(prefix)}


def extract_scopes(env: dict, separator: str = "__") -> dict:
    """Group env keys by their scope prefix.

    Returns a dict mapping scope -> {stripped_key: value}.
    Keys without a separator are placed under the empty string scope.
    """
    result: dict = {}
    for k, v in env.items():
        if separator in k:
            scope, _, rest = k.partition(separator)
            result.setdefault(scope, {})[rest] = v
        else:
            result.setdefault("", {})[k] = v
    return result


def merge_scopes(scoped: dict, separator: str = "__") -> dict:
    """Flatten a scope -> env mapping back into a single namespaced dict."""
    result = {}
    for scope, env in scoped.items():
        if scope:
            result.update(scope_env(env, scope, separator))
        else:
            result.update(env)
    return result
