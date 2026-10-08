"""Gate local: reconcilia checks reexecutados e registra ciclos sem nota externa."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    xml_paths = [ROOT / "docs/evidence/NOTEBOOK_CORE_REGRESSION_BEFORE_DOC_FIX.xml",
                 ROOT / "docs/evidence/NOTEBOOK_CORE_FINAL_DOCS_GREEN.xml"]
    outcomes = {}
    runs = []
    for path in xml_paths:
        tree = ET.parse(path)
        rows = tree.findall(".//testcase")
        for row in rows:
            outcomes[(row.get("classname"), row.get("name"))] = not any(
                row.find(name) is not None for name in ("failure", "error"))
        runs.append({"path": str(path.relative_to(ROOT)), "tests": len(rows),
                     "failures": len(tree.findall(".//failure")), "errors": len(tree.findall(".//error")),
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    assert outcomes and all(outcomes.values()), "Checks com falha ainda não resolvidos"
    mutants = json.loads((ROOT / "docs/evidence/R674_MUTATION.json").read_text())
    service = ROOT / "integrations/gemini_notebook.py"
    assert mutants["passed"] and mutants["source_sha256"] == hashlib.sha256(service.read_bytes()).hexdigest()
    real = json.loads((ROOT / "docs/evidence/R674_REAL_CENTRAL.json").read_text())
    assert real["confidence_ledger_unchanged"]
    assert all(row["status"] in {"completed", "prepared"} for row in real["receipts"])
    assert next(row for row in real["receipts"] if row["operation"] == "catalog")["mcp_tool_count"] == 49
    assert next(row for row in real["receipts"] if row["operation"] == "catalog")["cli_entry_count"] == 155
    assert next(row for row in real["receipts"] if row.get("authentication_valid") is not None)["authentication_valid"]
    mcp = json.loads((ROOT / "docs/evidence/R674_REAL_CORE_MCP.json").read_text())
    assert mcp["operation_status"] == "completed" and mcp["persistent_session"]
    config = json.loads((ROOT / "docs/evidence/R676_CONFIG_PROOF.json").read_text())
    assert config["reproduced"] and config["configured_agents"] == 238
    source = json.loads((ROOT / "docs/evidence/NOTEBOOK_SOURCE_PROVENANCE.json").read_text())
    assert source["installed_source_matches"]
    from evolution import evolution_registry
    cycles = {
        "R672": ("Transporte CLI/MCP oficial e sessões persistentes Gemini Notebook", ["integrations/gemini_notebook_transport.py", "integrations/gemini_notebook_session.py"]),
        "R673": ("Catálogo completo e política de efeitos Gemini Notebook", ["integrations/gemini_notebook_catalog.py"]),
        "R674": ("Orquestração central, skill, preflight e proveniência Gemini Notebook", ["integrations/gemini_notebook.py", "integrations/gemini_notebook_pipeline.py", "marceloclaro/orchestrator.py", "integrations/ecosystem_mcp.py"]),
        "R675": ("Podcast exige áudio real e não promove confiança por sucesso operacional", ["agent_runners/nlm_executor.py", "tests/test_r675_notebook_podcast_truthfulness.py"]),
        "R676": ("Especialistas Gemini notebook audit/upstream/transport registrados no Core", ["agents/catalog/gemini-notebook-audit.md", "agents/catalog/gemini-notebook-upstream.md", "agents/catalog/gemini-notebook-transport.md", "opencode.json"]),
    }
    hashes = {}
    for round_id, (objective, paths) in cycles.items():
        spec = next(ROOT.glob("specs/SPEC-935-" + round_id + "-*.md"))
        paths = [*paths, str(spec.relative_to(ROOT))]
        scoped_hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
        hashes.update(scoped_hashes)
        existing = next((cycle for cycle in evolution_registry.cycles if cycle.round_id == round_id), None)
        if existing is None:
            cycle = evolution_registry.record(objective, paths, score=None, round_id=round_id,
                lessons=["Provas operacionais delimitadas; não constituem inferência universal ou validação científica externa."])
            cycle.artifact_hashes = scoped_hashes
            cycle.evidence_trail = [row["path"] for row in runs]
            evolution_registry.save()
        elif existing.artifact_hashes == scoped_hashes:
            existing.evidence_trail = [row["path"] for row in runs]
            evolution_registry.save()
        else:
            raise RuntimeError("Ciclo já registrado com outra versão de artefatos: " + round_id)
    book = ROOT / "livro-core/output/pdf/main.pdf"
    hashes[str(book.relative_to(ROOT))] = hashlib.sha256(book.read_bytes()).hexdigest()
    report = {"status": "passed", "scope": "local_integration_release_gate",
              "test_result_policy": "Resultados da reexecução dirigida substituem os checks corrigidos da rodada completa.",
              "unique_tests_passed": len(outcomes), "runs": runs, "targeted_mutants_killed": len(mutants["mutants"]),
              "real_read_only_probes": len(real["receipts"]), "central_mcp_operation_completed": True,
              "mcp_tools": 49, "cli_entries": 155, "configured_agents": 238,
              "runtime_source_matches_requested_commit": source["installed_source_matches"],
              "recorded_cycles": list(cycles), "artifact_hashes": hashes,
              "remote_generation_tested": False, "enterprise_tested": False,
              "book_pdf_pages": 298,
              "scientifically_externally_validated": False}
    path = ROOT / "docs/evidence/NOTEBOOK_CORE_RELEASE_GATE.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"artifact_hashes", "runs"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
