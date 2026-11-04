"""R1052 — atualização de projeto com triagem humana, texto integral e integridade."""
from __future__ import annotations

import json
from pathlib import Path

from research.searchers import PaperRecord
from scientific_lab import research_project as rp


def rec(**kw):
    base = dict(
        title="Estudo A sobre o tema",
        authors=["Ana Silva"],
        year=2024,
        doi="10.1000/a",
        arxiv_id=None,
        url="https://example.org/a",
        pdf_url=None,
        abstract=(
            "Este estudo descreve um experimento controlado sobre o tema. "
            "Os resultados indicam uma associação descritiva, sem inferência causal."
        ),
        venue="Revista de Teste",
        source="openalex",
        citations=5,
        extra={},
    )
    base.update(kw)
    return PaperRecord(**base)


class FakeSearcher:
    def __init__(self, platforms=None):
        self.platforms = platforms

    def search(self, query, limit_per_platform=5):
        return [rec()]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def make_project(tmp_path: Path) -> Path:
    out = tmp_path / "projeto"
    result = rp.run(
        "tema controlado",
        out,
        question="Quais evidências disponíveis descrevem o tema controlado?",
        sources=["openalex"],
        searcher_factory=FakeSearcher,
    )
    assert result["status"] == "completed_pending_external_validation"
    return out


def make_fulltext(tmp_path: Path) -> Path:
    texts = tmp_path / "texts"
    texts.mkdir()
    (texts / "estudo-a.md").write_text(
        "# Estudo A\n\nDOI: 10.1000/a\n\n"
        "Este estudo descreve um experimento controlado sobre o tema e "
        "apresenta resultados descritivos sem inferência causal. "
        "A amostra incluiu participantes adultos e o desfecho foi medido "
        "no mesmo período.\n\n"
        "Os autores concluem que o resultado é exploratório e não permite "
        "generalização para outras populações.\n",
        encoding="utf-8",
    )
    return texts


def approval_for(out: Path, tmp_path: Path) -> Path:
    template = read_json(out / "07_validation/fulltext-approval.template.json")
    candidates = read_json(out / "03_evidence/fulltext-candidates.json")["candidates"]
    assert candidates
    template["reviewer"] = "Revisor Teste"
    template["reviewed_at"] = "2026-11-04T12:00:00Z"
    template["decision"] = "approved"
    template["human_confirmation"] = True
    template["approved_claim_ids"] = [candidates[0]["claim_id"]]
    path = tmp_path / "approval.json"
    path.write_text(json.dumps(template), encoding="utf-8")
    return path


def test_refresh_generates_fulltext_candidates_without_approval(tmp_path):
    out = make_project(tmp_path)
    texts = make_fulltext(tmp_path)
    result = rp.refresh_project(out, fulltext_dir=texts)
    assert result["counts"]["fulltext_candidates"] >= 1
    assert result["stages"]["fulltext"] == "completed_pending_human"
    assert (out / "03_evidence/fulltext-candidates.json").exists()
    assert (out / "07_validation/fulltext-approval.template.json").exists()
    audit = read_json(out / "05_audit/audit-report.json")
    assert audit["status"] == "pass_with_pending_human"
    assert rp.verify_manifest(out)["status"] == "pass"


def test_refresh_with_human_approval_creates_verified_evidence(tmp_path):
    out = make_project(tmp_path)
    texts = make_fulltext(tmp_path)
    rp.refresh_project(out, fulltext_dir=texts)
    approval = approval_for(out, tmp_path)
    result = rp.refresh_project(
        out, fulltext_dir=texts, fulltext_approval=approval,
    )
    assert result["counts"]["fulltext_verified"] >= 1
    claims = read_json(out / "03_evidence/claims.json")["claims"]
    fulltext_claims = [claim for claim in claims if "-FT-" in claim["id"]]
    assert fulltext_claims
    gate = read_json(out / "03_evidence/claim-gate.json")
    assert gate["truth_claim"] is False
    graph = read_json(out / "07_artifacts/evidence_graph/research-evidence-graph.json")
    assert graph["verified_edge_count"] >= 1
    manuscript = (out / "06_manuscript/manuscript.md").read_text(encoding="utf-8")
    assert "Evidências em texto integral" in manuscript
    assert "Revisor Teste" in manuscript
    assert rp.verify_manifest(out)["status"] == "pass"

    # idempotência: a mesma aprovação não duplica annotations
    annotations = list((out / "09_provenance/evidence_annotations").glob("*.json"))
    matching = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in annotations
        if json.loads(path.read_text(encoding="utf-8")).get("claim_id")
        == fulltext_claims[0]["id"]
    ]
    assert len(matching) == 1


def test_refresh_with_retraction_removes_claims_and_marks_study(tmp_path):
    out = make_project(tmp_path)

    def checker(doi):
        return {
            "status": "retracted",
            "updates": [{"relation": "is-retracted-by", "id": "10.1000/notice"}],
            "checked_at": "2026-11-04T12:00:00Z",
            "response_sha256": "a" * 64,
        }

    result = rp.refresh_project(
        out, check_integrity=True, integrity_checker=checker,
    )
    assert result["counts"]["retracted_studies"] >= 1
    studies = [
        read_json(path)
        for path in (out / "01_sources/systematic_review/studies").glob("*.json")
    ]
    assert any(study.get("integrity_status") == "retracted" for study in studies)
    claims = read_json(out / "03_evidence/claims.json")["claims"]
    assert claims == []
    gaps = read_json(out / "03_evidence/gaps.json")["gaps"]
    assert any(gap["reason"] == "retracted_study" for gap in gaps)
    assert result["status"] in {"partial", "blocked"}
    assert rp.verify_manifest(out)["status"] == "pass"


def test_cli_refresh_routes(monkeypatch, tmp_path, capsys):
    from scientific_lab.native import cli as native_cli

    calls = []

    def fake_refresh(out, **kwargs):
        calls.append((out, kwargs))
        return {"status": "completed_pending_external_validation"}

    monkeypatch.setattr(rp, "refresh_project", fake_refresh)
    code = native_cli.dispatch("research", [
        "refresh", "--out", str(tmp_path / "p"),
        "--fulltext-dir", str(tmp_path / "texts"),
        "--check-integrity", "--max-integrity-checks", "3",
    ])
    assert code == 0
    assert len(calls) == 1
    out, kwargs = calls[0]
    assert Path(out) == tmp_path / "p"
    assert kwargs["check_integrity"] is True
    assert kwargs["max_integrity_checks"] == 3
    assert json.loads(capsys.readouterr().out)["status"] == "completed_pending_external_validation"
