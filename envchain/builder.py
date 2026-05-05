"""Fluent builder for constructing EnvChain instances from multiple sources."""

from typing import Any, Dict, List, Optional

from envchain.chain import EnvChain
from envchain.loader import load_from_env, load_from_dotenv, load_from_json_file
from envchain.exporter import export_to_dict, export_to_json, export_to_dotenv
from envchain.merger import apply_merge, get_strategy


class EnvChainBuilder:
    """Fluent builder that assembles an EnvChain from layered sources."""

    def __init__(self, merge_strategy: str = "replace"):
        self._chain = EnvChain()
        self._layers: List[Dict[str, Any]] = []
        get_strategy(merge_strategy)  # validate early
        self._merge_strategy = merge_strategy

    def add_env(self, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Load variables from the current OS environment."""
        layer = load_from_env(prefix=prefix)
        self._layers.append(layer)
        self._chain.add_layer(layer)
        return self

    def add_dotenv(self, path: str, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Load variables from a .env file."""
        layer = load_from_dotenv(path, prefix=prefix)
        self._layers.append(layer)
        self._chain.add_layer(layer)
        return self

    def add_json(self, path: str, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Load variables from a JSON file."""
        layer = load_from_json_file(path, prefix=prefix)
        self._layers.append(layer)
        self._chain.add_layer(layer)
        return self

    def add_dict(self, data: Dict[str, Any]) -> "EnvChainBuilder":
        """Add a raw dictionary as a layer."""
        layer = dict(data)
        self._layers.append(layer)
        self._chain.add_layer(layer)
        return self

    def set_merge_strategy(self, strategy: str) -> "EnvChainBuilder":
        """Change the merge strategy (validated immediately)."""
        get_strategy(strategy)
        self._merge_strategy = strategy
        return self

    def build(self) -> EnvChain:
        """Return the assembled EnvChain."""
        return self._chain

    def resolve(self) -> Dict[str, Any]:
        """Resolve all layers using the configured merge strategy."""
        return apply_merge(self._layers, strategy=self._merge_strategy)

    # --- Export shortcuts ---

    def to_dict(self) -> Dict[str, Any]:
        return export_to_dict(self.resolve())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self.resolve(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self.resolve())

    def to_env(self, prefix: str = "") -> None:
        """Export resolved variables into the current process environment."""
        import os
        for key, value in self.resolve().items():
            os.environ[f"{prefix}{key}"] = str(value)

    def layer_count(self) -> int:
        return len(self._layers)

    def __repr__(self) -> str:
        return (
            f"EnvChainBuilder(layers={self.layer_count()}, "
            f"strategy={self._merge_strategy!r})"
        )
