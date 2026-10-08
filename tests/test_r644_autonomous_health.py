"""Saúde publicada por outro processo também condiciona fallback."""
from marceloclaro.autonomous import AutonomousCoordinator
from test_r640_autonomous import RuntimeDouble

pytest_plugins = ["test_r640_autonomous"]


def test_fallback_refreshes_eligibility_after_first_failure(isolated_orchestrator, registry):
    class RuntimeWithChangedHealth(RuntimeDouble):
        def status(self):
            result = super().status()
            if self.calls:
                result["executors"]["antigravity"]["eligible_for_auto"] = False
            return result

    runtime = RuntimeWithChangedHealth(available=("codex", "antigravity"), responses=[
        {"success": False, "error": "Falha de execução"}])
    report = AutonomousCoordinator(isolated_orchestrator, runtime, registry).run("Revisar código", max_steps=2)
    assert report["status"] == "failed"
    assert len(runtime.calls) == 1 and report["fallbacks"] == []
