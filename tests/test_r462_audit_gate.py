"""Testes da SPEC-935-R462 — Cadeia de Custódia Auditável.

Provam que o EvolutionAuditGate:
(a) recusa ciclo sem veredito externo e sem hash (fail-closed);
(b) rejeita ciclo cujo verificador == gerador (quebra gerador=julgador);
(c) detecta tamper de artefato via hash SHA-256;
(d) a métrica de Custódia sobe quando ciclos auditados são registrados;
(e) retém compatibilidade com ciclos legados (sem os campos novos);
(f) o registro auditado recusa persistir ciclo não aprovado (fail-closed);
(g) o relatório auditável é gerado.

IMPORTANTE (isolamento):
Cada teste cria sua PRÓPRIA instância de EvolutionRegistry com
`state_path=<arquivo temporário>` POR INSTÂNCIA. Isso evita tocar o arquivo
real `evolution/cycles.json` e é imune à ordem de importação dos módulos
(StatePath global não é usado aqui como estado de escrita).
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

import pytest

from evolution.audit_gate import EvolutionAuditGate  # noqa: E402
from evolution.cycles import EvolutionCycle, EvolutionRegistry  # noqa: E402


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _artefato() -> bytes:
    return b"def f():\n    return 42\n"


def _registry() -> EvolutionRegistry:
    """Cria um registro com state_path ISOLADO (nunca toca o arquivo real)."""
    tmp = tempfile.mkdtemp(prefix="evo_r462_")
    return EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json"))


def _isolated() -> "tuple[EvolutionRegistry, str]":
    """Retorna (registro isolado, dir_temp) para inspeção quando necessário."""
    tmp = tempfile.mkdtemp(prefix="evo_r462_")
    return EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json")), tmp


@pytest.fixture
def gate() -> EvolutionAuditGate:
    return EvolutionAuditGate()


def test_ciclo_sem_veredito_externo_e_rejeitado(gate: EvolutionAuditGate):
    """(a) fail-closed: sem trilha de evidência => recusa; e sem artefatos
    => recusa. A aprovação só ocorre com TODAS as condições presentes."""
    # sem trilha de evidência (condição iii do fator limítrofe)
    sem_evidencia = gate.verify_cycle(
        objective="teste",
        changes=["mudei X"],
        artifact_files={"a.py": b"x" * 10},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=[],  # vazio => recusa
    )
    assert sem_evidencia.passed is False
    assert "evid" in sem_evidencia.reason
    # sem artefatos => recusa
    sem_artefatos = gate.verify_cycle(
        objective="teste",
        changes=["mudei X"],
        artifact_files={},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=["spec"],
    )
    assert sem_artefatos.passed is False
    assert "artefato" in sem_artefatos.reason


def test_verifier_igual_ao_gerador_e_rejeitado(gate: EvolutionAuditGate):
    """(b) quebra gerador=julgador: verificador nao pode ser o gerador."""
    art = _artefato()
    ev = ["test_r462"]
    result = gate.verify_cycle(
        objective="teste",
        changes=["mudei Y"],
        artifact_files={"mod.py": art},
        verifier_identity="gerador",  # mesmo agente que gerou
        generator_identity="gerador",
        evidence_trail=ev,
    )
    assert result.passed is False
    # identidades distintas => passa
    ok = gate.verify_cycle(
        objective="teste",
        changes=["mudei Y"],
        artifact_files={"mod.py": art},
        verifier_identity="auditor_externo",
        generator_identity="gerador",
        evidence_trail=ev,
    )
    assert ok.passed is True


def test_tamper_de_artefato_e_detectado(gate: EvolutionAuditGate):
    """(c) hash registrado != hash real => compromised/tampered."""
    art = _artefato()
    hashes = {"mod.py": _sha(art.decode())}
    ev = ["test_r462"]
    result = gate.verify_cycle(
        objective="teste",
        changes=["z"],
        artifact_files={"mod.py": art},
        verifier_identity="auditor",
        generator_identity="gerador",
        evidence_trail=ev,
    )
    assert result.passed is True
    altered = b"def f():\n    return 999\n"
    assert _sha(art.decode()) != _sha(altered.decode())
    result2 = gate.verify_tamper(
        artifact_files={"mod.py": altered},
        registered_hashes=hashes,
    )
    assert result2.tampered is True


def test_custodia_sobe_ao_registrar_ciclo_auditado(gate: EvolutionAuditGate):
    """(d) métrica de Custódia aumenta quando ciclo auditado entra."""
    reg = _registry()
    before = reg.custody_metric()
    assert before["pct"] == 0.0

    art = _artefato()
    files = {"mod.py": art}
    v = gate.verify_cycle(
        objective="ciclo auditado R462",
        changes=["implementa gate"],
        artifact_files=files,
        verifier_identity="auditor_v1",
        generator_identity="gerador",
        evidence_trail=["test_r462"],
    )
    assert v.passed is True
    reg.record_audited(
        objective="ciclo auditado R462",
        changes=["implementa gate"],
        artifact_hashes={k: _sha(x.decode()) for k, x in files.items()},
        external_verdict={"passed": True, "evidence": ["test_r462"]},
        verifier_identity="auditor_v1",
        generator_identity="gerador",
        round_id="R462",
    )
    after = reg.custody_metric()
    assert after["pct"] == 100.0
    assert after["audited"] == 1


def test_legado_retro_compativel():
    """(e) ciclos legados (sem campos novos) continuam carregando."""
    reg, tmp = _isolated()
    legacy = EvolutionCycle(round_id="R999", objective="legacy", score=8.0)
    reg.cycles.append(legacy)
    reg.save()

    reg2 = EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json"))
    ciclos = [c for c in reg2.cycles if c.round_id == "R999"]
    assert len(ciclos) == 1
    assert ciclos[0].score == 8.0
    assert ciclos[0].artifact_hashes == {}
    assert ciclos[0].external_verdict is None
    assert ciclos[0].verifier_identity == ""


def test_gate_recusa_registro_sem_auditoria():
    """(f) fail-closed integrado à persistência: sem veredito aprovado,
    `record_audited` NÃO persiste e levanta PermissionError."""
    reg = _registry()
    with pytest.raises(PermissionError):
        reg.record_audited(
            objective="nao auditado",
            changes=["deveria falhar"],
            artifact_hashes={"a.py": "hash"},
            external_verdict={"passed": False},
            verifier_identity="auditor",
            generator_identity="gerador",
        )
    assert reg.custody_metric()["total"] == 0


def test_record_legado_marca_legacy_nao_quebra_compatibilidade():
    """`record()` antigo continua funcionando, porém marca o ciclo como
    `legacy` e NÃO eleva a métrica de Custódia."""
    reg = _registry()
    ciclo = reg.record(objective="ciclo legado", changes=["x"],
                       score=8.0, round_id="R990")
    assert ciclo.legacy is True
    assert ciclo.audited is False
    m = reg.custody_metric()
    assert m["audited"] == 0
    assert m["legacy"] == 1
    r = reg.custody_recent()
    assert r["total"] == 0 or r["pct"] == 0.0


def test_custody_recent_mede_ciclos_novos_auditados():
    """custody_recent() mede a fração de ciclos NOVOS (R462+) auditados,
    excluindo o legado."""
    reg = _registry()
    reg.cycles.append(
        EvolutionCycle(round_id="R100", objective="legado")
    )
    art = _artefato()
    reg.record_audited(
        objective="ciclo novo auditado",
        changes=["z"],
        artifact_hashes={"m.py": _sha(art.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        round_id="R462",
    )
    r = reg.custody_recent()
    assert r["total"] == 1
    assert r["audited"] == 1
    assert r["pct"] == 100.0


def test_report_gera_markdown_auditavel():
    """(g) evolution/report.py gera relatório Markdown auditável."""
    from evolution.report import EvolutionReport
    reg = _registry()
    art = _artefato()
    reg.record_audited(
        objective="rel",
        changes=["z"],
        artifact_hashes={"m.py": _sha(art.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        round_id="R462",
    )
    rep = EvolutionReport(reg)
    md = rep.to_markdown(limit=10)
    assert "Custódia recente" in md
    assert "R462" in md
    assert "APROVADO" in md
    assert "auditor_ext" in md
    tmp = tempfile.mkdtemp(prefix="evo_report_")
    out = os.path.join(tmp, "rel.md")
    rep.write(out)
    assert os.path.exists(out)
