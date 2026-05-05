"""Fluent builder for constructing and exporting EnvChain instances."""

from typing import Dict, Optional

from envchain.chain import EnvChain
from envchain.loader import load_from_dotenv, load_from_env, load_from_json_file
from envchain.exporter import (
    export_to_dict,
    export_to_dotenv,
    export_to_dotenv_file,
    export_to_env,
    export_to_json,
    export_to_json_file,
)


class EnvChainBuilder:
    """Fluent builder that layers env sources and resolves them.

    Example::

        chain = (
            EnvChainBuilder()
            .add_dotenv('.env')
            .add_dotenv('.env.production')
            .add_env(prefix='APP_')
            .build()
        )
    """

    def __init__(self) -> None:
        self._chain = EnvChain()

    # ------------------------------------------------------------------
    # Layer helpers
    # ------------------------------------------------------------------

    def add_env(self, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add current process environment as a layer."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(self, path: str) -> "EnvChainBuilder":
        """Add a .env file as a layer (missing files are silently skipped)."""
        try:
            self._chain.add_layer(load_from_dotenv(path))
        except FileNotFoundError:
            pass
        return self

    def add_json(self, path: str) -> "EnvChainBuilder":
        """Add a JSON file as a layer (missing files are silently skipped)."""
        try:
            self._chain.add_layer(load_from_json_file(path))
        except FileNotFoundError:
            pass
        return self

    def add_dict(self, data: Dict[str, str]) -> "EnvChainBuilder":
        """Add an explicit dict as a layer."""
        self._chain.add_layer(data)
        return self

    # ------------------------------------------------------------------
    # Terminal operations
    # ------------------------------------------------------------------

    def build(self) -> EnvChain:
        """Return the underlying :class:`EnvChain` instance."""
        return self._chain

    def resolve(self) -> Dict[str, str]:
        """Resolve all layers and return the merged dict."""
        return self._chain.resolve()

    # ------------------------------------------------------------------
    # Export shortcuts
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, str]:
        return export_to_dict(self.resolve())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self.resolve(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self.resolve())

    def to_env(self, prefix: Optional[str] = None) -> None:
        export_to_env(self.resolve(), prefix=prefix)

    def to_json_file(self, path: str, indent: int = 2) -> None:
        export_to_json_file(self.resolve(), path, indent=indent)

    def to_dotenv_file(self, path: str) -> None:
        export_to_dotenv_file(self.resolve(), path)
