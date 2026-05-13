"""envchain.stacker — Named stack management for layered env snapshots."""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional


class StackError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class EnvStack:
    """Manages a named, ordered stack of env dicts for push/pop workflows."""

    def __init__(self, name: str = "default") -> None:
        if not name or not isinstance(name, str):
            raise StackError("Stack name must be a non-empty string.")
        self._name = name
        self._stack: List[Dict[str, str]] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def depth(self) -> int:
        return len(self._stack)

    def push(self, env: Dict[str, str]) -> None:
        """Push a copy of env onto the stack."""
        if not isinstance(env, dict):
            raise StackError("env must be a dict.")
        self._stack.append(deepcopy(env))

    def pop(self) -> Dict[str, str]:
        """Remove and return the top env from the stack."""
        if not self._stack:
            raise StackError("Cannot pop from an empty stack.")
        return self._stack.pop()

    def peek(self) -> Dict[str, str]:
        """Return the top env without removing it."""
        if not self._stack:
            raise StackError("Cannot peek an empty stack.")
        return deepcopy(self._stack[-1])

    def merged(self) -> Dict[str, str]:
        """Return a single dict merged from bottom to top (top wins)."""
        result: Dict[str, str] = {}
        for layer in self._stack:
            result.update(layer)
        return result

    def clear(self) -> None:
        """Remove all layers from the stack."""
        self._stack.clear()

    def labels(self) -> List[int]:
        """Return indices of all layers (0 = bottom)."""
        return list(range(len(self._stack)))

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvStack(name={self._name!r}, depth={self.depth})"
