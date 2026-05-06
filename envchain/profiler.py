"""Environment profile manager for named configuration sets."""

from typing import Dict, Optional


class ProfileError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EnvProfiler:
    """Manages named environment profiles for switching between configurations."""

    def __init__(self):
        self._profiles: Dict[str, Dict[str, str]] = {}
        self._active: Optional[str] = None

    def register(self, name: str, env: Dict[str, str]) -> None:
        """Register a named profile with a given environment dict."""
        if not name or not isinstance(name, str):
            raise ProfileError("Profile name must be a non-empty string.")
        self._profiles[name] = dict(env)

    def activate(self, name: str) -> None:
        """Set the active profile by name."""
        if name not in self._profiles:
            raise ProfileError(f"Profile '{name}' is not registered.")
        self._active = name

    def active_name(self) -> Optional[str]:
        """Return the name of the currently active profile."""
        return self._active

    def get_active(self) -> Dict[str, str]:
        """Return the active profile's environment dict."""
        if self._active is None:
            raise ProfileError("No active profile set.")
        return dict(self._profiles[self._active])

    def get(self, name: str) -> Dict[str, str]:
        """Return a copy of a named profile's environment dict."""
        if name not in self._profiles:
            raise ProfileError(f"Profile '{name}' is not registered.")
        return dict(self._profiles[name])

    def list_profiles(self):
        """Return a list of all registered profile names."""
        return list(self._profiles.keys())

    def deregister(self, name: str) -> None:
        """Remove a registered profile."""
        if name not in self._profiles:
            raise ProfileError(f"Profile '{name}' is not registered.")
        del self._profiles[name]
        if self._active == name:
            self._active = None

    def merge_into_active(self, overrides: Dict[str, str]) -> Dict[str, str]:
        """Return active profile merged with overrides (does not mutate stored profile)."""
        base = self.get_active()
        base.update(overrides)
        return base
