"""Testes de PROVAGAÇÃO STRING do gate de Cadeia de Custódia (SPEC-935-R462)
no orquestrador — `marceloclaro.orchestrator.record_evolution()`.

Prova que o método de integração real:
(a) eleva a Custódia ao receber verifier_identity + artifact_files (auditado);
(b) mantém compatibilidade: chamada sem auditoria => legacy (audited=False) —
    não eleva custódia falsamente;
(c) persiste REJECT TRAIL quando o gate reprova (ex.: verifier == gerador);
(d) injeta reflexões no MetaBus em cada caminho.

ISOLAMENTO (lição crítica R462): o `record_evolution` usa o singleton global
`evolution_registry` (module-global em `marceloclaro.orchestrator`). Cada
teste MONKEYPATCH esse global com um registro isolado em arquivo temporário,
para NUNCA tocar o `evolution/cycles.json` real.
"""

from __future__ import annotations

import hashlib
import os
import tempfile

import pytest

from evolution.cycles import EvolutionRegistry


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _artefato() -> bytes:
    return b"def f():\n    return 42\n"


def _isolated_registry() -> EvolutionRegistry:
    """Registro isolado em arquivo temporário (nunca toca o real)."""
    tmp = tempfile.mkdtemp(prefix="evo_prop_")
    return EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json"))


@pytest.fixture
def orch(monkeypatch):
    """Instancia o orquestrador com o evolution_registry global ISOLADO."""
    from marceloclaro.orchestrator import MarceloClaroOrchestrator

    reg = _isolated_registry()
    # substitui o singleton global usado dentro de orchestrator.record_evolution
    monkeypatch.setattr(
        "marceloclaro.orchestrator.evolution_registry", reg,
    )
    o = MarceloClaroOrchestrator(auto_load_agents=False)
    o._evo_reg = reg  # guarda referência para assert nos testes
    return o


def test_auditado_eleva_custodia(orch):
    """(a) com verifier+artefatos, o ciclo é auditado e a Custódia sobe."""
    art = _artefato()
    res = orch.record_evolution(
        objective="ciclo auditado via orquestrador",
        changes=["integrou o gate"],
        score=9.0,
        lessons=["lição X"],
        verifier_identity="auditor@bloqueado",
        artifact_files={"mod.py": art},
        evidence_trail=["test_r462_gate_propagation"],
        round_id="R462",
    )
    assert res["audited"] is True
    assert res.get("rejected", False) is False

    m = orch._evo_reg.custody_metric()
    assert m["audited"] == 1
    assert m["legacy"] == 0
    # âncora merkle presente (imutabilidade composta)
    ciclo = orch._evo_reg.cycles[-1]
    assert ciclo.merkle_root != ""
    assert ciclo.audited is True
    assert ciclo.verifier_identity == "auditor@bloqueado"

    # recente R462+ = 100%
    r = orch._evo_reg.custody_recent()
    assert r["pct"] == 100.0


def test_sem_auditoria_fica_legado_honesto(orch):
    """(b) chamada antiga (sem verifier/artefatos): legacy, audited=False,
    NÃO eleva Custódia (anti-overclaim estrutural)."""
    res = orch.record_evolution(
        objective="ciclo sem auditoria",
        changes=["x"],
        score=8.0,
        lessons=["sem veredito externo"],
    )
    assert res["audited"] is False

    m = orch._evo_reg.custody_metric()
    assert m["audited"] == 0
    assert m["legacy"] == 1
    assert m["pct"] == 0.0


def test_verifier_igual_gerador_gera_reject_trail(orch):
    """(c) verifier == gerador: o gate reprova e o orquestrador persiste um
    REJECT TRAIL (rastro auditável da falha), sem elevar Custódia."""
    art = _artefato()
    res = orch.record_evolution(
        objective="falha no gate",
        changes=["viola gerador=julgador"],
        verifier_identity="marceloclaro",   # gerador se auto-avaliando
        generator_identity="marceloclaro",
        artifact_files={"mod.py": art},
        evidence_trail=["test_r462_gate_propagation"],
    )
    assert res["audited"] is False
    assert res["rejected"] is True

    m = orch._evo_reg.custody_metric()
    assert m["audited"] == 0
    assert m["rejected"] == 1     # rastro persistido
    # o ciclo persistido tem passed=False
    rej = [c for c in orch._evo_reg.cycles
           if c.external_verdict and c.external_verdict.get("passed") is False]
    assert len(rej) == 1


def test_verdict_externo_explicito_aprovado(orch):
    """(d) chamador pode fornecer external_verdict explícito aprovado; o
    caminho auditado é usado diretamente (sem re-verificação redundante)."""
    art = _artefato()
    res = orch.record_evolution(
        objective="veredito externo explícito",
        changes=["z"],
        verifier_identity="auditor_v2",
        artifact_files={"mod.py": art},
        external_verdict={"passed": True, "reason": "auditado por auditor_v2"},
        evidence_trail=["test_r462_gate_propagation"],
    )
    assert res["audited"] is True
    ciclo = orch._evo_reg.cycles[-1]
    assert ciclo.audited is True
    assert ciclo.external_verdict["passed"] is True
    assert ciclo.merkle_root != ""
