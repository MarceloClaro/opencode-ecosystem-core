"""Gate de entrega: GREEN real isolado não substitui RED anterior executado."""

import importlib
from types import SimpleNamespace

import pytest


@pytest.fixture
def delivery(tmp_path, monkeypatch):
    engine = importlib.import_module("sdd.spec_engine")
    runner = importlib.import_module("sdd.tdd_runner")
    primary_module = importlib.import_module("marceloclaro.orchestrator")
    monkeypatch.setattr(engine, "REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(runner, "REPO_ROOT", str(tmp_path))
    (tmp_path / "tests").mkdir()
    (tmp_path / "calculation.py").write_text("def add(): return 5\n")
    (tmp_path / "tests/test_feature.py").write_text(
        "from calculation import add\ndef test_add():\n    assert add() == 5\n"
    )
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "SPEC-935-R839-FIXTURE.md").write_text("""---
spec_id: SPEC-935-R839-FIXTURE
title: Contrato de soma retido
test_file: tests/test_feature.py
---
## Critérios de Aceitação Executáveis
- `soma` — o resultado deve ser cinco.
""")
    registry = engine.SpecRegistry()
    monkeypatch.setattr(registry, "specs", {})
    # Cada projeto de teste possui uma identidade formal própria; não herda
    # os caminhos do singleton utilizados por outro projeto temporário.
    monkeypatch.setattr(registry, "_formal_sources", {}, raising=False)
    monkeypatch.setattr(registry, "ambiguous_spec_sources", {}, raising=False)
    assert registry.load_formal_specs(str(specs)) == 1
    verifier = engine.SpecVerifier(registry)
    monkeypatch.setattr(primary_module, "spec_verifier", verifier)
    calls = []
    bus = SimpleNamespace(
        memory=SimpleNamespace(add_reflection=lambda **kwargs: None),
        publish=lambda topic, payload, **kwargs: calls.append((topic, payload)),
    )
    monkeypatch.setattr(primary_module, "metabus", bus)
    primary = primary_module.MarceloClaroOrchestrator.__new__(
        primary_module.MarceloClaroOrchestrator
    )
    primary.id = "marceloclaro"
    primary.strict_sdd = True
    primary.task_specs = {"T1": "SPEC-935-R839-FIXTURE"}
    primary.results = {}
    primary.task_stakes = {"T1": True}
    primary.trust = SimpleNamespace(
        learn=lambda action_id, success: calls.append(("trust", success))
    )
    primary.economy = SimpleNamespace(
        resolve=lambda task_id, success: calls.append(("stake", success))
    )
    spec = registry.get("SPEC-935-R839-FIXTURE")
    return tmp_path, primary, spec, calls, runner


@pytest.mark.parametrize("strict", [True, False])
def test_green_real_sem_red_historico_nao_conclui_entrega(
    delivery, strict, monkeypatch
):
    root, primary, spec, calls, runner = delivery
    monkeypatch.setenv("MCI_STATE_DIR", str(root / "state"))
    green = runner.TDDRunner().run_spec_test(spec)
    assert green.passed is True  # Execução real de teste verde, sem RED anterior.
    primary.strict_sdd = strict
    primary.report_completion("T1", "A1", {"answer": 5})
    result = next(payload for topic, payload in calls if topic == "task.complete")
    assert (
        result["status"] == "failed" and result["sdd_verification"]["verified"] is False
    )
    assert result["sdd_verification"]["red_history_required"] is True
    assert ("trust", False) in calls and ("stake", False) in calls


