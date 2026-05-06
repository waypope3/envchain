"""Fluent builder for constructing EnvChain instances from multiple sources."""

from typing import Optional, Dict, Any
from envchain.chain import EnvChain
from envchain.loader import load_from_env, load_from_dotenv, load_from_json_file
from envchain.exporter import export_to_dict, export_to_json, export_to_dotenv
from envchain.scoper import scope_env
from envchain.renderer import render_dict


class EnvChainBuilder:
    """Fluent builder that accumulates layers into an EnvChain."""

    def __init__(self):
        self._chain = EnvChain()

    def add_env(self, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer loaded from the current process environment."""
        data = load_from_env(prefix=prefix)
        self._chain.add_layer(data)
        return self

    def add_dotenv(self, path: str, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer loaded from a .env file."""
        data = load_from_dotenv(path, prefix=prefix)
        self._chain.add_layer(data)
        return self

    def add_json(self, path: str, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer loaded from a JSON file."""
        data = load_from_json_file(path, prefix=prefix)
        self._chain.add_layer(data)
        return self

    def add_dict(self, data: Dict[str, Any]) -> "EnvChainBuilder":
        """Add a layer from a plain dictionary."""
        self._chain.add_layer(dict(data))
        return self

    def add_scoped(self, data: Dict[str, Any], scope: str) -> "EnvChainBuilder":
        """Add a layer from a dict, prefixing all keys with the given scope."""
        scoped = scope_env(data, scope)
        self._chain.add_layer(scoped)
        return self

    def add_rendered(self, templates: Dict[str, str], strict: bool = True) -> "EnvChainBuilder":
        """Render a dict of templates against the current resolved env and add as a layer.

        This allows derived values to be computed from already-accumulated layers.
        """
        current = self._chain.resolve()
        rendered = render_dict(templates, current, strict=strict)
        self._chain.add_layer(rendered)
        return self

    def build(self) -> EnvChain:
        """Return the constructed EnvChain."""
        return self._chain

    def resolve(self) -> Dict[str, Any]:
        """Resolve and return the merged environment dict."""
        return self._chain.resolve()

    def to_dict(self) -> Dict[str, Any]:
        return export_to_dict(self._chain.resolve())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self._chain.resolve(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self._chain.resolve())
