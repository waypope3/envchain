"""EnvPipeline: sequential processing pipeline for env dicts."""

from typing import Callable, Any, Dict, List, Optional


class PipelineError(Exception):
    def __init__(self, step_name: str, message: str):
        self.step_name = step_name
        super().__init__(f"Pipeline step '{step_name}' failed: {message}")


class EnvPipeline:
    """Runs a sequence of transformation steps over an env dict."""

    def __init__(self):
        self._steps: List[tuple[str, Callable[[Dict[str, Any]], Dict[str, Any]]]] = []

    def add_step(self, name: str, fn: Callable[[Dict[str, Any]], Dict[str, Any]]) -> "EnvPipeline":
        """Register a named transformation step."""
        if not callable(fn):
            raise PipelineError(name, "step must be callable")
        if not name or not isinstance(name, str):
            raise PipelineError(name, "step name must be a non-empty string")
        self._steps.append((name, fn))
        return self

    def step_names(self) -> List[str]:
        """Return ordered list of registered step names."""
        return [name for name, _ in self._steps]

    def run(self, env: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all steps in order, passing result of each into the next."""
        current = dict(env)
        for name, fn in self._steps:
            try:
                result = fn(current)
                if not isinstance(result, dict):
                    raise PipelineError(name, "step must return a dict")
                current = result
            except PipelineError:
                raise
            except Exception as exc:
                raise PipelineError(name, str(exc)) from exc
        return current

    def run_partial(self, env: Dict[str, Any], up_to: str) -> Dict[str, Any]:
        """Run steps up to and including the named step."""
        current = dict(env)
        for name, fn in self._steps:
            try:
                result = fn(current)
                if not isinstance(result, dict):
                    raise PipelineError(name, "step must return a dict")
                current = result
            except PipelineError:
                raise
            except Exception as exc:
                raise PipelineError(name, str(exc)) from exc
            if name == up_to:
                return current
        raise PipelineError(up_to, f"step '{up_to}' not found in pipeline")

    def clear(self) -> "EnvPipeline":
        """Remove all registered steps."""
        self._steps.clear()
        return self

    def __len__(self) -> int:
        return len(self._steps)
