"""Export resolved env chains to various formats."""

import json
import os
from typing import Dict, Optional


def export_to_dict(resolved: Dict[str, str]) -> Dict[str, str]:
    """Return a plain copy of the resolved environment dict."""
    return dict(resolved)


def export_to_json(resolved: Dict[str, str], indent: int = 2) -> str:
    """Serialize resolved env vars to a JSON string."""
    return json.dumps(resolved, indent=indent, sort_keys=True)


def export_to_dotenv(resolved: Dict[str, str]) -> str:
    """Serialize resolved env vars to .env file format.

    Values containing whitespace or special characters are quoted.
    """
    lines = []
    for key in sorted(resolved):
        value = resolved[key]
        # Quote value if it contains spaces, quotes, or shell-special chars
        if any(ch in value for ch in (' ', '"', "'", '$', '\\', '\n')):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f'{key}={value}')
    return '\n'.join(lines)


def export_to_env(resolved: Dict[str, str], prefix: Optional[str] = None) -> None:
    """Inject resolved vars into the current process environment.

    Args:
        resolved: Dict of env vars to inject.
        prefix:   Optional prefix to prepend to every key before setting.
    """
    for key, value in resolved.items():
        env_key = f"{prefix}{key}" if prefix else key
        os.environ[env_key] = value


def export_to_json_file(resolved: Dict[str, str], path: str, indent: int = 2) -> None:
    """Write resolved env vars as JSON to *path*."""
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(resolved, fh, indent=indent, sort_keys=True)


def export_to_dotenv_file(resolved: Dict[str, str], path: str) -> None:
    """Write resolved env vars in .env format to *path*."""
    content = export_to_dotenv(resolved)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(content)
        if content:
            fh.write('\n')
