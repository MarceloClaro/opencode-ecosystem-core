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


# ---------------------------------------------------------------------------
# Endurecimento minucioso (SPEC-935-R462, fase "implemente minuciosamente")
# ---------------------------------------------------------------------------


def test_auto_hash_de_disco_ancora_imutabilidade_real(tmp_path):
    """(h) resolve_artifacts hasheia o conteúdo REAL de arquivos em disco
    (auto-hash), e merkle_root muda quando um arquivo é alterado."""
    gate = EvolutionAuditGate()
    f1 = tmp_path / "mod.py"
    f2 = tmp_path / "spec.md"
    f1.write_bytes(b"def f():\n    return 42\n")
    f2.write_bytes(b"# spec R462")

    hashes_antes = gate.resolve_artifacts({"mod.py": str(f1), "spec.md": str(f2)})
    assert isinstance(hashes_antes["mod.py"], str) and len(hashes_antes["mod.py"]) == 64
    assert hashes_antes["mod.py"] == _sha("def f():\n    return 42\n")

    # tamper real no disco
    f1.write_bytes(b"def f():\n    return 999\n")
    verification = gate.verify_tamper(
        artifact_files={"mod.py": str(f1), "spec.md": str(f2)},
        registered_hashes=hashes_antes,
    )
    assert verification.tampered is True
    assert "mod.py" in verification.reason


def test_merkle_root_agrega_e_verify_merkle_confere(gate: EvolutionAuditGate):
    """(i) merkle_root agrega os hashes de forma canônica (ordenada por nome)
    e verify_merkle confere a raiz ancorada."""
    h1 = {"a.py": "1111", "b.py": "2222"}
    root = gate.merkle_root(h1)
    assert isinstance(root, str) and len(root) == 64
    # mesma ordem (canônica por nome) => mesma raiz
    h_reord = {"b.py": "2222", "a.py": "1111"}
    assert gate.merkle_root(h_reord) == root
    # qualquer artefato alterado => raiz muda
    assert gate.merkle_root({"a.py": "9999", "b.py": "2222"}) != root
    # verificação da âncora
    assert gate.verify_merkle(hashes=h1, registered_root=root) is True
    assert gate.verify_merkle(hashes={"a.py": "9999", "b.py": "2222"},
                              registered_root=root) is False
    # conjunto vazio => raiz vazia (sem falsificação)
    assert gate.merkle_root({}) == ""


def test_merkle_root_e_sensivel_a_nome_do_artefato(gate: EvolutionAuditGate):
    """(j) a raiz muda se o NOME muda, mesmo com conteúdo igual."""
    m1 = gate.merkle_root({"x.py": "abc"})
    m2 = gate.merkle_root({"y.py": "abc"})
    assert m1 != m2


def test_git_head_commit_retorna_hash_ou_vazio():
    """(k) git_head_commit retorna o commit HEAD ou string vazia (não
    falsifica quando o repo/contexto não está disponível)."""
    from evolution.audit_gate import git_head_commit
    c = git_head_commit()
    # Em ambiente git (este repo), deve retornar um hash hex de 40 carac.
    if c:
        assert len(c) == 40
        assert all(ch in "0123456789abcdef" for ch in c)


def test_record_audited_ancora_commit_merkle_estado(gate: EvolutionAuditGate):
    """(l) o ciclo auditado grava âncoras externas: origin_commit (git HEAD),
    merkle_root (agregado dos artefatos) e state_merkle_root (fotografia do
    cycles.json antes da inserção)."""
    reg = _registry()
    art = _artefato()
    files = {"mod.py": art}
    v = gate.verify_cycle(
        objective="ancoras",
        changes=["z"],
        artifact_files=files,
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        evidence_trail=["test_r462"],
    )
    assert v.passed is True
    ciclo = reg.record_audited(
        objective="ancoras",
        changes=["z"],
        artifact_hashes={k: _sha(x.decode()) for k, x in files.items()},
        external_verdict={"passed": True},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        evidence_trail=["test_r462"],
        round_id="R462",
    )
    # merkle_root ancorado (agregado dos hashes do ciclo)
    assert ciclo.merkle_root == gate.merkle_root(
        {k: _sha(x.decode()) for k, x in files.items()})
    # origin_commit presente (repo git) OU vazio (contexto sem git) — sem falsificação
    assert isinstance(ciclo.origin_commit, str)
    # state_merkle_root: fotografia do cycles.json no momento do registro
    assert isinstance(ciclo.state_merkle_root, str)
    if ciclo.state_merkle_root:
        # re-hashear o OUTRO estado (após a persistência) deve divergir,
        # pois o hash foi tirado ANTES de inserir o ciclo
        with open(reg.state_path, "rb") as f:
            pos_hash = gate.hash_state(f.read())
        assert pos_hash != ciclo.state_merkle_root

    # persistência round-trip: as âncoras sobrevivem ao reload
    reg2 = EvolutionRegistry(state_path=reg.state_path)
    ciclos2 = [c for c in reg2.cycles if c.round_id == "R462"]
    assert len(ciclos2) == 1
    assert ciclos2[0].merkle_root == ciclo.merkle_root
    assert ciclos2[0].origin_commit == ciclo.origin_commit
    assert ciclos2[0].state_merkle_root == ciclo.state_merkle_root


