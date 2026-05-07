"""EnvChainBuilder: fluent builder for constructing and exporting env chains."""

from typing import Any, Dict, Optional

from envchain.chain import EnvChain
from envchain.loader import load_from_env, load_from_dotenv, load_from_json_file
from envchain.exporter import (
    export_to_dict,
    export_to_json,
    export_to_dotenv,
    export_to_env,
    export_to_json_file,
)
from envchain.scoper import scope_env
from envchain.pipeline import EnvPipeline


class EnvChainBuilder:
    """Fluent builder for layered env resolution with optional pipeline processing."""

    def __init__(self):
        self._chain = EnvChain()
        self._pipeline: Optional[EnvPipeline] = None

    def add_env(self, prefix: str = "") -> "EnvChainBuilder":
        """Add a layer loaded from the current process environment."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(self, path: str, prefix: str = "") -> "EnvChainBuilder":
        """Add a layer loaded from a .env file."""
        self._chain.add_layer(load_from_dotenv(path, prefix=prefix))
        return self

    def add_json(self, path: str, prefix: str = "") -> "EnvChainBuilder":
        """Add a layer loaded from a JSON file."""
        self._chain.add_layer(load_from_json_file(path, prefix=prefix))
        return self

    def add_dict(self, data: Dict[str, Any]) -> "EnvChainBuilder":
        """Add a layer from a plain dict."""
        self._chain.add_layer(dict(data))
        return self

    def add_scoped(self, scope: str, data: Dict[str, Any]) -> "EnvChainBuilder":
        """Add a layer with all keys prefixed by the given scope."""
        self._chain.add_layer(scope_env(data, scope))
        return self

    def set_pipeline(self, pipeline: EnvPipeline) -> "EnvChainBuilder":
        """Attach a processing pipeline applied during resolution."""
        self._pipeline = pipeline
        return self

    def build(self) -> Dict[str, Any]:
        """Resolve all layers and run through the pipeline if set."""
        resolved = self._chain.resolve()
        if self._pipeline is not None:
            resolved = self._pipeline.run(resolved)
        return resolved

    def get(self, key: str, default: Any = None) -> Any:
        """Resolve and return a single key."""
        return self.build().get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return export_to_dict(self.build())

    def to_json(self, indent: int = 2) -> str:
        return export_to_json(self.build(), indent=indent)

    def to_dotenv(self) -> str:
        return export_to_dotenv(self.build())

    def to_env(self) -> None:
        export_to_env(self.build())

    def to_json_file(self, path: str, indent: int = 2) -> None:
        export_to_json_file(self.build(), path, indent=indent)
