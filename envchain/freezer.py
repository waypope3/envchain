"""envchain.freezer — Freeze and unfreeze env snapshots to prevent accidental mutation."""

from __future__ import annotations

from typing import Any, Dict, Iterator


class FreezeError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class FrozenEnv:
    """An immutable view over an environment dictionary."""

    def __init__(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise FreezeError("data must be a dict")
        object.__setattr__(self, "_data", dict(data))

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __setattr__(self, name: str, value: Any) -> None:
        raise FreezeError("FrozenEnv is immutable; use unfreeze() to get a mutable copy")

    def __delattr__(self, name: str) -> None:
        raise FreezeError("FrozenEnv is immutable; use unfreeze() to get a mutable copy")

    def __repr__(self) -> str:
        return f"FrozenEnv({self._data!r})"

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


def freeze(env: Dict[str, Any]) -> FrozenEnv:
    """Return an immutable FrozenEnv from a plain dict."""
    if not isinstance(env, dict):
        raise FreezeError(f"Expected dict, got {type(env).__name__}")
    return FrozenEnv(env)


def unfreeze(frozen: FrozenEnv) -> Dict[str, Any]:
    """Return a mutable copy of the underlying data from a FrozenEnv."""
    if not isinstance(frozen, FrozenEnv):
        raise FreezeError(f"Expected FrozenEnv, got {type(frozen).__name__}")
    return dict(object.__getattribute__(frozen, "_data"))
