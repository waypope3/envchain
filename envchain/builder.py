"""EnvChainBuilder: fluent builder for constructing layered env chains."""

from __future__ import annotations

import json
from typing import Any

from envchain.chain import EnvChain
from envchain.loader import load_from_dotenv, load_from_env, load_from_json_file
from envchain.exporter import (
    export_to_dict,
    export_to_dotenv,
    export_to_json,
    export_to_json_file,
)
from envchain.scoper import scope_env
from envchain.trimmer import trim_env


class EnvChainBuilder:
    """Fluent builder that accumulates layers into an EnvChain."""

    def __init__(self) -> None:
        self._chain: EnvChain = EnvChain()

    # ------------------------------------------------------------------
    # Layer sources
    # ------------------------------------------------------------------

    def add_layer(self, data: dict[str, str]) -> "EnvChainBuilder":
        """Add a plain dict as a layer."""
        self._chain.add_layer(data)
        return self

    def add_env(self, prefix: str = "") -> "EnvChainBuilder":
        """Add current process environment (optionally filtered by prefix)."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(self, path: str) -> "EnvChainBuilder":
        """Add a .env file as a layer."""
        self._chain.add_layer(load_from_dotenv(path))
        return self

    def add_json_file(self, path: str) -> "EnvChainBuilder":
        """Add a JSON file as a layer."""
        self._chain.add_layer(load_from_json_file(path))
        return self

    def add_scoped(self, scope: str, data: dict[str, str]) -> "EnvChainBuilder":
        """Add a dict as a layer with keys prefixed by *scope*."""
        self._chain.add_layer(scope_env(data, scope))
        return self

    def add_trimmed(self, data: dict[str, str], *, normalize_keys: bool = False) -> "EnvChainBuilder":
        """Add a layer after trimming all keys and values."""
        self._chain.add_layer(trim_env(data, normalize_keys=normalize_keys))
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> dict[str, str]:
        """Resolve all layers and return the merged dict."""
        return self._chain.resolve()

    # ------------------------------------------------------------------
    # Export shortcuts
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        return export_to_dict(self.build())

    def to_json(self, *, indent: int = 2) -> str:
        return export_to_json(self.build(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self.build())

    def to_json_file(self, path: str, *, indent: int = 2) -> None:
        export_to_json_file(self.build(), path, indent=indent)

    def to_env(self) -> None:
        from envchain.exporter import export_to_env
        export_to_env(self.build())

    # ------------------------------------------------------------------
    # Chain access
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        return self._chain.get(key, default)

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvChainBuilder(layers={len(self._chain._layers)})"
