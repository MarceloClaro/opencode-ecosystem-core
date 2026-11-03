"""R1023: contratos locais e contraprovas; sem inferência LLM ou rede."""

from __future__ import annotations

import copy
import importlib
import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("livro-para-skill", "legislacao-brasileira-auditavel")
REPOS = {
    "remotion-dev/codex-plugin", "remotion-dev/chromium",
    "deepseek-ai/dsh-superagent-prototype", "cclank/lanshu-openai-media-api",
    "Crosstalk-Solutions/project-nomad", "asoutelino-svg/awesome-reverse-engineered",
    "asoutelino-svg/book-finder", "asoutelino-svg/book-to-skill",
    "asoutelino-svg/llm-legislativo", "asoutelino-svg/ciencia-de-dados-cibele-russo",
    "asoutelino-svg/leis_brasileiras",
}


def read(relative):
    path = ROOT / relative
    assert path.is_file(), f"Artefato ainda ausente: {relative}"
    return path.read_text(encoding="utf-8")


def manifest():
    return json.loads(read("federation/repository-curation-r1023.json"))


def module():
    assert (ROOT / "integrations/source_skill_contracts.py").is_file(), "Verificador ausente"
    return importlib.import_module("integrations.source_skill_contracts")


def text(slug):
    return read(f".opencode/skills/{slug}/SKILL.md")


def example(slug):
    return json.loads(read(f".opencode/skills/{slug}/references/exemplo.json"))


def test_repository_coverage_and_decisions():
    data = manifest()
    assert data["schema_version"] == "r1023.v1"
    rows = data["repositories"]
    assert {r["repo"] for r in rows} == REPOS
    assert len(rows) == len(REPOS)
    for row in rows:
        assert row["decision"] in {"original_adaptation", "reference_only", "deferred", "already_adapted"}
        assert row["installed"] is False and row["executed"] is False
        assert row["reason"] and row["limitations"] and row["core_paths"]
        for path in row["core_paths"]:
            assert (ROOT / path).is_file(), path


def test_pinned_evidence_and_license_limits():
    for row in manifest()["repositories"]:
        assert row["inspection_status"] in {"inspected", "unavailable"}
        assert row["license_scope"] and row["license_basis"]
        if row["inspection_status"] == "unavailable":
            assert row["error"] and row["decision"] == "deferred"
            continue
        assert re.fullmatch(r"[0-9a-f]{40}", row["commit"])
        assert row["documents"]
        for doc in row["documents"]:
            assert doc["url"].startswith(f"https://raw.githubusercontent.com/{row['repo']}/{row['commit']}/")
            assert re.fullmatch(r"[0-9a-f]{64}", doc["sha256"])
            assert doc["bytes"] > 0 and doc["http_status"] == 200
            assert doc["retrieved_at"]
        assert any("license" in d["path"].lower() for d in row["documents"])
    rows = {r["repo"]: r for r in manifest()["repositories"]}
    assert rows["asoutelino-svg/ciencia-de-dados-cibele-russo"]["decision"] == "reference_only"
    assert "NC" in rows["asoutelino-svg/ciencia-de-dados-cibele-russo"]["license_declared"]
    assert rows["remotion-dev/chromium"]["decision"] == "deferred"


def test_native_skill_discovery():
    from reversa_universal.skill_dispatch import ReversaSkillDispatcher
    dispatcher = ReversaSkillDispatcher(ROOT)
    for slug in SKILLS:
        body = text(slug)
        front = yaml.safe_load(body.split("---", 2)[1])
        assert front["name"] == slug and len(front["description"]) >= 30
        assert not front.get("disable-model-invocation", False)
        assert not (ROOT / ".claude/skills" / slug).exists()
        # Dispatcher real do Core; não equivale a execução da skill por LLM.
        assert dispatcher.resolve_skill(slug) == ROOT / ".opencode/skills" / slug / "SKILL.md"


def test_local_reference_links():
    for slug in SKILLS:
        base = ROOT / ".opencode/skills" / slug
        assert base.is_dir()
        for file in base.rglob("*.md"):
            for link in re.findall(r"\]\(([^\s)]+)\)", file.read_text()):
                if link.startswith(("https://", "http://", "#")):
                    continue
                target = (file.parent / link.split("#")[0]).resolve()
                assert target.is_relative_to(ROOT) and target.is_file(), (file, link)


def test_book_skill_contract():
    body = text(SKILLS[0])
    for section in ("## Entrada e direitos", "## Evidência e extração", "## Construção e validação", "## Limites"):
        assert section in body
    record = example(SKILLS[0])
    before = copy.deepcopy(record)
    result = module().assess_book(record)
    assert result["status"] == "candidate_for_review"
    assert result["content_verified"] is False and result["rights_verified"] is False
    assert result["actions_executed"] == [] and result["reasons"] == []
    assert record == before
    assert module().assess_book(record) == result


