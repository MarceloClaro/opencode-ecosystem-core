"""R1051 — pesquisador científico ponta a ponta, file-first e anti-overclaim."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from research.searchers import PaperRecord


def rec(**kw):
    base = dict(
        title="Evidência sobre o tema",
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
        return [
            rec(title="Estudo A", doi="10.1000/a", source="openalex"),
            rec(title="Estudo A duplicado", doi="10.1000/a", source="crossref"),
            rec(
                title="Estudo B sem resumo",
                doi="10.1000/b",
                source="europepmc",
                abstract="",
            ),
            rec(
                title="Estudo C sem DOI",
                doi=None,
                source="arxiv",
                url="https://arxiv.org/abs/9999.00001",
                abstract=(
                    "O preprint apresenta uma revisão narrativa do tema. "
                    "Não há dados primários nem teste de hipótese."
                ),
            ),
        ]


class BombSearcher:
    def __init__(self, platforms=None):
        raise AssertionError("o dry-run não pode instanciar buscador")


class FailingSearcher:
    def __init__(self, platforms=None):
        self.platforms = platforms

    def search(self, query, limit_per_platform=5):
        raise RuntimeError("network unavailable")


class SlowSearcher:
    def __init__(self, platforms=None):
        self.platforms = platforms

    def search(self, query, limit_per_platform=5):
        import time
        time.sleep(2)
        return [rec()]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_dry_run_does_not_instantiate_searcher_and_writes_contract(tmp_path):
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    result = rp.run("saúde mental em estudantes", out, dry_run=True,
                    searcher_factory=BombSearcher)

    assert result["status"] == "planned"
    contract = read_json(out / "00_contract/retrieval-contract.json")
    for field in (
        "contract_id", "theme", "question", "question_status", "intent",
        "target_entity", "accepted_identifiers", "databases", "filters",
        "expected_fields", "pagination", "budget", "provenance",
        "untrusted_data_policy", "missing_constraints",
        "clarification_required", "status",
    ):
        assert field in contract
    assert contract["question_status"] == "provisional_from_theme"
    assert contract["clarification_required"] is True
    assert contract["status"] == "draft"
    assert not list((out / "01_sources/metadata").glob("search-*.json"))
    assert rp.verify_manifest(out)["status"] == "pass"


def test_full_run_builds_deduplicated_evidence_and_manuscript(tmp_path):
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    result = rp.run(
        "saúde mental em estudantes",
        out,
        question="Quais evidências disponíveis descrevem a saúde mental em estudantes?",
        sources=["openalex", "crossref", "europepmc", "arxiv"],
        searcher_factory=FakeSearcher,
    )

    assert result["status"] == "completed_pending_external_validation"
    assert result["counts"]["records_retrieved"] == 4
    assert result["counts"]["unique_studies"] == 3
    assert result["counts"]["duplicates_removed"] == 1
    assert result["counts"]["claims"] == 2
    assert result["counts"]["blocked_claims"] == 0

    triage = read_json(out / "02_screening/triage.json")
    assert len(triage["studies"]) == 3
    assert triage["human_review_required"] is True
    assert all(
        item["decision"] in {"candidate_for_human_screening", "uncertain_for_human_screening"}
        for item in triage["studies"]
    )
    assert all(item["screening_status"] == "pending" for item in triage["studies"])

    records = read_json(out / "01_sources/source-records.json")
    abstracts = {item["article_id"]: item["abstract"] for item in records["records"]}
    claims = read_json(out / "03_evidence/claims.json")
    assert len(claims["claims"]) == 2
    for claim in claims["claims"]:
        for ev in claim["evidence"]:
            assert ev["quote"] in abstracts[ev["source_id"]]
            assert len(ev["source_sha256"]) == 64

    gate = read_json(out / "03_evidence/claim-gate.json")
    assert gate["status"] == "candidate"
    assert gate["truth_claim"] is False
    assert gate["confidence_promoted"] is False

    manuscript = (out / "06_manuscript/manuscript.md").read_text(encoding="utf-8")
    for heading in (
        "## Resumo", "## 1. Introdução", "## 2. Métodos", "## 3. Resultados",
        "## 4. Discussão", "## 5. Limitações", "## 6. Conclusão",
        "## Referências", "## Apêndice A",
    ):
        assert heading in manuscript
    for marker in ("[[", "TODO", "TBD", "lorem ipsum"):
        assert marker not in manuscript

    validation = (out / "07_validation/VALIDATION.md").read_text(encoding="utf-8")
    assert "pending_human" in validation
    assert "dois revisores" in validation

    audit = read_json(out / "05_audit/audit-report.json")
    assert audit["status"] == "pass_with_pending_human"
    assert audit["truth_claim"] is False
    assert audit["external_validation"] is False

    manifest = read_json(out / "08_manifest/project-manifest.json")
    assert manifest["policy"]["truth_claim"] is False
    assert manifest["policy"]["external_validation"] is False
    assert manifest["policy"]["human_review_required"] is True
    assert rp.verify_manifest(out)["status"] == "pass"


def test_search_budget_is_a_hard_deadline(tmp_path):
    import signal
    if not hasattr(signal, "SIGALRM"):
        pytest.skip("SIGALRM indisponível nesta plataforma")
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    result = rp.run(
        "tema", out, searcher_factory=SlowSearcher,
        budget={"timeout_seconds": 1},
    )
    assert result["status"] == "blocked"
    error = read_json(out / "01_sources/search-error.json")
    assert error["error_type"] == "_SearchDeadlineExceeded"


def test_search_failure_blocks_without_fabrication(tmp_path):
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    result = rp.run("tema", out, searcher_factory=FailingSearcher)

    assert result["status"] == "blocked"
    assert result["stages"]["search"] == "blocked"
    error = read_json(out / "01_sources/search-error.json")
    assert error["error_type"] == "RuntimeError"
    assert "network unavailable" in error["message"]
    assert not list((out / "01_sources/systematic_review/studies").glob("*.json"))

    gate = read_json(out / "03_evidence/claim-gate.json")
    assert gate["status"] == "blocked"
    assert gate["truth_claim"] is False

    manuscript = (out / "06_manuscript/manuscript.md").read_text(encoding="utf-8")
    assert "A busca não foi executada" in manuscript or "A busca falhou" in manuscript

    audit = read_json(out / "05_audit/audit-report.json")
    assert audit["status"] == "fail"
    assert any(
        check["id"] == "search_executed" and check["status"] == "fail"
        for check in audit["checks"]
    )


def test_provisional_question_is_flagged_for_human_confirmation(tmp_path):
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    rp.run("tema amplo", out, dry_run=True, searcher_factory=BombSearcher)

    contract = read_json(out / "00_contract/retrieval-contract.json")
    assert contract["question_status"] == "provisional_from_theme"
    assert "question" in " ".join(contract["missing_constraints"]).lower() or \
        contract["clarification_required"] is True

    validation = (out / "07_validation/VALIDATION.md").read_text(encoding="utf-8")
    assert "Confirmar a pergunta" in validation
    manuscript = (out / "06_manuscript/manuscript.md").read_text(encoding="utf-8")
    assert "provisória" in manuscript.lower()


def test_corpus_mode_rejects_non_literal_quote_and_accepts_valid_corpus(tmp_path):
    from scientific_lab import research_project as rp

    bad = tmp_path / "corpus-ruim.json"
    bad.write_text(json.dumps({
        "sources": [{"id": "S1", "text": "O texto diz exatamente isto.",
                     "provenance": "arquivo local"}],
        "claims": [{
            "id": "CLAIM-C1", "text": "O texto sustenta a afirmação.",
            "confidence": 0.7,
            "evidence": [{"source_id": "S1", "quote": "trecho que não existe"}],
            "inference_level": "observation",
            "falsifier": "Se o trecho não estiver no texto.",
            "mechanism": "Citação literal do corpus fornecido pelo operador.",
            "contradictions": [], "status": "supported",
        }],
    }, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError):
        rp.run("tema", tmp_path / "ruim", dry_run=True, corpus_path=bad)

    good = tmp_path / "corpus-bom.json"
    good.write_text(json.dumps({
        "sources": [{"id": "S1", "text": "O texto diz exatamente isto.",
                     "provenance": "arquivo local verificado pelo operador"}],
        "claims": [{
            "id": "CLAIM-C1", "text": "O corpus afirma que o texto diz isto.",
            "confidence": 0.7,
            "evidence": [{"source_id": "S1", "quote": "diz exatamente isto"}],
            "inference_level": "observation",
            "falsifier": "Se o trecho não estiver no texto.",
            "mechanism": "Citação literal do corpus fornecido pelo operador.",
            "contradictions": [], "status": "supported",
        }],
    }, ensure_ascii=False), encoding="utf-8")

    out = tmp_path / "bom"
    result = rp.run("tema", out, dry_run=True, corpus_path=good,
                    searcher_factory=BombSearcher)
    assert result["status"] == "completed_pending_external_validation"
    council = read_json(out / "03_evidence/council-claims.json")
    assert council["status"] == "partial"  # uma única fonte: não é "supported"
    assert council["truth_claim"] is False
    gate = read_json(out / "03_evidence/claim-gate.json")
    assert gate["status"] == "candidate"
    manuscript = (out / "06_manuscript/manuscript.md").read_text(encoding="utf-8")
    assert "CLAIM-C1" in manuscript
    assert "arquivo local verificado pelo operador" in manuscript


def test_overclaim_and_placeholder_scanners(tmp_path):
    from scientific_lab import research_project as rp

    assert rp.scan_overclaim("Este estudo prova que X causa Y.")["status"] == "fail"
    assert rp.scan_overclaim("Este estudo não prova causalidade.")["status"] == "pass"
    assert rp.scan_overclaim("O resultado é definitivo.")["status"] == "fail"
    assert rp.scan_overclaim("O resultado não é definitivo.")["status"] == "pass"
    assert rp.scan_overclaim(
        "| ART-0001 | Prova de conceito | openalex | 10.1/a | sim |"
    )["status"] == "pass"
    assert rp.scan_overclaim(
        "[ART-0001] Autoria. **Prova de conceito**. Revista. DOI: 10.1/a."
    )["status"] == "pass"
    assert rp.scan_overclaim(
        "**CLAIM-ART-0001** — *Prova de conceito* (2024), fonte `openalex`."
    )["status"] == "pass"
    assert rp.scan_placeholders("Texto com TODO no meio.")["status"] == "fail"
    assert rp.scan_placeholders("Texto completo, sem marcadores.")["status"] == "pass"

    out = tmp_path / "projeto"
    rp.run("tema", out, dry_run=True, searcher_factory=BombSearcher)
    manuscript_path = out / "06_manuscript/manuscript.md"
    manuscript_path.write_text(
        manuscript_path.read_text(encoding="utf-8")
        + "\n\nEste estudo prova que o tema causa o desfecho.\n",
        encoding="utf-8",
    )
    audit = rp.audit_project(out)
    assert audit["status"] == "fail"
    assert audit["overclaim"]["status"] == "fail"
    assert audit["overclaim"]["matches"]


def test_manifest_detects_tampering(tmp_path):
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    rp.run("tema", out, dry_run=True, searcher_factory=BombSearcher)
    assert rp.verify_manifest(out)["status"] == "pass"

    manuscript_path = out / "06_manuscript/manuscript.md"
    manuscript_path.write_text("adulterado\n", encoding="utf-8")
    result = rp.verify_manifest(out)
    assert result["status"] == "fail"
    assert any("06_manuscript/manuscript.md" in failure for failure in result["failures"])


def test_cli_research_project_routes_to_pipeline(monkeypatch, tmp_path, capsys):
    from scientific_lab import research_project as rp
    from scientific_lab.native import cli as native_cli

    calls = []

    def fake_run(theme, out, **kwargs):
        calls.append((theme, out, kwargs))
        return {"status": "planned", "project_id": "RP-TEST"}

    monkeypatch.setattr(rp, "run", fake_run)
    code = native_cli.dispatch("research", [
        "project", "--theme", "Tema", "--out", str(tmp_path / "p"),
        "--question", "Pergunta?", "--sources", "openalex,crossref",
        "--limit", "12", "--per-platform", "3", "--dry-run",
    ])
    assert code == 0
    assert len(calls) == 1
    theme, out, kwargs = calls[0]
    assert theme == "Tema"
    assert Path(out) == tmp_path / "p"
    assert kwargs["question"] == "Pergunta?"
    assert kwargs["sources"] == ["openalex", "crossref"]
    assert kwargs["limit"] == 12
    assert kwargs["per_platform"] == 3
    assert kwargs["dry_run"] is True
    assert json.loads(capsys.readouterr().out)["project_id"] == "RP-TEST"


def test_cli_returns_blocked_code(monkeypatch, tmp_path):
    from scientific_lab import research_project as rp
    from scientific_lab.native import cli as native_cli

    monkeypatch.setattr(rp, "run", lambda *a, **k: {"status": "blocked"})
    assert native_cli.dispatch("research", [
        "project", "--theme", "Tema", "--out", str(tmp_path / "p"), "--dry-run",
    ]) == 4


def test_invalid_inputs_are_rejected(tmp_path):
    from scientific_lab import research_project as rp

    with pytest.raises(ValueError):
        rp.run("", tmp_path / "a")
    with pytest.raises(ValueError):
        rp.run("tema", tmp_path / "b", sources=["github"])
    with pytest.raises(ValueError):
        rp.run("tema", tmp_path / "c", limit=0)
    with pytest.raises(ValueError):
        rp.run("tema", tmp_path / "d", per_platform=0)


def test_manifest_and_contract_schemas_validate(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    rp.run("tema", out, dry_run=True, searcher_factory=BombSearcher)
    root = Path(__file__).resolve().parents[1] / "scientific_lab/schemas"
    for name, document in (
        ("research-project-manifest.schema.json",
         read_json(out / "08_manifest/project-manifest.json")),
        ("retrieval-contract.schema.json",
         read_json(out / "00_contract/retrieval-contract.json")),
    ):
        schema = read_json(root / name)
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(document, schema)


def test_dry_run_manifest_declares_no_publication_or_download(tmp_path):
    from scientific_lab import research_project as rp

    out = tmp_path / "projeto"
    result = rp.run("tema", out, dry_run=True, searcher_factory=BombSearcher)
    manifest = read_json(out / "08_manifest/project-manifest.json")
    assert manifest["policy"]["publication"] == "not_performed"
    assert manifest["policy"]["pdf_downloads"] == 0
    assert manifest["policy"]["credentials_used"] is False
    assert result["external_validation"] is False
    assert result["human_review_required"] is True
