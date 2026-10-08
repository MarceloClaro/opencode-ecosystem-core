"""Consolida evidências locais R663–R666 sem atribuir validação externa."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evolution.cycles import EvolutionRegistry  # noqa: E402
from integrations.opencode_cli import build_config  # noqa: E402

EVIDENCE = ROOT / "docs/evidence"
REAL = EVIDENCE / "R663_R666_REAL_20261004_114400"
SPECS = [
    "specs/SPEC-935-R663-scientific-provenance-pipeline.md",
    "specs/SPEC-935-R664-potentiality-composition.md",
    "specs/SPEC-935-R665-evolutionary-sequencing.md",
    "specs/SPEC-935-R666-knowledge-evolution-orchestration.md",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False),
                    encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> None:
    suites = []
    test_sources = set()
    skipped = []
    for name in ("R663_R666_REGRESSION.xml", "R663_R666_EXTENDED_FINAL.xml"):
        path = EVIDENCE / name
        root = ET.parse(path).getroot()
        cases = list(root.iter("testcase"))
        failures = sum(bool(t.find("failure") is not None or t.find("error") is not None)
                       for t in cases)
        skip_cases = [t for t in cases if t.find("skipped") is not None]
        require(failures == 0, f"Regressão falhou: {name}")
        suites.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path),
                       "passed": len(cases) - len(skip_cases), "skipped": len(skip_cases),
                       "failures": failures})
        for case in cases:
            test_sources.add(case.attrib["classname"].replace(".", "/") + ".py")
        skipped.extend({"test": t.attrib["classname"] + "::" + t.attrib["name"],
                        "reason": t.find("skipped").attrib.get("message", "")}
                       for t in skip_cases)
    probe = load(REAL / "probe.json")
    require(probe["success"] is True and all(v is True for v in probe["checks"].values()),
            "Probe CLI/MCP incompleto")
    for relative, expected in probe["executed_code_hashes"].items():
        require(digest(ROOT / relative) == expected, f"Código mudou após execução: {relative}")

    artifact_hashes = {}
    for report in (probe["science"], probe["mcp"]["science"]):
        require(report["status"] == "completed" and report["experiment_executed"] is True,
                "Experimento incompleto")
        require(report["reproduction"]["matched"] is True and
                report["reproduction"]["process_executed"] is True,
                "Reprodução incompleta")
        require(report["computational_review"]["human_peer_review"] is False and
                report["external_validation"] is False, "Escopo indevido")
        for artifact in report["artifacts"].values():
            path = Path(artifact["path"]).resolve()
            require(path.is_relative_to(REAL), "Artefato fora do diretório da prova")
            actual = digest(path)
            require(actual == artifact["sha256"], f"Hash de artefato divergente: {path.name}")
            artifact_hashes[str(path.relative_to(ROOT))] = actual

    sources = REAL / "sources"
    require(len(probe["retrievals"]) == 3, "Recibos HTTP incompletos")
    for receipt, name in zip(probe["retrievals"],
                             ("iris.zip", "crossref-0.json", "crossref-1.json")):
        require(receipt["status_code"] == 200 and digest(sources / name) == receipt["sha256"],
                f"Recibo HTTP divergente: {name}")
    with zipfile.ZipFile(sources / "iris.zip") as archive:
        member = archive.read("bezdekIris.data")
    require(member == (sources / "bezdekIris.data").read_bytes(), "Extração UCI divergente")
    for number in (0, 1):
        reference = load(sources / f"reference-{number}.json")
        raw = load(sources / f"crossref-{number}.json")["message"]
        require(reference["upstream_sha256"] == digest(sources / f"crossref-{number}.json")
                and reference["records"][0]["doi"] == raw["DOI"]
                and reference["records"][0]["title"] == raw["title"][0],
                "Snapshot bibliográfico divergente do recibo")
    first, second = probe["transformations"]
    require(first["input_sha256"] == digest(sources / "bezdekIris.data") and
            first["output_sha256"] == digest(sources / "iris.csv") and
            second["input_sha256"] == first["output_sha256"] and
            second["output_sha256"] == digest(sources / "iris-two-species.csv"),
            "Cadeia de transformação divergente")
    with (sources / "iris.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with (sources / "iris-two-species.csv").open(encoding="utf-8", newline="") as stream:
        subset = list(csv.DictReader(stream))
    require(len(rows) == 150 and len(subset) == 100 and
            subset == [row for row in rows if row["species"] in second["selection"]],
            "Subconjunto prespecificado divergente")

    mutations = load(EVIDENCE / "R663_R666_MUTATIONS.json")
    require(mutations["success"] is True and len(mutations["mutants"]) == 4 and
            all(m["detected"] is True for m in mutations["mutants"]), "Mutações não detectadas")
    for mutant in mutations["mutants"]:
        require(digest(Path(mutant["log"])) == mutant["log_sha256"], "Log de mutação alterado")
    require(load(ROOT / "opencode.json") == build_config(), "Configuração não reproduzível")

    registry = EvolutionRegistry()
    objectives = (
        "Pesquisa reproduzível com fontes reais, proveniência e bloqueio de simulações",
        "DNA de capacidades, potenciais emergentes e composição rastreável",
        "Sequenciamento evolutivo por dependências e correção de Nash/Pareto",
        "Orquestração central CLI/MCP e observações metacognitivas persistentes",
    )
    cycle_receipts = []
    for number, spec, objective in zip(range(663, 667), SPECS, objectives):
        existing = [c for c in registry.cycles if c.round_id == f"R{number}"]
        require(len(existing) <= 1, f"Ciclo duplicado: R{number}")
        cycle = existing[0] if existing else registry.record(
            objective=objective, changes=[spec, "docs/CONHECIMENTO_CIENTIFICO_R663_R666.md"],
            score=None, round_id=f"R{number}",
            lessons=["Gate: docs/evidence/R663_R666_RELEASE_GATE.json",
                     "723 testes locais aprovados; um PDF ignorado; quatro mutações detectadas.",
                     "Reprodução computacional não equivale a replicação independente.",
                     "Sem avaliação externa, revisão humana ou pontuação científica atribuída."])
        require(cycle.audited is False and cycle.score is None, "Ciclo atribui avaliação indevida")
        cycle_receipts.append({"round_id": cycle.round_id, "created": not bool(existing),
                               "audited": cycle.audited, "score": cycle.score})

    doctor_run = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "doctor"],
                                cwd=ROOT, capture_output=True, text=True, timeout=60)
    require(doctor_run.returncode == 0, "Doctor não executou")
    doctor = json.loads(doctor_run.stdout)
    require(doctor["checks_failed"] == 0, "Doctor reportou falha")
    doctor_path = EVIDENCE / "R663_R666_DOCTOR.json"
    write(doctor_path, doctor)

    files = set(probe["executed_code_hashes"]) | set(SPECS) | test_sources | {
        "research/hub.py", "skills/tooling/data_knowledge_hub/datasets.py",
        "agentic_science_v2/deep_research.py", "mci/pipeline/scientific_governance_pipeline.py",
        "gametheory/phd_auditor.py", "scanners/trajectory_mapper.py", "marceloclaro/cli.py",
        "marceloclaro/doctor.py", "integrations/opencode_cli.py", "opencode.json",
        "scripts/probe_knowledge_mutations.py", "scripts/finalize_knowledge_gate.py",
        "docs/CONHECIMENTO_CIENTIFICO_R663_R666.md",
    }
    # Classnames de suites antigas incluem a classe; o módulo é o arquivo existente.
    resolved_files = set()
    for relative in files:
        path = ROOT / relative
        while not path.is_file() and path.suffix == ".py" and path.parent != ROOT:
            path = path.parent.with_suffix(".py")
        require(path.is_file(), f"Fonte não encontrada: {relative}")
        resolved_files.add(str(path.relative_to(ROOT)))
    gate = {
        "status": "PASS_LOCAL_SCOPE", "generated_at": datetime.now(timezone.utc).isoformat(),
        "specs": SPECS, "tests": {"passed": sum(s["passed"] for s in suites),
            "skipped": skipped, "failures": 0, "suites": suites},
        "real_probe": {"path": str((REAL / "probe.json").relative_to(ROOT)),
            "sha256": digest(REAL / "probe.json"), "checks": probe["checks"],
            "executed_code_hashes": probe["executed_code_hashes"],
            "artifact_hashes": artifact_hashes},
        "mutations": {"path": "docs/evidence/R663_R666_MUTATIONS.json",
            "sha256": digest(EVIDENCE / "R663_R666_MUTATIONS.json"), "detected": 4},
        "doctor": {"path": str(doctor_path.relative_to(ROOT)), "sha256": digest(doctor_path),
            "passed": doctor["checks_passed"], "warned": doctor["checks_warned"],
            "failed": doctor["checks_failed"]},
        "evolution_cycles": cycle_receipts,
        "final_snapshot_hashes": {p: digest(ROOT / p) for p in sorted(resolved_files)},
        "external_validation": False, "human_peer_review": False,
        "independent_replication": False, "model_inference_executed": False,
        "limitations": ["Aprovação de contratos locais; não certifica ciência universal.",
            "Potenciais e roadmaps são hipóteses/estimativas condicionais.",
            "RAG de metadados; não comprova leitura integral dos artigos.",
            "MiroFish/OASIS externo e transporte Hermes não executados nesta prova.",
            "Artigos e código foram gerados; livro completo não foi gerado."]}
    write(EVIDENCE / "R663_R666_RELEASE_GATE.json", gate)
    print(json.dumps({"status": gate["status"], "tests_passed": gate["tests"]["passed"],
                      "skipped": len(skipped), "artifacts": len(artifact_hashes),
                      "mutants_detected": 4, "doctor": gate["doctor"],
                      "cycles": cycle_receipts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
