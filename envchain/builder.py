"""Fluent builder for constructing layered EnvChain instances."""

from typing import Any, Dict, List, Optional

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
from envchain.comparator import compare_envs
from envchain.grouper import (
    group_by_prefix,
    group_by_mapping,
    group_by_predicate,
)
from typing import Callable


class EnvChainBuilder:
    """Fluent builder that accumulates layers and resolves them via EnvChain."""

    def __init__(self) -> None:
        self._chain: EnvChain = EnvChain()

    # ------------------------------------------------------------------
    # Layer additions
    # ------------------------------------------------------------------

    def add_env(self, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer sourced from the current process environment."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(self, path: str, prefix: Optional[str] = None) -> "EnvChainBuilder":
        """Add a layer sourced from a .env file."""
        data = load_from_dotenv(path)
        if prefix:
            data = {k: v for k, v in data.items() if k.startswith(prefix)}
        self._chain.add_layer(data)
        return self

    def add_json(self, path: str) -> "EnvChainBuilder":
        """Add a layer sourced from a JSON file."""
        self._chain.add_layer(load_from_json_file(path))
        return self

    def add_dict(self, data: Dict[str, str]) -> "EnvChainBuilder":
        """Add an explicit dict as a layer."""
        self._chain.add_layer(dict(data))
        return self

    def add_scoped(self, env: Dict[str, str], scope: str) -> "EnvChainBuilder":
        """Add a layer where all keys are prefixed with *scope*."""
        self._chain.add_layer(scope_env(env, scope))
        return self

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def build(self) -> Dict[str, str]:
        """Resolve all layers and return the merged dict."""
        return self._chain.resolve()

    # ------------------------------------------------------------------
    # Export shortcuts
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, str]:
        return export_to_dict(self.build())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self.build(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self.build())

    def to_env_commands(self) -> List[str]:
        return export_to_env(self.build())

    def to_json_file(self, path: str, indent: int = 2) -> None:
        export_to_json_file(self.build(), path, indent=indent)

    # ------------------------------------------------------------------
    # Comparison shortcut
    # ------------------------------------------------------------------

    def compare_with(self, other: "EnvChainBuilder"):
        return compare_envs(self.build(), other.build())

    # ------------------------------------------------------------------
    # Grouping shortcuts
    # ------------------------------------------------------------------

    def group_by_prefix(self, separator: str = "_", lowercase_groups: bool = False):
        return group_by_prefix(self.build(), separator=separator, lowercase_groups=lowercase_groups)

    def group_by_mapping(self, mapping: Dict[str, List[str]], include_unmatched: bool = False):
        return group_by_mapping(self.build(), mapping, include_unmatched=include_unmatched)

    def group_by_predicate(self, predicates: Dict[str, Callable], include_unmatched: bool = False):
        return group_by_predicate(self.build(), predicates, include_unmatched=include_unmatched)
