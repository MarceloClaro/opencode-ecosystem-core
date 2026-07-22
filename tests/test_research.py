# -*- coding: utf-8 -*-
"""
Testes TDD do subsistema Research (SPEC-017).
Todos os testes rodam OFFLINE (sem rede), usando registros sintéticos,
exceto quando marcados como integração de rede (pulados por padrão).
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.searchers import PaperRecord, MultiSearcher, ALL_SEARCHERS
from research.fichamento import (CitationFormatter, CriticalAnalyzer,
                                 FichamentoWriter)
from research.pdf2md import Pdf2Markdown
from research.downloader import PaperDownloader
from research.hub import ResearchHub


# ----------------------------------------------------------------------
def _rec(**kw) -> PaperRecord:
    base = dict(
        title="Metacognitive Coordination in Multi-Agent LLM Systems",
        authors=["Silva, João", "Santos, Maria", "Doe, John"],
        year=2024,
        doi="10.1234/mca.2024.001",
        venue="Journal of Autonomous Agents",
        abstract=("We propose a metacognitive coordination layer for "
                  "multi-agent LLM systems with experiments and open source "
                  "code for reproducibility. Results show significant gains."),
        source="arxiv",
        url="https://example.org/paper",
        citations=150,
    )
    base.update(kw)
    return PaperRecord(**base)


TEMA = "metacognição em sistemas multiagentes LLM"


# ----------------------------------------------------------------------
# REQ-017.1/2 — plataformas registradas
# ----------------------------------------------------------------------
class TestSearchers:
    def test_plataformas_essenciais_registradas(self):
        for nome in ("arxiv", "openalex", "crossref", "semantic_scholar",
                     "europepmc", "scielo", "github", "kaggle"):
            assert nome in ALL_SEARCHERS, f"plataforma ausente: {nome}"

    def test_multisearcher_seleciona_plataformas(self):
        ms = MultiSearcher(platforms=["arxiv", "github"])
        assert len(ms.searchers) == 2

    def test_paper_record_identifier(self):
        assert _rec().identifier() == "10.1234/mca.2024.001"
        assert _rec(doi="", arxiv_id="2510.01285").identifier() == "2510.01285"


# ----------------------------------------------------------------------
# REQ-017.7 — ABNT NBR 6023:2018 / APA 7 / NBR 10520:2023
# ----------------------------------------------------------------------
class TestCitations:
    def test_abnt_sobrenome_maiusculo_e_doi(self):
        ref = CitationFormatter.abnt(_rec())
        assert "SILVA, J." in ref
        assert "SANTOS, M." in ref
        assert "DOI: https://doi.org/10.1234/mca.2024.001" in ref
        assert "2024" in ref

    def test_apa_ampersand_e_ano_entre_parenteses(self):
        ref = CitationFormatter.apa(_rec())
        assert "& Doe, J." in ref
        assert "(2024)" in ref
        assert "https://doi.org/10.1234/mca.2024.001" in ref

    def test_citacao_nbr_10520_et_al(self):
        cit = CitationFormatter.abnt_citacao_direta(_rec())
        assert cit == "(Silva et al., 2024, p. N)"

    def test_bibtex_valido(self):
        bib = CitationFormatter.bibtex(_rec(), "silva2024")
        assert bib.startswith("@article{silva2024,")
        assert "doi = {10.1234/mca.2024.001}" in bib


# ----------------------------------------------------------------------
# REQ-017.5 — análise crítica com aderência ao tema
# ----------------------------------------------------------------------
class TestCriticalAnalyzer:
    def test_aderencia_alta_para_artigo_relevante(self):
        an = CriticalAnalyzer("metacognitive multi-agent LLM systems")
        result = an.analyze(_rec())
        assert result.aderencia_score >= 4.0
        assert result.pontos_fortes and result.limitacoes and result.lacunas
        assert "LEITURA" in result.veredicto

    def test_aderencia_baixa_para_artigo_irrelevante(self):
        an = CriticalAnalyzer("quantum error correction superconducting qubits")
        rec = _rec(title="Cooking recipes dataset",
                   abstract="A dataset of pasta recipes.")
        result = an.analyze(rec)
        assert result.aderencia_score < 4.0
        assert "OPCIONAL" in result.veredicto


# ----------------------------------------------------------------------
# REQ-017.5/6 — fichamento e resenha em arquivos
# ----------------------------------------------------------------------
class TestFichamentoWriter:
    @pytest.fixture()
    def writer(self, tmp_path):
        return FichamentoWriter(str(tmp_path / "fich"), str(tmp_path / "res"),
                                TEMA)

    def test_fichamento_tres_camadas(self, writer):
        fulltext = ("We propose a novel framework. " * 10 +
                    "Results show significant improvements in coordination, "
                    "communication and metacognition across all benchmarks "
                    "evaluated in our extensive experimental campaign here.")
        path = writer.fichamento(_rec(), fulltext, "artigo.md")
        text = Path(path).read_text(encoding="utf-8")
        assert "## 3. Fichamento bibliográfico" in text
        assert "## 4. Fichamento de citação" in text
        assert "## 5. Fichamento crítico" in text
        assert "NBR 6023:2018" in text and "APA (7ª ed.)" in text
        assert "Aderência ao tema" in text

    def test_resenha_critica_com_veredicto(self, writer):
        path = writer.resenha(_rec(), "")
        text = Path(path).read_text(encoding="utf-8")
        assert "Resenha crítica" in text
        assert "veredicto" in text.lower()
        assert "**ABNT:**" in text and "**APA 7:**" in text


# ----------------------------------------------------------------------
# REQ-017.3 — downloader com validação %PDF-
# ----------------------------------------------------------------------
class TestDownloader:
    def test_rejeita_repositorios(self, tmp_path):
        dl = PaperDownloader(str(tmp_path))
        repo = _rec(extra={"type": "repository"})
        results = dl.download([repo])
        assert len(results) == 1 and not results[0].ok

    def test_sem_pdf_url_falha_com_erro_claro(self, tmp_path):
        dl = PaperDownloader(str(tmp_path))
        dl.scihub_cli = None  # força ausência do CLI
        rec = _rec(pdf_url="", doi="")
        results = dl.download([rec])
        assert not results[0].ok


# ----------------------------------------------------------------------
# REQ-017.4 — conversão PDF→MD
# ----------------------------------------------------------------------
class TestPdf2Md:
    def test_converte_pdf_minimo(self, tmp_path):
        # PDF mínimo válido gerado via fpdf2 (pré-instalada na sandbox);
        # se indisponível, pula.
        try:
            from fpdf import FPDF
        except ImportError:
            pytest.skip("fpdf2 indisponível")
        pdf_path = tmp_path / "mini.pdf"
        doc = FPDF()
        doc.add_page()
        doc.set_font("helvetica", size=14)
        doc.cell(0, 10, "Metacognition improves coordination in agents.")
        doc.output(str(pdf_path))

        conv = Pdf2Markdown(str(tmp_path / "md"))
        md = conv.convert(str(pdf_path), _rec())
        assert md is not None
        text = Path(md).read_text(encoding="utf-8")
        assert text.startswith("---")           # frontmatter YAML
        assert "Metacognition" in text

    def test_pdf_inexistente_retorna_none(self, tmp_path):
        conv = Pdf2Markdown(str(tmp_path / "md"))
        assert conv.convert(str(tmp_path / "nao_existe.pdf")) is None


# ----------------------------------------------------------------------
# REQ-017.8/9 — ResearchHub offline (sem download) e manifest
# ----------------------------------------------------------------------
class TestResearchHubOffline:
    def test_pasta_unica_e_manifest(self, tmp_path, monkeypatch):
        hub = ResearchHub(TEMA, production_folder=str(tmp_path / "producao"))
        # monkeypatch: substitui a busca em rede por registros sintéticos
        fake = [_rec(),
                _rec(title="Game-theoretic reasoning for agent societies",
                     doi="10.5555/gt.2023", year=2023,
                     authors=["Nash, John"]),
                _rec(title="ecosystem-core", doi="", year=None,
                     extra={"type": "repository"},
                     url="https://github.com/x/y",
                     abstract="Repo de código")]
        monkeypatch.setattr(hub.searcher, "search",
                            lambda q, limit_per_platform=5: fake)
        manifest = hub.run(max_papers=2, download=False)

        pesquisa = tmp_path / "producao" / "pesquisa"
        assert (pesquisa / "RESEARCH_MANIFEST.json").exists()
        assert (pesquisa / "referencias_abnt.md").exists()
        assert (pesquisa / "referencias_apa.md").exists()
        assert (pesquisa / "referencias.bib").exists()
        assert (pesquisa / "repositorios.md").exists()
        assert len(list((pesquisa / "fichamentos").glob("*.md"))) == 2
        assert len(list((pesquisa / "resenhas").glob("*.md"))) == 2
        assert manifest["resumo"]["artigos_selecionados"] == 2
        assert manifest["resumo"]["repositorios_datasets"] == 1
        # INV-017.3: correspondência fichamentos ↔ referências
        abnt = (pesquisa / "referencias_abnt.md").read_text(encoding="utf-8")
        assert "NASH, J." in abnt and "SILVA, J." in abnt
        # checksums presentes
        data = json.loads((pesquisa / "RESEARCH_MANIFEST.json")
                          .read_text(encoding="utf-8"))
        assert data["files_sha256"]
        assert "ABNT NBR 6023:2018" in data["normas"]

    def test_referencias_abnt_alfabeticas(self, tmp_path, monkeypatch):
        hub = ResearchHub(TEMA, production_folder=str(tmp_path / "p2"))
        fake = [_rec(title="Zeta agents", authors=["Zappa, Frank"], doi="10.1/z"),
                _rec(title="Alpha agents", authors=["Abreu, Ana"], doi="10.1/a")]
        monkeypatch.setattr(hub.searcher, "search",
                            lambda q, limit_per_platform=5: fake)
        hub.run(max_papers=2, download=False)
        abnt = (tmp_path / "p2" / "pesquisa" / "referencias_abnt.md").read_text(
            encoding="utf-8")
        assert abnt.index("ABREU") < abnt.index("ZAPPA")


# ----------------------------------------------------------------------
# REQ-017.10 — integração com o orquestrador
# ----------------------------------------------------------------------
class TestOrchestratorIntegration:
    def test_orquestrador_expoe_metodos_research(self):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        assert hasattr(MarceloClaroOrchestrator, "research")
        assert hasattr(MarceloClaroOrchestrator, "research_search")
