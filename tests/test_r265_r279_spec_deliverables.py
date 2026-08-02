# -*- coding: utf-8 -*-
"""Testes de regressão de entregáveis — SPECs R265, R266, R277, R278, R279.

Estas cinco specs apontavam para "validação inline" ou para arquivos de
teste que nunca existiram no histórico do git — overclaim do tipo que o
CORRIGENDUM documenta. Este arquivo dá a cada spec uma verificação real e
repetível dos entregáveis que ela reivindica. Artefatos arquivados fora do
checkout são pulados explicitamente — nunca aprovados por ausência.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VR = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
PDF_OLD = VR / "_archive" / "pdf_old"


def _require(path: Path, spec: str):
    if not path.exists():
        pytest.skip(f"{spec}: artefato não presente no checkout: {path.name}")
    return path


# ── SPEC-935-R265 — auditoria final do miolo 160x230mm ────────────────

class TestR265AuditoriaFinal:
    def test_pdf_final_do_miolo_presente_e_com_folios(self):
        pdf = _require(
            PDF_OLD / "main_miolo_amazon_kdp_160x230mm_COM-FOLIOS_SEM-LINKS_SAFE-MARGINS.pdf",
            "R265",
        )
        pypdf = pytest.importorskip("pypdf")
        reader = pypdf.PdfReader(str(pdf))
        assert len(reader.pages) > 100


# ── SPEC-935-R266 — ficha de estudo crítica ───────────────────────────

class TestR266FichaEstudo:
    def test_ficha_compilada_presente(self):
        pdf = _require(PDF_OLD / "ficha_estudo_critico.pdf", "R266")
        pypdf = pytest.importorskip("pypdf")
        reader = pypdf.PdfReader(str(pdf))
        assert len(reader.pages) >= 2


# ── SPEC-935-R277 — dossiê multiagente literário (7 especialistas) ────

class TestR277AgentesLiterarios:
    def test_cards_literarios_carregam_no_catalogo(self):
        from marceloclaro.catalog_loader import load_catalog_definitions

        defs = load_catalog_definitions()
        literary = [
            d for d in defs
            if Path(d["source_file"]).name.startswith("literary-")
        ]
        assert len(literary) >= 7, (
            f"esperados >= 7 agentes literary-*, encontrados {len(literary)}"
        )
        for d in literary:
            assert d["description"], f"{d['agent_id']} sem descrição"


# ── SPEC-935-R278 — revisão CONT e DOC ────────────────────────────────

class TestR278FragmentosContDoc:
    @pytest.mark.parametrize("family", ["cont", "doc"])
    def test_fragmentos_existem_e_nao_vazios(self, family):
        directory = VR / "fragmentos" / family
        _require(directory, "R278")
        tex_files = sorted(directory.glob("*.tex"))
        assert tex_files, f"nenhum .tex em fragmentos/{family}"
        for tex in tex_files:
            assert tex.stat().st_size > 0, f"{tex.name} vazio"


# ── SPEC-935-R279 — protocolo beta + dossiê bibliográfico ─────────────

class TestR279RelatoriosBeta:
    @pytest.mark.parametrize("name", [
        "beta_reading_protocol_R279.md",
        "bibliographic_dossier_R279.md",
    ])
    def test_relatorio_presente_e_substancial(self, name):
        report = _require(VR / "_archive" / "relatorios" / name, "R279")
        text = report.read_text(encoding="utf-8")
        assert len(text) > 500, f"{name} suspeito de placeholder"
