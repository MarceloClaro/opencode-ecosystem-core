# -*- coding: utf-8 -*-
"""
Testes R110 — Doctor (diagnóstico de saúde) + prática de CORRIGENDUM
=====================================================================
Testa marceloclaro/doctor.py (run_doctor, checks individuais) e
MarceloClaroOrchestrator.doctor(), além da presença/estrutura de
CORRIGENDUM.md.

Inspirado no comando `doctor`/`status` e no `CORRIGENDUM.md` do projeto
original OpenCode_Ecosystem.

Requisitos (SPEC-935-R110):
  - run_doctor() agrega checks estruturais em segundos (sem rodar pytest)
  - Detecta perda silenciosa de ciclos no registro de evolução (mesmo
    bug corrigido no R108) comparando contagem bruta do JSON vs. carregada
  - Sinaliza loop specs mal-formados
  - MarceloClaroOrchestrator.doctor() inclui catalog_agents e trust_status
  - CORRIGENDUM.md existe, referencia os 5 itens identificados e é
    detectado pelo check correspondente
"""

import copy
import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(autouse=True)
def _isolate_metacognitive_memory():
    """Ver justificativa em tests/test_r108_marceloclaro_scientific_fusion.py.
    Tambem isola o LoopSpecRegistry (singleton): testes que registram
    loop specs de teste (ex.: um mal-formado de proposito) nao podem
    vazar para outros testes no mesmo processo."""
    from mci.metabus import metabus
    from sdd.loop_spec import loop_spec_registry

    memory_snapshot = (
        copy.deepcopy(metabus.memory.episodic),
        copy.deepcopy(metabus.memory.semantic),
        copy.deepcopy(metabus.memory.confidence_ledger),
    )
    loops_snapshot = dict(loop_spec_registry.loops)
    yield
    metabus.memory.episodic, metabus.memory.semantic, metabus.memory.confidence_ledger = memory_snapshot
    metabus.memory._save()
    loop_spec_registry.loops = loops_snapshot


# ── 1. run_doctor() estrutural ───────────────────────────────────────

class TestRunDoctor:
    def test_returns_expected_shape(self):
        from marceloclaro.doctor import run_doctor
        report = run_doctor()
        for key in ("overall", "checks", "checks_total", "checks_passed",
                    "checks_warned", "checks_failed", "duration_seconds"):
            assert key in report
        assert report["overall"] in ("healthy", "degraded", "unhealthy")
        assert report["checks_total"] == len(report["checks"])

    def test_is_fast_not_a_full_pytest_run(self):
        """O doctor precisa ser um check estrutural rapido — nao deve
        chamar a suite pytest completa (~150s)."""
        import time
        from marceloclaro.doctor import run_doctor
        start = time.time()
        run_doctor()
        assert time.time() - start < 5.0

    def test_real_evolution_registry_has_no_silent_loss(self):
        """Regressao direta do bug do R108: garante que o arquivo real
        evolution/cycles.json nao volta a perder ciclos silenciosamente."""
        from marceloclaro.doctor import run_doctor
        report = run_doctor()
        evo_check = next(c for c in report["checks"] if c["name"] == "evolution_registry")
        assert evo_check["status"] == "pass"


# ── 2. Checks individuais (cenarios controlados) ─────────────────────

