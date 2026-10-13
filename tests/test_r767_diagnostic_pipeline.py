# -*- coding: utf-8 -*-
"""TDD SPEC-935-R767 — Pipeline de Diagnóstico por Gaps (hermético, tmp_path)."""
import os

import pytest


def _plano(tmp_path, teoremas=True, proibido=False, cobertura=True):
    lean = tmp_path / "t.lean"
    lean.write_text(
        "theorem alfa : True := trivial\n"
        + ("theorem beta : True := trivial\n" if teoremas else "")
        + ("-- sorry aqui\n" if proibido else ""),
        encoding="utf-8",
    )
    audit = tmp_path / "axiomas.txt"
    audit.write_text(
        "'alfa' depends on axioms: [propext]\n"
        + ("'beta' depends on axioms: [propext]\n" if cobertura else ""),
        encoding="utf-8",
    )
    return {
        "conjuntos": [
            {"tipo": "nomes", "id": "teoremas", "arquivo": str(lean),
             "regex": r"theorem\s+(\w+)",
             "esperados": ["alfa", "beta"],
             "proibidos": [r"\bsorry\b"]},
            {"tipo": "cobertura", "id": "axiomas",
             "arquivo": str(lean), "regex": r"theorem\s+(\w+)",
             "referencia": {"arquivo": str(audit),
                            "regex": r"'(\w+)' depends on axioms"}},
        ]
    }


def test_spec_r767_registered():
    from sdd.spec_engine import spec_registry
    assert spec_registry.get("SPEC-935-R767") is not None


def test_consistente_sem_gaps(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    r = DiagnosticPipeline().varrer(_plano(tmp_path))
    assert r["falharam"] == 0 and r["gaps"] == []
    assert r["rotulo"] == "candidato_a_inspecao"


def test_nome_faltante(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    r = DiagnosticPipeline().varrer(_plano(tmp_path, teoremas=False))
    assert any(g["motivo"] == "faltante" and "beta" in g["detalhe"]
               for g in r["gaps"])


def test_token_proibido(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    r = DiagnosticPipeline().varrer(_plano(tmp_path, proibido=True))
    assert any(g["motivo"] == "proibido" for g in r["gaps"])


def test_cobertura_faltante(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    r = DiagnosticPipeline().varrer(_plano(tmp_path, cobertura=False))
    assert any(g["motivo"] == "cobertura" and "beta" in g["detalhe"]
               for g in r["gaps"])


def test_plano_malformado():
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    with pytest.raises(ValueError):
        DiagnosticPipeline().varrer({"conjuntos": [{"tipo": "x"}]})


def test_arquivo_ausente_vira_gap(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    r = DiagnosticPipeline().varrer(
        {"conjuntos": [{"tipo": "nomes", "id": "q",
                        "arquivo": str(tmp_path / "nao_existe.txt"),
                        "regex": r"(\w+)", "esperados": [],
                        "proibidos": []}]})
    assert any(g["motivo"] == "arquivo_ausente" for g in r["gaps"])


def _plano_cobertura_spec_lean(spec, lean):
    return {"conjuntos": [
        {"tipo": "cobertura", "id": "spec-cobre-lean",
         "arquivo": str(lean), "regex": r"theorem\s+(\w+)",
         "referencia": {"arquivo": str(spec), "regex": r"`([A-Za-z_0-9]+)` \(R\d+\)"}},
    ]}


@pytest.mark.parametrize("spec_text", ["", "`alfa` (R1)\n"])
def test_cobertura_spec_detecta_teorema_nao_documentado(tmp_path, spec_text):
    from scanners.diagnostic_pipeline import DiagnosticPipeline

    lean = tmp_path / "theorems.lean"
    lean.write_text("theorem alfa : True := trivial\ntheorem beta : True := trivial\n",
                    encoding="utf-8")
    spec = tmp_path / "spec.md"
    spec.write_text(spec_text, encoding="utf-8")

    result = DiagnosticPipeline().varrer(_plano_cobertura_spec_lean(spec, lean))

    assert result["falharam"] == 1
    assert any(gap["motivo"] == "cobertura" and gap["detalhe"] == "beta"
               for gap in result["gaps"])


def test_cobertura_spec_reconhece_identificador_com_maiuscula(tmp_path):
    from scanners.diagnostic_pipeline import DiagnosticPipeline

    lean = tmp_path / "theorems.lean"
    lean.write_text("theorem softmax_mem_Ioo : True := trivial\n", encoding="utf-8")
    spec = tmp_path / "spec.md"
    spec.write_text("`softmax_mem_Ioo` (R756)\n", encoding="utf-8")

    result = DiagnosticPipeline().varrer(_plano_cobertura_spec_lean(spec, lean))

    assert result["falharam"] == 0, result["gaps"]


def test_gap_real_no_repo():
    # Cobertura dos teoremas Lean pela SPEC; não avalia testes ou axiomas.
    from scanners.diagnostic_pipeline import DiagnosticPipeline
    base = "/home/marceloclaro/opencode-ecosystem-core"
    lean = os.path.join(base, "plugins/lean-nucleo-verificacao/teoremas/roteamento_atencao.lean")
    if not os.path.isfile(lean):
        pytest.skip("artefato Lean ausente")
    spec = os.path.join(base, "specs/SPEC-935-R755-teorema-roteamento-atencao.md")
    r = DiagnosticPipeline().varrer(_plano_cobertura_spec_lean(spec, lean))
    assert r["falharam"] == 0, r["gaps"]