def test_par_red_green_real_permite_entrega_da_mesma_spec(delivery):
    from sdd.tdd_history import TDDHistory

    root, primary, spec, calls, _runner = delivery
    history = TDDHistory(root=root, state_dir=root / "history")
    primary._tdd_history = history
    (root / "calculation.py").write_text("def add(): return 4\n")
    red = history.run(spec, phase="red", timeout_seconds=30)
    assert red.accepted is True
    (root / "calculation.py").write_text("def add(): return 5\n")
    primary.report_completion("T1", "A1", {"answer": 5})
    result = next(payload for topic, payload in calls if topic == "task.complete")
    assert (
        result["status"] == "completed"
        and result["sdd_verification"]["verified"] is True
    )
    assert result["sdd_verification"]["red_history_valid"] is True
    assert ("trust", True) in calls and ("stake", True) in calls


def test_autocorrecao_sem_red_bloqueia_antes_de_aplicar_patch(delivery, monkeypatch):
    from mci import self_correction as module

    root, primary, spec, _calls, _runner = delivery
    monkeypatch.setenv("MCI_STATE_DIR", str(root / "state"))
    monkeypatch.setattr(module, "spec_verifier", primary_module_verifier(primary))
    fixes = []
    engine = module.SelfCorrectionEngine(corrigendum_path=root / "corrigendum.md")
    result = engine.run_correction_cycle(
        spec.spec_id,
        {"description": "falha controlada"},
        lambda: fixes.append(True) or True,
    )
    assert result["success"] is False and result["stage"] == "red"
    assert fixes == [] and engine.get_correction_history() == []


def primary_module_verifier(primary):
    return importlib.import_module("marceloclaro.orchestrator").spec_verifier


def test_refactor_que_quebra_codigo_nao_conclui_ciclo(delivery, monkeypatch):
    from sdd.tdd_history import TDDHistory

    root, primary, spec, _calls, runner = delivery
    monkeypatch.setenv("MCI_STATE_DIR", str(root / "state"))
    monkeypatch.setattr(runner, "spec_verifier", primary_module_verifier(primary))
    history = TDDHistory(root=root)
    (root / "calculation.py").write_text("def add(): return 4\n")
    assert history.run(spec, phase="red", timeout_seconds=30).accepted is True

    def producer(*_):
        (root / "calculation.py").write_text("def add(): return 5\n")
        return {"answer": 5}

    def refactor(*_):
        (root / "calculation.py").write_text("def add(): return 3\n")
        return {"answer": 5}

    result = runner.TDDRunner(max_iterations=1).run_cycle(spec, producer, refactor)
    assert result["success"] is False and result["phase"] == "refactor"
    assert spec.status != "verified"


def test_autocorrecao_com_red_real_aplica_e_registra_green(delivery, monkeypatch):
    from mci import self_correction as module
    from sdd.tdd_history import TDDHistory

    root, primary, spec, _calls, _runner = delivery
    monkeypatch.setattr(module, "spec_verifier", primary_module_verifier(primary))
    history = TDDHistory(root=root, state_dir=root / "history")
    (root / "calculation.py").write_text("def add(): return 4\n")
    assert history.run(spec, phase="red", timeout_seconds=30).accepted is True
    corrigendum = root / "corrigendum.md"
    corrigendum.write_text("# Registro controlado\n")
    engine = module.SelfCorrectionEngine(corrigendum_path=corrigendum, history=history)

    def fix():
        (root / "calculation.py").write_text("def add(): return 5\n")
        return True

    result = engine.run_correction_cycle(
        spec.spec_id, {"description": "soma controlada"}, fix
    )
    assert result["success"] is True and result["stage"] == "applied"
    assert result["verification_result"]["red_history_valid"] is True
    assert len(engine.get_correction_history()) == 1
    assert spec.spec_id in corrigendum.read_text()


def test_preflight_recusa_historico_de_outra_raiz(delivery):
    from sdd.tdd_history import TDDHistory

    root, primary, spec, _calls, _runner = delivery
    other = root / "other"
    other.mkdir()
    primary._tdd_history = TDDHistory(root=other, state_dir=other / "history")
    result = primary.sdd_preflight(spec.spec_id)
    assert result["ready"] is False and result["error"] == "history_scope_invalid"
