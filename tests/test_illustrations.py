# -*- coding: utf-8 -*-
"""
Testes TDD — SPEC-018: Ilustrações Científicas e FigureHunter.
Todos offline (sem rede); a renderização PNG é opcional (INV-018.6).
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from illustrations import MermaidEngine, GraphifyEngine, MiraEngine, MIRA_CATALOG
from illustrations.mermaid_engine import _sanitize_label
from research.figure_hunter import ExtractedFigure, FigureHunter


# ----------------------------------------------------------------------
# MermaidEngine (REQ-018.1, INV-018.3, INV-018.6)
# ----------------------------------------------------------------------
class TestMermaidEngine:
    def test_flowchart_generates_valid_code(self, tmp_path):
        me = MermaidEngine(output_dir=str(tmp_path))
        fig = me.flowchart("Fluxo Teste", [("A", "B"), ("B", "C")])
        assert fig.code.startswith("graph TD")
        assert "-->" in fig.code

    def test_labels_never_contain_parentheses(self, tmp_path):
        # INV-018.3: parênteses quebram o parser Mermaid em labels
        me = MermaidEngine(output_dir=str(tmp_path))
        fig = me.flowchart("Parens", [("Executa (TDD)", "Valida (SDD)")])
        for line in fig.code.splitlines():
            if "[" in line:  # linhas de definição de nó
                label = line.split("[", 1)[1]
                assert "(" not in label and ")" not in label

    def test_sanitize_label(self):
        assert "(" not in _sanitize_label("Executa (TDD)")

    def test_mmd_always_preserved(self, tmp_path):
        # INV-018.6: .mmd sempre existe mesmo sem renderizador
        me = MermaidEngine(output_dir=str(tmp_path))
        fig = me.flowchart("Preserva", [("X", "Y")])
        me.render(fig)
        assert fig.mmd_path and Path(fig.mmd_path).exists()

    def test_mindmap_and_outline(self, tmp_path):
        me = MermaidEngine(output_dir=str(tmp_path))
        mm = me.mindmap("Mapa", "Raiz", {"Ramo": ["Folha1", "Folha2"]})
        assert mm.code.startswith("mindmap")
        fo = me.from_outline("Outline", ["Intro", "Método", "Resultados"])
        assert fo.code.count("-->") == 2

    def test_latex_figure_block(self, tmp_path):
        me = MermaidEngine(output_dir=str(tmp_path))
        fig = me.flowchart("Latex", [("A", "B")], caption="Legenda teste")
        block = fig.latex_figure()
        assert "\\begin{figure}" in block and "Legenda teste" in block


# ----------------------------------------------------------------------
# GraphifyEngine (REQ-018.2)
# ----------------------------------------------------------------------
class TestGraphifyEngine:
    TEXTS = {
        "doc1": "agentes metacognição memória atenção orquestração " * 30,
        "doc2": "memória episódica atenção transformador agentes " * 25,
    }

    def test_build_graph(self, tmp_path):
        ge = GraphifyEngine(output_dir=str(tmp_path))
        g = ge.build(self.TEXTS)
        assert len(g.nodes) > 0 and len(g.edges) > 0
        # nós ordenados por frequência (value decrescente)
        values = [n["value"] for n in g.nodes]
        assert values == sorted(values, reverse=True)

    def test_edges_min_cooccurrence(self, tmp_path):
        ge = GraphifyEngine(output_dir=str(tmp_path))
        g = ge.build(self.TEXTS)
        assert all(e["value"] >= 2 for e in g.edges)

    def test_export_three_artifacts(self, tmp_path):
        ge = GraphifyEngine(output_dir=str(tmp_path))
        g = ge.build(self.TEXTS)
        paths = ge.export(g)
        for key in ("json", "html", "report"):
            assert Path(paths[key]).exists()
        data = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
        assert "nodes" in data and "edges" in data

    def test_report_has_hubs(self, tmp_path):
        ge = GraphifyEngine(output_dir=str(tmp_path))
        g = ge.build(self.TEXTS)
        assert "Conceitos-chave" in g.report


# ----------------------------------------------------------------------
# MiraEngine (REQ-018.3, INV-018.1, INV-018.2)
# ----------------------------------------------------------------------
class TestMiraEngine:
    def test_metaphor_selection(self, tmp_path):
        mi = MiraEngine(output_dir=str(tmp_path))
        assert mi.pick_metaphor("orquestração de agentes").key == "orquestracao"
        assert mi.pick_metaphor("pipeline de dados em fluxo").key == "pipeline"
        assert mi.pick_metaphor("janela de contexto e memoria").key == "contexto"
        assert mi.pick_metaphor("debito tecnico com juros").key == "debito"

    def test_regra_zero_loop_infinito(self, tmp_path):
        # INV-018.1: toda animação do catálogo usa loop infinito
        for met in MIRA_CATALOG:
            assert "infinite" in met.svg, f"metáfora {met.key} sem loop perpétuo"

    def test_title_max_6_words(self, tmp_path):
        # INV-018.2
        mi = MiraEngine(output_dir=str(tmp_path))
        card = mi.card("Um Título Extremamente Longo Que Passa De Seis Palavras", "x")
        assert len(card.title.split()) <= 6

    def test_render_self_contained_html(self, tmp_path):
        mi = MiraEngine(output_dir=str(tmp_path))
        card = mi.render(mi.card("Pipeline de Produção", "fluxo de etapas"))
        html = Path(card.html_path).read_text(encoding="utf-8")
        assert "anim-stage" in html and "Replay" in html and "infinite" in html

    def test_illustrate_sections(self, tmp_path):
        mi = MiraEngine(output_dir=str(tmp_path))
        cards = mi.illustrate_sections({"Seção A": "pipeline", "Seção B": "orquestração"})
        assert len(cards) == 2
        assert all(c.html_path and Path(c.html_path).exists() for c in cards)


# ----------------------------------------------------------------------
# FigureHunter (REQ-018.4, REQ-018.5, INV-018.4, INV-018.5)
# ----------------------------------------------------------------------
class TestFigureHunter:
    def _fig(self, **kw):
        base = dict(image_path="/tmp/x.png", source_pdf="/tmp/paper.pdf", page=3,
                    caption="Arquitetura do sistema.", authors="SILVA, J.; SOUZA, M.",
                    year="2025", title="Multi-agent metacognition", doi="10.1000/xyz")
        base.update(kw)
        return ExtractedFigure(**base)

    def test_abnt_and_apa_always_present(self):
        # INV-018.5: mesmo sem autor, a fonte é explicitada
        fig = self._fig(authors="", year="", title="", doi="")
        assert "AUTOR DESCONHECIDO" in fig.abnt()
        assert "Unknown" in fig.apa()

    def test_abnt_format(self):
        fig = self._fig()
        abnt = fig.abnt()
        assert abnt.startswith("SILVA, J.") and "2025" in abnt and "DOI:" in abnt

    def test_latex_figure_cites_source(self):
        fig = self._fig()
        block = fig.latex_figure()
        assert "\\caption" in block and "Fonte:" in block and "2025" in block

    def test_catalog_written(self, tmp_path):
        hunter = FigureHunter(images_dir=str(tmp_path))
        hunter.figures = [self._fig(image_path=str(tmp_path / "f1.png"))]
        catalog = hunter.write_catalog()
        assert catalog and Path(catalog).exists()
        content = Path(catalog).read_text(encoding="utf-8")
        assert "ABNT" in content and "APA" in content and "```latex" in content
        assert (tmp_path / "figuras.json").exists()

    def test_empty_catalog_returns_none(self, tmp_path):
        hunter = FigureHunter(images_dir=str(tmp_path))
        assert hunter.write_catalog() is None

    def test_harvest_missing_folder(self, tmp_path):
        hunter = FigureHunter()
        assert hunter.harvest_production(str(tmp_path / "nao-existe")) == []

    @pytest.mark.skipif(
        not list((ROOT / "producao_cientifica").rglob("pesquisa/pdfs/*.pdf"))
        if (ROOT / "producao_cientifica").exists() else True,
        reason="nenhum PDF real disponível")
    def test_harvest_real_production(self, tmp_path):
        # REQ-018.4 com PDFs reais baixados pelo ResearchHub
        prod = next(p.parent.parent.parent for p in
                    (ROOT / "producao_cientifica").rglob("pesquisa/pdfs/*.pdf"))
        hunter = FigureHunter()
        figs = hunter.harvest_production(str(prod))
        assert isinstance(figs, list)  # pode ser 0 se PDFs sem imagens grandes


# ----------------------------------------------------------------------
# Integração com o orquestrador (REQ-018.6)
# ----------------------------------------------------------------------
class TestOrchestratorIllustrations:
    def test_knowledge_graph_method(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        out = orch.knowledge_graph(
            {"a": "agentes memória atenção " * 30},
            output_dir=str(tmp_path / "grafo"))
        assert out["nodes"] > 0 and Path(out["paths"]["html"]).exists()

    def test_illustrate_method(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        orch = MarceloClaroOrchestrator(auto_load_agents=False)
        report = orch.illustrate(
            str(tmp_path),
            sections={"Orquestração": "coordenação de agentes"},
            outline=["Introdução", "Método", "Conclusão"])
        assert "mermaid" in report and report.get("mira_cards")
        assert (tmp_path / "ilustracoes").exists()