class TestIndividualChecks:
    def test_evolution_registry_check_fails_on_silent_data_loss(self, tmp_path, monkeypatch):
        """Simula exatamente o bug do R108: o arquivo em disco tem 2
        ciclos, mas o registro (por qualquer motivo — ex.: o bug de
        chave extra ja corrigido) carregou menos do que isso."""
        from marceloclaro import doctor as doctor_mod
        import evolution.cycles as cycles_mod

        evo_dir = tmp_path / "evolution"
        evo_dir.mkdir()
        (evo_dir / "cycles.json").write_text(json.dumps({
            "cycles": [
                {"round_id": "R1", "objective": "o", "changes": [], "score": 9.0, "lessons": []},
                {"round_id": "R2", "objective": "o", "changes": [], "score": 9.0, "lessons": []},
            ]
        }), encoding="utf-8")

        monkeypatch.setattr(doctor_mod, "REPO_ROOT", str(tmp_path))

        class RegistryThatLostOneCycle:
            def __init__(self):
                self.cycles = [object()]  # deveria ter 2, carregou so 1

        monkeypatch.setattr(cycles_mod, "EvolutionRegistry", RegistryThatLostOneCycle)

        check = doctor_mod._check_evolution_registry()
        assert check.status == "fail"
        assert "Perda silenciosa" in check.detail

    def test_loop_specs_check_flags_malformed_loop(self, monkeypatch):
        from marceloclaro import doctor as doctor_mod
        from sdd.loop_spec import LoopSpecification, LoopSpecRegistry

        registry = LoopSpecRegistry()
        registry.register(LoopSpecification(
            name="loop-mal-formado-teste",
            description="d", use_when="u",
            trigger_justification="",  # propositalmente vazio -> mal formado
            goal="g", verification_description="v", memory_location="m",
        ))

        check = doctor_mod._check_loop_specs()
        assert check.status == "fail"
        assert "loop-mal-formado-teste" in check.detail

    def test_opencode_config_check_fails_on_invalid_json(self, tmp_path, monkeypatch):
        from marceloclaro import doctor as doctor_mod
        bad_path = tmp_path / "opencode.json"
        bad_path.write_text("{ isso nao e json valido", encoding="utf-8")
        monkeypatch.setattr(doctor_mod, "REPO_ROOT", str(tmp_path))
        check = doctor_mod._check_opencode_config()
        assert check.status == "fail"

    def test_corrigendum_check_warns_when_absent(self, tmp_path, monkeypatch):
        from marceloclaro import doctor as doctor_mod
        monkeypatch.setattr(doctor_mod, "REPO_ROOT", str(tmp_path))
        check = doctor_mod._check_corrigendum()
        assert check.status == "warn"

    def test_corrigendum_check_passes_when_present_and_substantial(self):
        from marceloclaro import doctor as doctor_mod
        check = doctor_mod._check_corrigendum()
        assert check.status == "pass"


# ── 3. MarceloClaroOrchestrator.doctor() ─────────────────────────────

class TestOrchestratorDoctor:
    def test_includes_catalog_and_trust_status(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        report = orch.doctor()
        assert "catalog_agents" in report
        assert "trust_status" in report
        assert report["overall"] in ("healthy", "degraded", "unhealthy")

    def test_loop_spec_check_passes_after_orchestrator_init(self):
        """A LoopSpecification do pipeline cientifico (R109) e registrada
        no __init__, entao o check deve refletir isso como bem formado."""
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        report = orch.doctor()
        loop_check = next(c for c in report["checks"] if c["name"] == "loop_specs")
        assert loop_check["status"] in ("pass", "warn")
        assert "scientific-discovery" not in loop_check["detail"] or loop_check["status"] == "pass"


# ── 4. CORRIGENDUM.md — presenca e conteudo ──────────────────────────

class TestCorrigendumDocument:
    def test_file_exists_at_repo_root(self):
        path = os.path.join(REPO_ROOT, "CORRIGENDUM.md")
        assert os.path.exists(path)

    def test_references_the_five_identified_overclaims(self):
        path = os.path.join(REPO_ROOT, "CORRIGENDUM.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for marker in (
            "Tabela comparativa vs. frameworks externos",
            "Qualis A1",
            "Score médio",
            "160+ agentes",
            "Superhuman",
        ):
            assert marker in content, f"Marcador ausente no CORRIGENDUM: {marker}"

    def test_readme_and_architecture_reference_corrigendum(self):
        for doc_name in ("README.md", "ARCHITECTURE.md"):
            path = os.path.join(REPO_ROOT, doc_name)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "CORRIGENDUM.md" in content, f"{doc_name} nao referencia CORRIGENDUM.md"
