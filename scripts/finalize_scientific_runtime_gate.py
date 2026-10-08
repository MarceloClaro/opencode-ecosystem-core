"""Consolida o gate local R667–R671, preservando escopo e origem das provas."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from evolution.cycles import EvolutionRegistry  # noqa: E402
from integrations.opencode_cli import build_config  # noqa: E402
from integrations.scientific_plugins import ScientificPluginService  # noqa: E402

EVIDENCE = ROOT / "docs/evidence"
CORE = EVIDENCE / "R671_REAL_20261004_195302/probe.json"
SCIENCE = EVIDENCE / "R663_R666_REAL_20261004_165302/probe.json"
HOST = EVIDENCE / "R670_HOST_REAL/probe.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    code_hashes, artifact_hashes, suites, skipped, test_sources = {}, {}, [], [], set()
    for name in ("R667_R671_GREEN.xml", "R667_R671_REGRESSION.xml", "R667_R671_DOCUMENTATION.xml"):
        path = EVIDENCE / name
        cases = list(ET.parse(path).iter("testcase"))
        failed = [c for c in cases if c.find("failure") is not None or c.find("error") is not None]
        skips = [c for c in cases if c.find("skipped") is not None]
        require(not failed, "Falha em " + name)
        suites.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path),
                       "passed": len(cases) - len(skips), "skipped": len(skips), "failures": len(failed)})
        skipped.extend({"test": c.attrib["classname"] + "::" + c.attrib["name"],
                        "reason": c.find("skipped").attrib.get("message", "")} for c in skips)
        for c in cases:
            parts = c.attrib["classname"].split(".")
            while parts:
                candidate = ROOT.joinpath(*parts).with_suffix(".py")
                if candidate.is_file():
                    test_sources.add(str(candidate.relative_to(ROOT)))
                    break
                parts.pop()
    core, science, host = load(CORE), load(SCIENCE), load(HOST)
    for name, probe, key in (("core", core, "code_sha256"), ("science", science, "executed_code_hashes")):
        require(probe["success"] is True and all(probe["checks"].values()), "Probe incompleto: " + name)
        for relative, expected in probe[key].items():
            require(digest(ROOT / relative) == expected, "Código alterado após prova: " + relative)
            code_hashes[relative] = expected
    require(host["success"] is True and all(host["checks"].values()), "Conectores incompletos")
    require(digest(ROOT / "integrations/scientific_plugins.py") == host["code_sha256"], "Plugin mudou após prova")

    def artifacts(items):
        for item in items:
            path = Path(item["path"]).resolve()
            require(path.is_relative_to(ROOT) and path.is_file(), "Artefato ausente ou fora do workspace")
            require(digest(path) == item["sha256"], "Artefato alterado: " + path.name)
            artifact_hashes[str(path.relative_to(ROOT))] = item["sha256"]

    for report in (core["cli_hermes"], core["mcp"]["runtime"]):
        require(report["status"] == "completed" and report["inference_executed"] is True
                and report["external_process_executed"] is True, "Runtime externo incompleto")
        require(report["externally_validated"] is False and report["scientific_claim_eligible"] is False, "Escopo indevido")
        artifacts(report["artifacts"].values())
    for download in (core["hf"], core["kaggle"]):
        require(download["version_pinned"] is True and download["download_executed"] is True, "Download sem versão")
        artifacts(download["files"])
        path = Path(download["manifest_path"])
        require(digest(path) == download["manifest_sha256"], "Manifesto de fonte alterado")
        artifact_hashes[str(path.relative_to(ROOT))] = digest(path)
    custom = core["custom"]
    artifacts(custom["artifacts"].values())
    require(custom["rows"] == 150 and custom["synthetic"] is False and custom["mirrored_rows_merged"] == 150, "Composição divergente")
    lineage = load(Path(custom["artifacts"]["lineage"]["path"]))
    assignments = {}
    for record in lineage:
        group = record["group_hash"]
        require(group not in assignments or assignments[group] == record["split"], "Vazamento entre splits")
        assignments[group] = record["split"]
        require(len(record["sources"]) == 2, "Proveniência incompleta por linha")
    require(len({r["observation_id"] for r in lineage}) == 150, "ID duplicado na composição")
    for report in (science["science"], science["mcp"]["science"]):
        require(report["reproduction"]["matched"] is True and report["reproduction"]["process_executed"] is True, "Reprodução incompleta")
        require(report["external_validation"] is False and report["computational_review"]["human_peer_review"] is False, "Revisão superestimada")
        artifacts(report["artifacts"].values())

    service = ScientificPluginService(ROOT)
    registry = service._registry()
    require(len(registry) == 12 and all(service._snapshot(Path(e["package_root"])) == e["files"] for e in registry.values()), "Pacote importado mudou")
    for name in ("wolfram", "genomic", "ngs"):
        receipt = host["results"][name]
        request = load(service._path("requests", receipt["request_id"] + ".json"))
        persisted = service.result(receipt["request_id"])
        require(persisted["response_sha256"] == receipt["response_sha256"]
                and receipt["request_sha256"] == request["request_sha256"]
                and persisted["host_tool"] == request["host_tool"], "Recibo hospedado divergente")
    boltz = load(EVIDENCE / "R670_BOLTZ_INSTALL.json")
    require(digest(Path(boltz["binary_path"])) == boltz["binary_sha256"]
            and host["results"]["boltz_auth_status"]["exit_code"] == 0, "Boltz não instalado/autenticado")
    mutations = load(EVIDENCE / "R667_R671_MUTATIONS.json")
    require(mutations["success"] is True and len(mutations["mutants"]) == 4, "Contraprovas incompletas")
    for m in mutations["mutants"]:
        require(m["detected"] is True and digest(Path(m["log"])) == m["log_sha256"], "Contraprova alterada")
    config = load(ROOT / "opencode.json")
    require(config == build_config(), "Configuração não reproduzível")
    book_path = EVIDENCE / "R669_BOOK_PREVIEW_FINAL/report.json"
    book = load(book_path)
    require(book["compile_exit_code"] == 0 and book["catalog_agents"] == len(config["agent"])
            and book["pdf_sha256"] == digest(ROOT / "livro-core/main.pdf")
            and book["visual_review"]["status"] == "passed", "Catálogo PDF não conferido")

    specs = sorted(ROOT.glob("specs/SPEC-935-R66[789]-*.md")) + sorted(ROOT.glob("specs/SPEC-935-R67[01]-*.md"))
    require(len(specs) == 5, "Especificações ausentes")
    evolution = EvolutionRegistry()
    cycles = []
    for number, spec in zip(range(667, 672), specs):
        existing = [c for c in evolution.cycles if c.round_id == f"R{number}"]
        require(len(existing) <= 1, "Ciclo duplicado")
        cycle = existing[0] if existing else evolution.record(
            objective=spec.name.removeprefix("SPEC-935-").removesuffix(".md"),
            changes=[str(spec.relative_to(ROOT)), "docs/INTEGRACOES_CIENTIFICAS_R667_R671.md"],
            lessons=["Gate local: docs/evidence/R667_R671_RELEASE_GATE.json",
                     "Execução, instrução importada e validação externa permanecem distintas.",
                     "106 testes específicos, regressão 777/9 skips; quatro contraprovas detectadas."],
            score=None, round_id=f"R{number}")
        require(cycle.score is None and cycle.audited is False, "Ciclo promoveu validação")
        cycles.append({"round_id": cycle.round_id, "created": not bool(existing), "audited": cycle.audited, "score": cycle.score})
    doctor_run = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "doctor"], cwd=ROOT, text=True, capture_output=True, timeout=60)
    doctor = json.loads(doctor_run.stdout)
    require(doctor_run.returncode == 0 and doctor["checks_failed"] == 0, "Doctor falhou")
    doctor_path = EVIDENCE / "R667_R671_DOCTOR.json"
    doctor_path.write_text(json.dumps(doctor, ensure_ascii=False, indent=2), encoding="utf-8")

    tracked = set(code_hashes) | test_sources | {str(p.relative_to(ROOT)) for p in specs} | {
        "integrations/opencode_cli.py", "marceloclaro/cli.py", "opencode.json", ".opencode/scientific-plugins/registry.json",
        "docs/AGENTES_R669.md", "docs/INTEGRACOES_CIENTIFICAS_R667_R671.md", "README.md", "MANUAL.md", "ARCHITECTURE.md",
        "installer/README.md", "installer/windows/README.md", "livro-core/gen_mod10.py", "livro-core/mod-10-catalogo.tex",
        "livro-core/main.pdf",
        "scripts/probe_scientific_runtime_mutations.py", "scripts/probe_scientific_plugins_host.py", "scripts/install_boltz_pinned.py",
        "scripts/probe_mirofish_hermes_real.py", "scripts/finalize_scientific_runtime_gate.py"}
    tracked.update(str(p.relative_to(ROOT)) for p in ROOT.glob("agents/catalog/*.md") if p.stem in {
        "scientific-capabilities-audit", "simulation-game-audit", "book-mcp", "book-finetuning", "library-architecture",
        "hooks-integration", "mcp-cli-integration", "live-mirofish-hermes"})
    paths = [CORE, SCIENCE, HOST, doctor_path, book_path, EVIDENCE / "R667_R671_MUTATIONS.json"]
    tracked.update(str(p.relative_to(ROOT)) for p in paths)
    tracked.update(s["path"] for s in suites)
    hashes = {p: digest(ROOT / p) for p in sorted(tracked)}
    result = {"status": "PASS", "scope": "Local software gate plus actual downloads, external processes and host-reported connector calls",
              "generated_at": datetime.now(timezone.utc).isoformat(), "suites": suites, "skipped_tests": skipped,
              "mutations_detected": 4, "cycles": cycles, "probes": [str(p.relative_to(ROOT)) for p in (CORE, SCIENCE, HOST)],
              "book_catalog": book,
              "configuration": {"agents": len(config["agent"]), "mcp_servers": len(config["mcp"]), "commands": len(config["command"])},
              "doctor": {k: doctor[k] for k in ("checks_total", "checks_passed", "checks_warned", "checks_failed")},
              "artifact_hashes": artifact_hashes, "code_and_evidence_hashes": hashes,
              "external_validation": False, "human_peer_review": False,
              "limitations": ["Nine legacy MiroFish HTTP tests skipped: HTTP service not started; official OASIS script executed separately.",
                              "Hosted responses rely on the authenticated host; receipt binding is not independent cryptographic authentication.",
                              "Genomic catalog and NGS infrastructure inspection are not scientific predictions or workflows.",
                              "No Boltz molecular job, training, grant creation, publication or deployment was performed.",
                              "Tests in different suites overlap; counts must not be added as unique test totals."]}
    path = EVIDENCE / "R667_R671_RELEASE_GATE.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"status": result["status"], "path": str(path), "suites": suites, "cycles": cycles, "doctor": result["doctor"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
