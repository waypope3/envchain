"""Tests for envchain.pipeline."""

import pytest
from envchain.pipeline import EnvPipeline, PipelineError


class TestEnvPipelineBasic:
    def test_empty_pipeline_returns_copy(self):
        p = EnvPipeline()
        env = {"A": "1"}
        result = p.run(env)
        assert result == env
        assert result is not env

    def test_single_step_applied(self):
        p = EnvPipeline()
        p.add_step("upper", lambda e: {k: v.upper() for k, v in e.items()})
        result = p.run({"key": "hello"})
        assert result == {"key": "HELLO"}

    def test_multiple_steps_applied_in_order(self):
        p = EnvPipeline()
        p.add_step("add_x", lambda e: {**e, "X": "x"})
        p.add_step("add_y", lambda e: {**e, "Y": "y"})
        result = p.run({})
        assert result == {"X": "x", "Y": "y"}

    def test_step_receives_previous_output(self):
        p = EnvPipeline()
        p.add_step("set_a", lambda e: {**e, "A": "1"})
        p.add_step("double_a", lambda e: {**e, "A": e["A"] * 2})
        result = p.run({})
        assert result["A"] == "11"

    def test_original_env_not_mutated(self):
        p = EnvPipeline()
        p.add_step("pop", lambda e: {})
        env = {"KEY": "val"}
        p.run(env)
        assert env == {"KEY": "val"}


class TestEnvPipelineErrors:
    def test_non_callable_step_raises(self):
        p = EnvPipeline()
        with pytest.raises(PipelineError):
            p.add_step("bad", "not_a_function")  # type: ignore

    def test_empty_name_raises(self):
        p = EnvPipeline()
        with pytest.raises(PipelineError):
            p.add_step("", lambda e: e)

    def test_step_returning_non_dict_raises(self):
        p = EnvPipeline()
        p.add_step("bad_return", lambda e: [1, 2, 3])  # type: ignore
        with pytest.raises(PipelineError) as exc_info:
            p.run({})
        assert "bad_return" in str(exc_info.value)

    def test_step_raising_exception_wrapped(self):
        def boom(e):
            raise ValueError("something broke")

        p = EnvPipeline()
        p.add_step("exploder", boom)
        with pytest.raises(PipelineError) as exc_info:
            p.run({})
        assert "exploder" in str(exc_info.value)
        assert "something broke" in str(exc_info.value)


class TestRunPartial:
    def test_stops_at_named_step(self):
        p = EnvPipeline()
        p.add_step("first", lambda e: {**e, "A": "1"})
        p.add_step("second", lambda e: {**e, "B": "2"})
        p.add_step("third", lambda e: {**e, "C": "3"})
        result = p.run_partial({}, "second")
        assert "A" in result
        assert "B" in result
        assert "C" not in result

    def test_unknown_step_raises(self):
        p = EnvPipeline()
        p.add_step("only", lambda e: e)
        with pytest.raises(PipelineError):
            p.run_partial({}, "missing")


class TestPipelineUtils:
    def test_step_names_returns_ordered_list(self):
        p = EnvPipeline()
        p.add_step("alpha", lambda e: e)
        p.add_step("beta", lambda e: e)
        assert p.step_names() == ["alpha", "beta"]

    def test_len_reflects_step_count(self):
        p = EnvPipeline()
        assert len(p) == 0
        p.add_step("s1", lambda e: e)
        assert len(p) == 1

    def test_clear_removes_all_steps(self):
        p = EnvPipeline()
        p.add_step("s1", lambda e: e)
        p.clear()
        assert len(p) == 0
        assert p.run({"K": "v"}) == {"K": "v"}

    def test_add_step_returns_self_for_chaining(self):
        p = EnvPipeline()
        result = p.add_step("s1", lambda e: e)
        assert result is p
