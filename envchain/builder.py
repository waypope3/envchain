"""Builder module for constructing EnvChain instances fluently."""

from envchain.chain import EnvChain
from envchain.loader import load_from_env, load_from_json_file, load_from_dotenv
from envchain.exporter import (
    export_to_dict,
    export_to_json,
    export_to_dotenv,
    export_to_env,
    export_to_json_file,
)
from envchain.snapshot import create_snapshot, restore_snapshot


class EnvChainBuilder:
    """Fluent builder for assembling layered env chains."""

    def __init__(self):
        self._chain = EnvChain()
        self._snapshots: dict = {}

    def add_env(self, prefix: str = "") -> "EnvChainBuilder":
        """Add a layer loaded from OS environment variables."""
        self._chain.add_layer(load_from_env(prefix=prefix))
        return self

    def add_dotenv(self, path: str) -> "EnvChainBuilder":
        """Add a layer loaded from a .env file."""
        self._chain.add_layer(load_from_dotenv(path))
        return self

    def add_json(self, path: str) -> "EnvChainBuilder":
        """Add a layer loaded from a JSON file."""
        self._chain.add_layer(load_from_json_file(path))
        return self

    def add_dict(self, data: dict) -> "EnvChainBuilder":
        """Add a layer from a plain dict."""
        self._chain.add_layer(data)
        return self

    def snapshot(self, label: str = "") -> "EnvChainBuilder":
        """Save the current resolved state as a named snapshot."""
        key = label or f"_snap_{len(self._snapshots)}"
        self._snapshots[key] = create_snapshot(self._chain.resolve(), label=label)
        return self

    def restore(self, label: str) -> "EnvChainBuilder":
        """Replace current chain with a previously saved snapshot."""
        if label not in self._snapshots:
            raise KeyError(f"No snapshot found with label '{label}'.")
        data = restore_snapshot(self._snapshots[label])
        self._chain = EnvChain()
        self._chain.add_layer(data)
        return self

    def build(self) -> EnvChain:
        """Return the assembled EnvChain."""
        return self._chain

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

    def get(self, key: str, default=None):
        return self._chain.get(key, default)
