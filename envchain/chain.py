"""Core environment variable chaining and inheritance logic."""

from __future__ import annotations

from typing import Dict, List, Optional


class EnvChain:
    """Manages layered environment variable inheritance across deployment stages."""

    def __init__(self, base: Optional[Dict[str, str]] = None) -> None:
        self._layers: List[Dict[str, str]] = []
        if base:
            self._layers.append(dict(base))

    def add_layer(self, env: Dict[str, str]) -> "EnvChain":
        """Push a new environment layer on top of the chain.

        Later layers override earlier ones for the same key.

        Args:
            env: Mapping of variable names to values.

        Returns:
            self, to allow fluent chaining.
        """
        self._layers.append(dict(env))
        return self

    def resolve(self) -> Dict[str, str]:
        """Merge all layers and return the final resolved environment.

        Keys defined in higher layers take precedence over lower ones.

        Returns:
            A single flat dictionary with all resolved variables.
        """
        merged: Dict[str, str] = {}
        for layer in self._layers:
            merged.update(layer)
        return merged

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a single resolved variable by key.

        Args:
            key: The variable name to look up.
            default: Value returned when the key is absent.

        Returns:
            The resolved value or *default*.
        """
        return self.resolve().get(key, default)

    def stage(self, name: str, overrides: Dict[str, str]) -> "EnvChain":
        """Create a child EnvChain for a named deployment stage.

        The child inherits the current resolved state and applies *overrides*
        on top without mutating the parent chain.

        Args:
            name: Human-readable stage identifier (e.g. 'production').
            overrides: Stage-specific variable overrides.

        Returns:
            A new EnvChain representing the stage environment.
        """
        child = EnvChain(self.resolve())
        child.add_layer(overrides)
        child._stage_name = name  # type: ignore[attr-defined]
        return child

    @property
    def layer_count(self) -> int:
        """Number of layers currently in the chain."""
        return len(self._layers)

    def __repr__(self) -> str:  # pragma: no cover
        stage = getattr(self, "_stage_name", "<root>")
        return f"EnvChain(stage={stage!r}, layers={self.layer_count})"
