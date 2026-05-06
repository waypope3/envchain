"""Tests for envchain.profiler module."""

import pytest
from envchain.profiler import EnvProfiler, ProfileError


BASE_ENV = {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}
DEV_ENV = {"APP_ENV": "development", "DEBUG": "true", "PORT": "5000"}


class TestRegisterAndGet:
    def test_register_and_retrieve(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        assert p.get("prod") == BASE_ENV

    def test_get_returns_copy(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        result = p.get("prod")
        result["NEW_KEY"] = "val"
        assert "NEW_KEY" not in p.get("prod")

    def test_register_invalid_name_raises(self):
        p = EnvProfiler()
        with pytest.raises(ProfileError):
            p.register("", BASE_ENV)

    def test_get_unknown_profile_raises(self):
        p = EnvProfiler()
        with pytest.raises(ProfileError):
            p.get("nonexistent")

    def test_list_profiles_empty(self):
        p = EnvProfiler()
        assert p.list_profiles() == []

    def test_list_profiles_after_register(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        p.register("dev", DEV_ENV)
        assert set(p.list_profiles()) == {"prod", "dev"}


class TestActivate:
    def test_activate_sets_active(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        p.activate("prod")
        assert p.active_name() == "prod"

    def test_get_active_returns_correct_env(self):
        p = EnvProfiler()
        p.register("dev", DEV_ENV)
        p.activate("dev")
        assert p.get_active() == DEV_ENV

    def test_get_active_returns_copy(self):
        p = EnvProfiler()
        p.register("dev", DEV_ENV)
        p.activate("dev")
        result = p.get_active()
        result["EXTRA"] = "x"
        assert "EXTRA" not in p.get_active()

    def test_activate_unknown_raises(self):
        p = EnvProfiler()
        with pytest.raises(ProfileError):
            p.activate("ghost")

    def test_no_active_raises_on_get(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        with pytest.raises(ProfileError):
            p.get_active()


class TestDeregister:
    def test_deregister_removes_profile(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        p.deregister("prod")
        assert "prod" not in p.list_profiles()

    def test_deregister_clears_active(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        p.activate("prod")
        p.deregister("prod")
        assert p.active_name() is None

    def test_deregister_unknown_raises(self):
        p = EnvProfiler()
        with pytest.raises(ProfileError):
            p.deregister("missing")


class TestMergeIntoActive:
    def test_merge_applies_overrides(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        p.activate("prod")
        result = p.merge_into_active({"PORT": "9000", "EXTRA": "yes"})
        assert result["PORT"] == "9000"
        assert result["EXTRA"] == "yes"
        assert result["APP_ENV"] == "production"

    def test_merge_does_not_mutate_stored(self):
        p = EnvProfiler()
        p.register("prod", BASE_ENV)
        p.activate("prod")
        p.merge_into_active({"PORT": "9999"})
        assert p.get_active()["PORT"] == "8080"
