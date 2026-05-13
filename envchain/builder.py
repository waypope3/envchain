"""EnvChainBuilder: fluent interface for assembling and exporting env chains."""

from typing import Any, Dict, Optional

from envchain.chain import EnvChain
from envchain.loader import load_from_env, load_from_json_file, load_from_dotenv
from envchain.exporter import (
    export_to_dict,
    export_to_json,
    export_to_dotenv,
    export_to_env,
    export_to_json_file,
)
from envchain.scoper import scope_env
from envchain.aliaser import apply_aliases


class EnvChainBuilder:
    """Fluent builder for constructing an EnvChain from multiple sources."""

    def __init__(self) -> None:
        self._chain = EnvChain()

    # ------------------------------------------------------------------
    # Layer addition
    # ------------------------------------------------------------------

    def add_layer(self, data: Dict[str, Any]) -> "EnvChainBuilder":
        """Add a plain dict as a layer."""
        self._chain.add_layer(data)
        return self

    def add_env(self, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add current process environment (optionally filtered by prefix)."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(
        self, path: str, prefix: Optional[str] = None
    ) -> "EnvChainBuilder":
        """Add variables from a .env file."""
        self._chain.add_layer(load_from_dotenv(path, prefix=prefix))
        return self

    def add_json(
        self, path: str, prefix: Optional[str] = None
    ) -> "EnvChainBuilder":
        """Add variables from a JSON file."""
        self._chain.add_layer(load_from_json_file(path, prefix=prefix))
        return self

    def add_scoped(
        self, data: Dict[str, Any], scope: str
    ) -> "EnvChainBuilder":
        """Add a dict as a layer, prefixing all keys with *scope*."""
        self._chain.add_layer(scope_env(data, scope))
        return self

    def add_aliased(
        self,
        data: Dict[str, Any],
        aliases: Dict[str, str],
        *,
        keep_original: bool = True,
        missing_ok: bool = False,
    ) -> "EnvChainBuilder":
        """Add a dict layer after applying key aliases."""
        aliased = apply_aliases(
            data, aliases, keep_original=keep_original, missing_ok=missing_ok
        )
        self._chain.add_layer(aliased)
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> EnvChain:
        """Return the underlying EnvChain instance."""
        return self._chain

    # ------------------------------------------------------------------
    # Export shortcuts
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return export_to_dict(self._chain.resolve())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self._chain.resolve(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self._chain.resolve())

    def to_env(self) -> None:
        export_to_env(self._chain.resolve())

    def to_json_file(self, path: str, indent: int = 2) -> None:
        export_to_json_file(self._chain.resolve(), path, indent=indent)
