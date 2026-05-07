"""envchain.builder — Fluent builder for constructing layered EnvChain instances."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from envchain.chain import EnvChain
from envchain.exporter import (
    export_to_dict,
    export_to_dotenv,
    export_to_json,
    export_to_json_file,
)
from envchain.freezer import FrozenEnv, freeze
from envchain.loader import load_from_dotenv, load_from_env, load_from_json_file
from envchain.scoper import scope_env


class EnvChainBuilder:
    """Fluent builder that accumulates layers and produces an EnvChain."""

    def __init__(self) -> None:
        self._chain: EnvChain = EnvChain()

    # ------------------------------------------------------------------
    # Layer sources
    # ------------------------------------------------------------------

    def add_env(self, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer sourced from the current process environment."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(self, path: str, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer sourced from a .env file."""
        self._chain.add_layer(load_from_dotenv(path, prefix=prefix))
        return self

    def add_json(self, path: str) -> "EnvChainBuilder":
        """Add a layer sourced from a JSON file."""
        self._chain.add_layer(load_from_json_file(path))
        return self

    def add_dict(self, data: Dict[str, Any]) -> "EnvChainBuilder":
        """Add a layer from a plain dictionary."""
        self._chain.add_layer(dict(data))
        return self

    def add_scoped(
        self, data: Dict[str, Any], scope: str
    ) -> "EnvChainBuilder":
        """Add a layer whose keys are prefixed with *scope*."""
        self._chain.add_layer(scope_env(data, scope))
        return self

    # ------------------------------------------------------------------
    # Export shortcuts
    # ------------------------------------------------------------------

    def build(self) -> EnvChain:
        """Return the underlying EnvChain."""
        return self._chain

    def to_dict(self) -> Dict[str, Any]:
        return export_to_dict(self._chain.resolve())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self._chain.resolve(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self._chain.resolve())

    def to_json_file(self, path: str, indent: int = 2) -> None:
        export_to_json_file(self._chain.resolve(), path, indent=indent)

    def to_frozen(self) -> FrozenEnv:
        """Return the resolved environment as an immutable FrozenEnv."""
        return freeze(self._chain.resolve())

    def get(self, key: str, default: Any = None) -> Any:
        return self._chain.get(key, default)
