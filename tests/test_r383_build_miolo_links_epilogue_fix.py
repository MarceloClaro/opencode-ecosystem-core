# -*- coding: utf-8 -*-
"""Testes de regressão — SPEC-935-R383.

Prova que scripts/build_miolo.py::extract_fragment_content() não descarta
mais conteúdo narrativo real que aparece depois da linha "↪ Links:" —
bug real encontrado ao investigar por que scripts/regenerate_vic_cont_r376.py
produzia CONT-07.tex divergente do committado (a divergência era perda de
conteúdo, não uma edição manual pós-geração como se supôs inicialmente).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from build_miolo import extract_fragment_content, parse_fragments, MOLAMBUROS  # noqa: E402


def _frag(lines):
    return {"id": "TEST-00", "lines": lines, "title": "## TEST-00 — Teste"}


class TestExtractFragmentContentComEpilogo:
    def test_links_como_ultimo_elemento_comportamento_inalterado(self):
        frag = _frag([
            "Parágrafo principal do fragmento.",
            "",
            "**↪ Links:** DOC-01 | CONT-05",
        ])
        content, links = extract_fragment_content(frag)
        assert "Parágrafo principal" in content
        assert "↪ Links:" not in content
        assert "DOC-01" in links

    def test_conteudo_apos_links_e_preservado_no_corpo(self):
        frag = _frag([
            "Parágrafo principal do fragmento.",
            "",
            "**↪ Links:** DOC-01 | CONT-05",
            "",
            "---",
            "",
            "### Epílogo real",
            "",
            "Este texto não pode desaparecer.",
        ])
        content, links = extract_fragment_content(frag)
        assert "Parágrafo principal" in content
        assert "Este texto não pode desaparecer" in content
        assert "↪ Links:" in content, (
            "quando há conteúdo real depois da linha de Links, ela deve "
            "permanecer no corpo em sua posição original, não ser "
            "silenciosamente descartada junto com o epílogo"
        )

    def test_links_seguida_apenas_de_regra_horizontal_ainda_e_extraida(self):
        frag = _frag([
            "Parágrafo principal.",
            "",
            "**↪ Links:** DOC-01",
            "",
            "---",
            "",
        ])
        content, links = extract_fragment_content(frag)
        assert "↪ Links:" not in content
        assert "DOC-01" in links

    def test_sem_linha_de_links_retorna_tudo_como_conteudo(self):
        frag = _frag(["Só conteúdo, sem seção de links."])
        content, links = extract_fragment_content(frag)
        assert content == "Só conteúdo, sem seção de links."
        assert links == ""


class TestRegressaoManuscritoReal:
    """Confirma, sobre o molambudos.md real, que os 4 fragmentos afetados
    (achados por varredura completa do documento) não perdem mais conteúdo."""

    def test_fragmentos_com_epilogo_pos_links_preservam_todo_o_texto(self):
        md = MOLAMBUROS.read_text(encoding="utf-8")
        _, fragments = parse_fragments(md)
        frag_map = {f["id"]: f for f in fragments}

        afetados = ["CONT-03", "CONT-07", "MEM-27", "LUC-Escolha"]
        for fid in afetados:
            frag = frag_map.get(fid)
            if frag is None:
                continue
            lines = frag["lines"]
            links_idx = next(
                (i for i, l in enumerate(lines) if "↪ Links:" in l), None
            )
            assert links_idx is not None, f"{fid}: linha de Links não encontrada"
            trailing = [
                l for l in lines[links_idx + 1:] if l.strip() and l.strip() != "---"
            ]
            assert trailing, f"{fid}: era esperado ter conteúdo após Links"

            content, _ = extract_fragment_content(frag)
            for line in trailing:
                # cada palavra significativa da cauda deve sobreviver no corpo
                for word in line.split():
                    if len(word) >= 6:
                        assert word in content, (
                            f"{fid}: palavra {word!r} da cauda pós-Links "
                            "desapareceu do conteúdo extraído"
                        )

    def test_fragmentos_sem_epilogo_continuam_extraindo_links_normalmente(self):
        md = MOLAMBUROS.read_text(encoding="utf-8")
        _, fragments = parse_fragments(md)
        frag_map = {f["id"]: f for f in fragments}

        # amostra de fragmentos onde Links é de fato o último elemento
        for fid in ("CONT-05", "CONT-06", "CONT-08"):
            frag = frag_map.get(fid)
            if frag is None:
                continue
            content, links = extract_fragment_content(frag)
            assert links, f"{fid}: esperava linha de links extraída normalmente"
            assert "↪ Links:" not in content
