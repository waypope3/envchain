"""Fluent builder for constructing EnvChain instances."""
import os
from envchain.chain import EnvChain
from envchain.loader import load_from_env, load_from_json_file, load_from_dotenv
from envchain.exporter import (
    export_to_dict,
    export_to_json,
    export_to_dotenv,
    export_to_env,
    export_to_json_file,
)
from envchain.scoper import scope_env, unscope_env


class EnvChainBuilder:
    def __init__(self):
        self._chain = EnvChain()

    def add_env(self, prefix: str = "", strip_prefix: bool = True) -> "EnvChainBuilder":
        data = load_from_env(prefix=prefix, strip_prefix=strip_prefix)
        self._chain.add_layer(data)
        return self

    def add_dotenv(self, path: str) -> "EnvChainBuilder":
        data = load_from_dotenv(path)
        self._chain.add_layer(data)
        return self

    def add_json(self, path: str) -> "EnvChainBuilder":
        data = load_from_json_file(path)
        self._chain.add_layer(data)
        return self

    def add_dict(self, data: dict) -> "EnvChainBuilder":
        self._chain.add_layer(dict(data))
        return self

    def add_scoped(self, data: dict, scope: str) -> "EnvChainBuilder":
        """Add a dict whose keys will be prefixed with the given scope."""
        self._chain.add_layer(scope_env(data, scope))
        return self

    def resolve_scope(self, scope: str) -> dict:
        """Resolve the chain and return only keys matching the given scope (stripped)."""
        resolved = self._chain.resolve()
        return unscope_env(resolved, scope)

    def build(self) -> EnvChain:
        return self._chain

    def resolve(self) -> dict:
        return self._chain.resolve()

    # --- export shortcuts ---

    def to_dict(self) -> dict:
        return export_to_dict(self._chain.resolve())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self._chain.resolve(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self._chain.resolve())

    def to_env(self) -> None:
        export_to_env(self._chain.resolve())

    def to_json_file(self, path: str, indent: int = 2) -> None:
        export_to_json_file(self._chain.resolve(), path, indent=indent)
