# -*- coding: utf-8 -*-
"""Testes TDD — SPEC-935-R368 — cobertura epistêmica do catálogo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from transformer.episteme import (  # noqa: E402
    EPISTEMES,
    catalog_episteme_coverage,
    infer_agent_episteme,
    infer_episteme_from_text,
)


# ═══════════════════════════════════════════════════════════════════════
# 1. Agentes legados representativos agora classificam
# ═══════════════════════════════════════════════════════════════════════

class TestLexicoAmpliado:
    def _infer(self, name):
        return infer_agent_episteme(
            category="academic", agent_type="maswos-agent", tags=[], name=name
        )

    def test_resultados_empirico(self):
        p = self._infer("09_agente_resultados_evidencias")
        assert p is not None and p.episteme == "empirico_analitico"

    def test_consistencia_critico(self):
        p = self._infer("14_agente_consistencia_interna_coerencia")
        assert p is not None and p.episteme == "critico_reflexivo"

    def test_resumo_abstract_hermeneutico(self):
        p = self._infer("15_agente_resumo_abstract_palavras_chave")
        assert p is not None and p.episteme == "hermeneutico_interpretativo"

    def test_integracao_editorial_docx_pragmatico(self):
        p = self._infer("16_agente_integracao_editorial_docx")
        assert p is not None and p.episteme == "pragmatico_tecnico"

    def test_ml_dl_datamining_empirico(self):
        p = self._infer("22_agente_ml_dl_datamining")
        assert p is not None and p.episteme == "empirico_analitico"


# ═══════════════════════════════════════════════════════════════════════
# 2. Invariantes do léxico
# ═══════════════════════════════════════════════════════════════════════

class TestInvariantes:
    def test_sinais_disjuntos_entre_regimes(self):
        seen = {}
        for regime, spec in EPISTEMES.items():
            for sinal in spec["sinais"]:
                assert sinal not in seen, (
                    f"sinal {sinal!r} em {regime} e em {seen.get(sinal)}"
                )
                seen[sinal] = regime

    def test_nunca_chuta_preservado(self):
        assert infer_episteme_from_text("xyzzy blorb quux") is None
        assert infer_episteme_from_text("") is None

    def test_ambiguos_continuam_fora(self):
        # Termos deliberadamente não classificados (regime não claro)
        for regime in EPISTEMES.values():
            for ambiguo in ("escopo", "busca", "diagnostico"):
                assert ambiguo not in regime["sinais"]


# ═══════════════════════════════════════════════════════════════════════
# 3. Função de cobertura (pura)
# ═══════════════════════════════════════════════════════════════════════

def _defs(*entries):
    out = []
    for name, episteme, tags in entries:
        out.append({
            "agent_id": name,
            "episteme": episteme,
            "category": "academic",
            "type": "specialist",
            "description": "",
            "skills": [{"id": "s", "name": "s", "description": "", "tags": tags}],
        })
    return out


class TestCoverageFunction:
    def test_conta_explicitas_inferidas_e_sem(self):
        defs = _defs(
            ("a", "formal_dedutivo", []),                      # explícita
            ("agente_estatistica_regressao", None, ["sample"]),  # inferida
            ("blorb", None, []),                                # sem episteme
        )
        cov = catalog_episteme_coverage(defs)
        assert cov["total"] == 3
        assert cov["explicit"] == 1
        assert cov["inferred"] == 1
        assert cov["uncovered"] == 1
        assert abs(cov["coverage_ratio"] - 2 / 3) < 1e-9
        assert cov["measured"] is True

    def test_catalogo_vazio(self):
        cov = catalog_episteme_coverage([])
        assert cov["total"] == 0
        assert cov["coverage_ratio"] is None

    def test_cobertura_do_catalogo_real_acima_do_piso(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        cov = catalog_episteme_coverage(load_catalog_definitions())
        assert cov["total"] > 100
        assert cov["coverage_ratio"] >= 0.5, (
            f"cobertura {cov['coverage_ratio']:.2f} abaixo do piso de 0.5"
        )


# ═══════════════════════════════════════════════════════════════════════
# 4. Check no doctor
# ═══════════════════════════════════════════════════════════════════════

class TestDoctorCheck:
    def test_doctor_inclui_episteme_coverage(self):
        from marceloclaro.doctor import run_doctor

        result = run_doctor()
        names = [c["name"] for c in result["checks"]]
        assert "episteme_coverage" in names
        check = [c for c in result["checks"] if c["name"] == "episteme_coverage"][0]
        assert check["status"] in {"pass", "warn"}
        # detail deve reportar números medidos
        assert "%" in check["detail"]
        assert "agentes" in check["detail"].lower()
