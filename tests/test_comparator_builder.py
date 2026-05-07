"""Integration tests: EnvChainBuilder -> compare_envs -> render_text_report."""

from envchain.builder import EnvChainBuilder
from envchain.comparator import compare_envs
from envchain.reporter import render_text_report


class TestBuilderComparatorIntegration:
    def _build(self, layers: list) -> dict:
        builder = EnvChainBuilder()
        for layer in layers:
            builder.add_dict(layer)
        return builder.build().resolve()

    def test_two_builds_identical_no_diff(self):
        env_a = self._build([{"APP": "prod", "DB": "main"}])
        env_b = self._build([{"APP": "prod", "DB": "main"}])
        result = compare_envs(env_a, env_b)
        assert not result.has_differences

    def test_added_layer_shows_new_keys(self):
        env_a = self._build([{"APP": "prod"}])
        env_b = self._build([{"APP": "prod"}, {"FEATURE_X": "on"}])
        result = compare_envs(env_a, env_b)
        assert "FEATURE_X" in result.added

    def test_override_layer_shows_changed_key(self):
        env_a = self._build([{"LEVEL": "info"}])
        env_b = self._build([{"LEVEL": "info"}, {"LEVEL": "debug"}])
        result = compare_envs(env_a, env_b)
        assert "LEVEL" in result.changed
        assert result.changed["LEVEL"] == ("info", "debug")

    def test_report_generated_from_builder_output(self):
        env_a = self._build([{"HOST": "localhost"}])
        env_b = self._build([{"HOST": "remotehost", "PORT": "5432"}])
        result = compare_envs(env_a, env_b)
        report = render_text_report(result)
        assert "HOST" in report
        assert "PORT" in report

    def test_empty_before_full_after_all_added(self):
        env_a = self._build([])
        env_b = self._build([{"A": "1", "B": "2"}])
        result = compare_envs(env_a, env_b)
        assert set(result.added.keys()) == {"A", "B"}
        assert not result.removed
        assert not result.changed
