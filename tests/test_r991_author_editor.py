"""R991: autor/editor de alto rigor; fixtures são texto sintético, sem LLM/rede."""
import importlib
import json

import pytest


def author_editor():
    assert importlib.util.find_spec("academic.author_editor"), "Módulo R991 ausente"
    return importlib.import_module("academic.author_editor")


SAMPLE = """\
# Introdução
Este estudo investiga um problema delimitado. A lacuna foi identificada na literatura.

# Objetivos
O objetivo geral é caracterizar o fenômeno. Os objetivos específicos incluem medir e comparar.

# Fundamentação Teórica
Conforme a teoria, os construtos se relacionam (Silva, 2024).

# Metodologia
Adotamos um desenho descritivo com amostragem aleatória.

# Resultados
Os resultados mostram uma tendência observada.

# Discussão
A discussão confronta os achados com a literatura.

# Conclusão
A conclusão sintetiza a contribuição e os limites.
"""


def test_manuscript_sections_have_canonical_order_and_moves():
    sections = author_editor().MANUSCRIPT_SECTIONS
    assert [s["key"] for s in sections] == [
        "titulo", "resumo", "introducao", "objetivos", "fundamentacao_teorica",
        "metodologia", "resultados", "discussao", "conclusao", "referencias"]
    for section in sections:
        assert section["role"] and section["moves"]
    assert any(s["key"] == "introducao" and "justificativa" in s["role"].lower() for s in sections)


def test_extract_structure_detects_present_and_missing_without_fabrication():
    result = author_editor().extract_structure(SAMPLE)
    present = result["present"]
    assert {"introducao", "objetivos", "fundamentacao_teorica", "metodologia",
            "resultados", "discussao", "conclusao"}.issubset(present)
    assert "referencias" in result["missing"] and "resumo" in result["missing"]
    assert "titulo" in result["missing"]
    assert result["order"] == [s for s in result["order"] if s in present]
    assert result["fabricated"] == []


def test_plain_text_without_headings_does_not_invent_sections():
    result = author_editor().extract_structure("Um parágrafo contínuo sem títulos de seção.")
    assert result["present"] == [] and result["fabricated"] == []
    assert result["missing"] == [s["key"] for s in author_editor().MANUSCRIPT_SECTIONS]


def test_style_fingerprint_is_structural_and_never_verbatim():
    fingerprint = author_editor().style_fingerprint(SAMPLE)
    assert "register" in fingerprint and "person" in fingerprint
    assert "hedging" in fingerprint and "connectives" in fingerprint
    assert "citation_density" in fingerprint and "type_token_ratio" in fingerprint
    assert fingerprint["verbatim_spans"] == []  # anti-plágio por construção
    assert fingerprint["anti_plagiarism"] is True
    assert "A lacuna foi identificada na literatura" not in json.dumps(fingerprint)


def test_reasoning_registry_maps_traditions_to_core_engines():
    registry = author_editor().reasoning_registry()
    required = {"axiomatico", "aristotelico", "cartesiano", "peirceano", "popperiano",
                "game_theory", "bayesiano", "causal", "dialetico", "fuzzy"}
    assert required.issubset(registry)
    for name, framework in registry.items():
        assert framework["engine"] and framework["scope"]
        assert framework["laws"] or framework["axioms"] or framework["lemmas"]
        assert framework["proves_empirical_truth"] is False
    assert "silogismo" in json.dumps(registry["aristotelico"], ensure_ascii=False).lower()
    assert "dúvida metódica" in json.dumps(registry["cartesiano"], ensure_ascii=False).lower()
    assert "minimax" in json.dumps(registry["game_theory"], ensure_ascii=False).lower()


def test_author_brief_without_sources_does_not_invent_references():
    brief = author_editor().author_brief("Como caracterizar o fenômeno X?")
    assert brief["status"] == "planned"
    assert brief["sections"] and brief["reasoning_plan"] and brief["style_plan"]
    assert brief["anti_plagiarism"]["verbatim_copy"] is False
    assert brief["search"] == "pending" and brief["references"] == []
    assert brief["scientific_acceptance"] is False and brief["human_review_required"] is True


def test_author_brief_with_sources_keeps_literal_evidence_only():
    sources = [{"id": "s1", "text": "Tendência observada em 12 amostras.", "provenance": "fixture"}]
    brief = author_editor().author_brief("Questão?", sources=sources)
    assert brief["search"] == "supplied"
    assert brief["references"][0]["source_id"] == "s1"
    # O plano não copia frases das fontes para o esboço de seções.
    assert "12 amostras" not in json.dumps(brief["sections"])


@pytest.mark.parametrize("kwargs", [
    {"topic": ""}, {"topic": None}, {"topic": "x" * 4001},
    {"topic": "t", "sources": "not-a-list"},
    {"topic": "t", "sources": [{"id": "s1", "text": "t", "provenance": "p", "extra": 1}]},
])
def test_author_brief_rejects_invalid_input(kwargs):
    with pytest.raises(ValueError):
        author_editor().author_brief(**kwargs)


def test_style_fingerprint_rejects_empty_or_non_text():
    with pytest.raises(ValueError):
        author_editor().style_fingerprint("")
    with pytest.raises(ValueError):
        author_editor().style_fingerprint(None)


def test_cli_author_editor_is_available_without_fallback(monkeypatch, capsys):
    from marceloclaro import scientific_lab as cli
    assert "author-editor" in cli.HELP
    monkeypatch.setattr(cli, "dispatch", lambda *a: pytest.fail("Fallback externo"))
    assert cli.main(["author-editor", "brief", "--topic", "Questão"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "planned" and payload["human_review_required"] is True


def test_build_references_from_oa_flattens_and_dedups_by_doi():
    oa = {"searches": [{"theme": "t", "sources": {
        "openalex": {"status": "ok", "results": [{"title": "Quantum computing", "year": 1998,
                                   "doi": "10.1088/0034-4885/61/2/002", "source": "openalex"}]},
        "crossref": {"status": "ok", "results": [{"title": "Quantum computing", "year": 1998,
                                  "doi": "10.1088/0034-4885/61/2/002", "source": "crossref"}]},
        "arxiv": {"status": "ok", "results": [{"title": "Quantum Computing: Vision and Challenges", "year": 2024,
                               "doi": None, "source": "arxiv"}]},
    }}]}
    refs = author_editor().build_references_from_oa(oa)
    assert len(refs) == 2  # DOI duplicado colapsado
    assert any(r["doi"] == "10.1088/0034-4885/61/2/002" for r in refs)
    assert any(r["doi"] is None and "arxiv" == r["source"] for r in refs)


def test_author_brief_accepts_verified_references_and_maps_to_sections():
    refs = [{"doi": "10.1088/0034-4885/61/2/002", "title": "Quantum computing",
             "year": 1998, "source": "openalex", "verified": True},
            {"doi": None, "title": "Quantum Computing: Vision and Challenges",
             "year": 2024, "source": "arxiv", "verified": False}]
    brief = author_editor().author_brief("Estado da computação quântica", bibliography=refs)
    assert brief["bibliography"] == refs
    assert set(brief["section_references"]["referencias"]) == {0, 1}
    assert brief["section_references"]["fundamentacao_teorica"] == [0, 1]
    assert brief["references_verified_count"] == 1  # só o DOI verificado
    assert brief["scientific_acceptance"] is False


def test_author_brief_rejects_references_without_required_fields():
    with pytest.raises(ValueError):
        author_editor().author_brief("t", bibliography=[{"title": "só título"}])
