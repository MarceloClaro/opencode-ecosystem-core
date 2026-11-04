"""R1053-B — pacote de submissão com LaTeX/DOCX, checklist e declarações."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scientific_lab import submission


def make_project(tmp_path: Path) -> Path:
    out = tmp_path / "projeto"
    manuscript = out / "06_manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "manuscript.md").write_text(
        "# Evidências sobre o tema\n\n"
        "## Resumo\n\nTexto do resumo.\n\n"
        "## 1. Introdução\n\nTexto da introdução.\n",
        encoding="utf-8",
    )
    (manuscript / "references.json").write_text(json.dumps({
        "records": [{
            "article_id": "ART-0001",
            "title": "Estudo A",
            "authors": ["Ana Silva", "Bruno Souza"],
            "year": 2024,
            "venue": "Revista de Teste",
            "doi": "10.1000/a",
            "url": "https://example.org/a",
        }],
    }), encoding="utf-8")
    return out


def test_build_creates_markdown_bib_checklist_and_declarations(tmp_path):
    out = make_project(tmp_path)
    result = submission.build(out, journal="Revista Teste", compile_pdf=False)
    sub = out / "10_submission"
    assert result["human_review_required"] is True
    assert result["truth_claim"] is False
    assert (sub / "manuscript.md").exists()
    bib = (sub / "references.bib").read_text(encoding="utf-8")
    assert "Estudo A" in bib and "10.1000/a" in bib
    checklist = json.loads((sub / "journal-checklist.json").read_text(encoding="utf-8"))
    assert checklist["status"] == "pending_human"
    assert all(item["status"] == "pending_human" for item in checklist["items"])
    declarations = json.loads((sub / "declarations.json").read_text(encoding="utf-8"))
    assert declarations["status"] == "pending_human"
    assert all(
        item["status"] == "pending_human"
        for item in declarations["fields"].values()
    )
    assert "PENDENTE_HUMANO" in (sub / "cover-letter.md").read_text(encoding="utf-8")
    assert "PENDENTE_HUMANO" in (sub / "declarations.md").read_text(encoding="utf-8")
    manifest = json.loads((sub / "submission-manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] in {"completed", "partial"}
    assert manifest["truth_claim"] is False
    assert manifest["files"]


def test_build_copies_figures_and_tables(tmp_path):
    out = make_project(tmp_path)
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "figura.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")
    tables = tmp_path / "tables"
    tables.mkdir()
    (tables / "tabela.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    submission.build(
        out, journal="Revista Teste", figures_dir=figures,
        tables_dir=tables, compile_pdf=False,
    )
    sub = out / "10_submission"
    assert (sub / "figures/figura.png").exists()
    assert (sub / "tables/tabela.csv").exists()
    manifest = json.loads((sub / "submission-manifest.json").read_text(encoding="utf-8"))
    assert any(item["copied"] for item in manifest["figures"])
    assert any(item["copied"] for item in manifest["tables"])


def test_build_requires_manuscript(tmp_path):
    with pytest.raises(ValueError):
        submission.build(tmp_path, compile_pdf=False)


def test_latex_escape_and_bib_without_authors():
    assert submission._latex_escape("A & B_100%") == r"A \& B\_100\%"
    bib = submission.build_bib({"records": [{
        "title": "Título", "authors": [], "year": 2024,
        "venue": "Revista", "doi": None, "url": None,
    }]})
    assert "Autoria não informada" in bib


def test_refresh_integrates_submission_package(tmp_path):
    from research.searchers import PaperRecord
    from scientific_lab import research_project as rp

    class FakeSearcher:
        def __init__(self, platforms=None):
            self.platforms = platforms

        def search(self, query, limit_per_platform=5):
            return [PaperRecord(
                title="Estudo para submissão",
                authors=["Ana Silva"],
                year=2024,
                doi="10.1000/sub",
                url="https://example.org/sub",
                abstract=(
                    "Este estudo descreve um experimento controlado sobre o tema. "
                    "Os resultados indicam uma associação descritiva."
                ),
                venue="Revista de Teste",
                source="openalex",
            )]

    out = tmp_path / "projeto"
    rp.run(
        "tema para submissão",
        out,
        question="Quais evidências descrevem o tema para submissão?",
        sources=["openalex"],
        searcher_factory=FakeSearcher,
    )
    result = rp.refresh_project(
        out, submission_package=True, journal="Revista Teste",
    )
    assert result["stages"]["submission"] == "completed"
    assert result["counts"]["submission_files"] > 0
    assert (out / "10_submission/submission-manifest.json").exists()
    audit = json.loads((out / "05_audit/audit-report.json").read_text(encoding="utf-8"))
    checks = {check["id"]: check["status"] for check in audit["checks"]}
    assert checks["submission_package"] == "pass"
    assert rp.verify_manifest(out)["status"] == "pass"


def test_cli_submission_routes(monkeypatch, tmp_path, capsys):
    from scientific_lab import research_project as rp
    from scientific_lab.native import cli as native_cli

    calls = []

    def fake_refresh(out, **kwargs):
        calls.append((out, kwargs))
        return {"status": "completed_pending_external_validation"}

    monkeypatch.setattr(rp, "refresh_project", fake_refresh)
    code = native_cli.dispatch("research", [
        "submission", "--out", str(tmp_path / "p"),
        "--journal", "Revista Teste",
    ])
    assert code == 0
    assert len(calls) == 1
    out, kwargs = calls[0]
    assert Path(out) == tmp_path / "p"
    assert kwargs["submission_package"] is True
    assert kwargs["journal"] == "Revista Teste"
    assert json.loads(capsys.readouterr().out)["status"] == "completed_pending_external_validation"
