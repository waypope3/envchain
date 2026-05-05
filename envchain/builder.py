"""Convenience builder that wires loaders directly into an EnvChain."""

from pathlib import Path
from typing import Optional

from .chain import EnvChain
from .loader import load_from_dotenv, load_from_env, load_from_json_file


class EnvChainBuilder:
    """Fluent builder for constructing an :class:`EnvChain` from multiple sources.

    Example::

        chain = (
            EnvChainBuilder()
            .add_dotenv(".env")
            .add_dotenv(".env.production")
            .add_env(prefix="APP_")
            .build()
        )
        value = chain.get("DATABASE_URL")
    """

    def __init__(self) -> None:
        self._chain = EnvChain()

    def add_env(self, prefix: Optional[str] = None, name: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer sourced from the current process environment.

        Args:
            prefix: Optional prefix to filter and strip from variable names.
            name: Optional label for this layer (for debugging).

        Returns:
            self, for chaining.
        """
        layer = load_from_env(prefix=prefix)
        self._chain.add_layer(layer, name=name or f"env(prefix={prefix!r})")
        return self

    def add_dotenv(
        self,
        path: str | Path,
        *,
        missing_ok: bool = False,
        name: Optional[str] = None,
    ) -> "EnvChainBuilder":
        """Add a layer sourced from a .env file.

        Args:
            path: Path to the .env file.
            missing_ok: If True, silently skip missing files instead of raising.
            name: Optional label for this layer.

        Returns:
            self, for chaining.
        """
        try:
            layer = load_from_dotenv(path)
        except FileNotFoundError:
            if missing_ok:
                return self
            raise
        self._chain.add_layer(layer, name=name or str(path))
        return self

    def add_json(
        self,
        path: str | Path,
        *,
        missing_ok: bool = False,
        name: Optional[str] = None,
    ) -> "EnvChainBuilder":
        """Add a layer sourced from a JSON file.

        Args:
            path: Path to the JSON file.
            missing_ok: If True, silently skip missing files instead of raising.
            name: Optional label for this layer.

        Returns:
            self, for chaining.
        """
        try:
            layer = load_from_json_file(path)
        except FileNotFoundError:
            if missing_ok:
                return self
            raise
        self._chain.add_layer(layer, name=name or str(path))
        return self

    def build(self) -> EnvChain:
        """Return the fully configured :class:`EnvChain`."""
        return self._chain