def test_record_rejected_persiste_rastro_auditavel():
    """(m) um veredito REPROVADO é persistido como rastro auditável
    (reject trail), não apenas exceção — a falha também é rastreável."""
    reg = _registry()
    total_antes = reg.custody_metric()["total"]
    ciclo = reg.record_rejected(
        objective="tentativa reprovada",
        changes=["falhou no gate"],
        reason="verificador == gerador",
        verifier_identity="gerador",
        generator_identity="gerador",
    )
    assert ciclo.audited is False
    assert ciclo.external_verdict["passed"] is False
    assert ciclo.external_verdict["reason"] == "verificador == gerador"

    m = reg.custody_metric()
    assert m["total"] == total_antes + 1
    assert m["rejected"] == 1   # contabilizado como reject trail
    assert m["audited"] == 0    # NÃO conta como ciclo auditado

    # round-trip: o rastro persiste após reload
    reg2 = EvolutionRegistry(state_path=reg.state_path)
    rej = [c for c in reg2.cycles if c.external_verdict
           and c.external_verdict.get("passed") is False]
    assert len(rej) == 1


def test_verify_tamper_detecta_tamper_real_persistido(gate: EvolutionAuditGate, tmp_path):
    """(n) cenário completo de tamper real: hash registrado -> alteração no
    disco -> verify_tamper marca tampered=True e a métrica reflete."""
    f = tmp_path / "mod.py"
    f.write_bytes(b"def f():\n    return 42\n")

    v = gate.verify_cycle(
        objective="tamper real",
        changes=["z"],
        artifact_files={"mod.py": str(f)},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        evidence_trail=["test_r462"],
    )
    assert v.passed is True
    registered = v.hashes

    # altera o arquivo no disco
    f.write_bytes(b"def f():\n    return 999\n")
    res = gate.verify_tamper(artifact_files={"mod.py": str(f)},
                             registered_hashes=registered)
    assert res.tampered is True

    # veredito externo marcado com tampered reflete no registro
    reg = _registry()
    ciclo = reg.record_audited(
        objective="tamper real",
        changes=["z"],
        artifact_hashes=registered,
        external_verdict={"passed": True, "tampered": True},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        round_id="R700",
    )
    assert ciclo.external_verdict["tampered"] is True
    assert reg.custody_metric()["tampered"] == 1


def test_full_load_mapeia_todos_os_tipos_de_ciclo():
    """(o) carregamento completo (full-load) preserva auditado, legado e
    rejeitado juntos no mesmo registro, sem perda de nenhum."""
    reg, tmp = _isolated()
    reg.record(objective="legado", changes=["x"], round_id="R100")       # legacy
    reg.record_rejected(objective="rejeitado", changes=["z"],
                        reason="gate", verifier_identity="gerador",
                        generator_identity="gerador", round_id="R101")   # rejected
    art = _artefato()
    reg.record_audited(
        objective="auditado", changes=["z"],
        artifact_hashes={"m.py": _sha(art.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        round_id="R102",
    )                                                                   # audited

    reg2 = EvolutionRegistry(state_path=os.path.join(tmp, "cycles.json"))
    assert len(reg2.cycles) == 3
    m = reg2.custody_metric()
    assert m["legacy"] == 1
    assert m["rejected"] == 1
    assert m["audited"] == 1
    assert m["total"] == 3


def test_pdf_gerado_quando_conversor_disponivel():
    """(p) report.to_pdf retorna caminho se pandoc/weasyprint existir, ou None
    (não falsifica) caso contrário."""
    from evolution.report import EvolutionReport
    reg = _registry()
    art = _artefato()
    reg.record_audited(
        objective="pdf", changes=["z"],
        artifact_hashes={"m.py": _sha(art.decode())},
        external_verdict={"passed": True},
        verifier_identity="auditor_ext",
        generator_identity="gerador",
        round_id="R462",
    )
    rep = EvolutionReport(reg)
    tmp = tempfile.mkdtemp(prefix="evo_report_")
    out = os.path.join(tmp, "rel.pdf")
    result = rep.to_pdf(out)
    if result is not None:
        assert result == out
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0
    else:
        # sem conversor: retorna None, sem criar arquivo fantasma
        assert not os.path.exists(out)