@pytest.mark.parametrize("field,value,reason", [
    ("rights_basis", "unknown", "rights_unresolved"),
    ("rights_evidence", "", "rights_evidence_missing"),
    ("text_available", False, "text_unavailable"),
    ("coverage", "unavailable", "coverage_invalid"),
    ("edition", "", "edition_missing"),
    ("source_sha256", "abc", "hash_invalid"),
    ("locators", [], "locators_missing"),
    ("locators", [1], "locators_missing"),
    ("locators", [""], "locators_missing"),
    ("source_role", "ai_summary", "primary_source_required"),
    ("execute_source_instructions", True, "source_instructions_forbidden"),
    ("execute_source_instructions", "false", "source_instructions_forbidden"),
    ("text_available", "true", "text_unavailable"),
])
def test_book_negative_cases(field, value, reason):
    record = example(SKILLS[0]); record[field] = value
    result = module().assess_book(record)
    assert result["status"] == "blocked" and reason in result["reasons"]
    assert result["actions_executed"] == []


def test_legislation_skill_contract():
    body = text(SKILLS[1])
    for section in ("## Recorte temporal", "## Fontes e versões", "## Consulta e registro", "## Limites"):
        assert section in body
    result = module().assess_legislation(example(SKILLS[1]))
    assert result["status"] == "candidate_for_review"
    assert result["validity_verified"] is False and result["content_verified"] is False
    assert result["actions_executed"] == [] and result["reasons"] == []


@pytest.mark.parametrize("field,value,reason", [
    ("jurisdiction", "", "jurisdiction_missing"),
    ("as_of", "2026-02-30", "reference_date_invalid"),
    ("retrieved_at", "2026-01-40", "retrieval_date_invalid"),
    ("source_url", "https://www.planalto.gov.br.attacker.example/lei", "official_source_required"),
    ("source_url", "https://user:secret@www.planalto.gov.br/lei", "official_source_required"),
    ("source_url", "https://www.planalto.gov.br:8443/lei", "official_source_required"),
    ("source_url", "https://www.planalto.gov.br\n/lei", "official_source_required"),
    ("source_url", "https://[not-an-ip/lei", "official_source_required"),
    ("source_url", "http://www.planalto.gov.br/lei", "official_source_required"),
    ("source_url", "https://github.com/user/leis/blob/main/lei.md", "official_source_required"),
    ("source_sha256", None, "hash_invalid"),
    ("locators", [], "locators_missing"),
    ("record_type", "proposal", "proposal_not_enacted"),
    ("record_type", "inventado", "record_type_invalid"),
    ("claim_current_validity", True, "validity_requires_legal_review"),
    ("claim_current_validity", "false", "validity_requires_legal_review"),
    ("text_version", "", "text_version_missing"),
    ("text_available", False, "text_unavailable"),
])
def test_legislation_negative_cases(field, value, reason):
    record = example(SKILLS[1]); record[field] = value
    result = module().assess_legislation(record)
    assert result["status"] == "blocked" and reason in result["reasons"]
    assert result["validity_verified"] is False


def test_existing_routes_reused():
    book = text(SKILLS[0]); law = text(SKILLS[1])
    assert "ecosystem_library_search" in book and "research/pdf_pipeline.py" in book
    assert "educacao-legislacao" in law and "list_sources" in law
    for path, marker in (
        (".opencode/skills/federacao-universal/SKILL.md", "references/curadoria-r1023.md"),
        (".opencode/skills/reverse-engineer-anything/SKILL.md", "references/search-before-reconstruction.md"),
        (".claude/skills/cp-direcao-de-edicao/SKILL.md", "references/curadoria-r1023.md"),
    ):
        assert marker in read(path)
        assert (ROOT / path).parent.joinpath(marker).is_file()


def test_no_executable_imports_or_model_override(monkeypatch, capsys):
    for slug in SKILLS:
        for path in (ROOT / ".opencode/skills" / slug).rglob("*"):
            if path.is_file():
                assert path.suffix in {".md", ".json"}
    import io
    engine = module()
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(example(SKILLS[0]))))
    assert engine.main(["book"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "candidate_for_review"
    for raw in ("[]", "{", '{"x":NaN}', '{"x":1,"x":2}', " " * (1024 * 1024 + 1)):
        monkeypatch.setattr("sys.stdin", io.StringIO(raw))
        assert engine.main(["book"]) == 2
        result = json.loads(capsys.readouterr().out)
        assert result["status"] == "blocked" and result["actions_executed"] == []
    source = read("integrations/source_skill_contracts.py")
    import ast
    tree = ast.parse(source)
    imports = {n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import)}
    imports |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert imports <= {"__future__", "argparse", "datetime", "json", "re", "sys", "urllib", "collections"}
    assert not {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)} & {"exec", "eval", "__import__", "open"}
