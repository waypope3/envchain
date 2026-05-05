"""Loaders for populating EnvChain layers from various sources."""

import json
import os
from pathlib import Path
from typing import Dict, Optional


def load_from_env(prefix: Optional[str] = None) -> Dict[str, str]:
    """Load variables from the current process environment.

    Args:
        prefix: If provided, only include variables starting with this prefix.
                The prefix is stripped from the resulting keys.

    Returns:
        A dict of environment variable key/value pairs.
    """
    env = dict(os.environ)
    if prefix is None:
        return env
    stripped = {}
    for key, value in env.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            stripped[new_key] = value
    return stripped


def load_from_json_file(path: str | Path) -> Dict[str, str]:
    """Load variables from a JSON file.

    The JSON file must be a flat object mapping string keys to string values.

    Args:
        path: Path to the JSON file.

    Returns:
        A dict of key/value pairs from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file content is not a flat JSON object.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}, got {type(data).__name__}")

    result: Dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise ValueError(f"All keys must be strings, got {type(key).__name__} for key {key!r}")
        result[key] = str(value)
    return result


def load_from_dotenv(path: str | Path) -> Dict[str, str]:
    """Load variables from a .env-style file.

    Supports KEY=VALUE lines. Lines starting with '#' and blank lines are ignored.
    Values may optionally be quoted with single or double quotes.

    Args:
        path: Path to the .env file.

    Returns:
        A dict of key/value pairs parsed from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")

    result: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            result[key] = value
    return result
