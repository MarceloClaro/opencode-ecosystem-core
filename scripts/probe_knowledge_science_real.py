"""Prova pública real R663–R666; não faz parte dos testes herméticos."""
from __future__ import annotations

import asyncio
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CORE_FILES = ["research/provenance_pipeline.py", "research/statistical_methods.py",
              "marceloclaro/knowledge_evolution.py", "marceloclaro/science_cli.py",
              "marceloclaro/orchestrator.py", "mci/metabus.py", "integrations/ecosystem_mcp.py",
              "scanners/potentiality_scanner.py", "scanners/knowledge_composition.py",
              "scanners/capability_dna.py", "scanners/evolutionary_sequencing.py",
              "scripts/probe_knowledge_science_real.py"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, maximum: int = 2_000_000) -> tuple[bytes, dict]:
    with requests.get(url, timeout=(10, 15), stream=True,
                      headers={"User-Agent": "OpenCode-Core-Scientific-Provenance/1.0"}) as response:
        response.raise_for_status()
        chunks = []
        total = 0
        deadline = time.monotonic() + 45
        for chunk in response.iter_content(16384):
            total += len(chunk)
            if total > maximum or time.monotonic() > deadline:
                raise ValueError("Fonte excedeu limite de bytes/tempo")
            chunks.append(chunk)
        raw = b"".join(chunks)
        return raw, {"url": url, "final_url": response.url, "status_code": response.status_code,
                     "sha256": digest(raw), "bytes": len(raw), "retrieved_at": time.time()}


async def mcp_plan(config: dict, science_config: dict) -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    server = StdioServerParameters(command=sys.executable,
                                   args=["-m", "integrations.ecosystem_mcp"], cwd=str(ROOT))
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            inventory = await session.list_tools()
            science_result = await session.call_tool("ecosystem_scientific_run", {"config": science_config})
            if science_result.isError:
                raise RuntimeError(str(science_result.content))
            science = science_result.structuredContent
            if science is None:
                science = json.loads(next(c.text for c in science_result.content if c.type == "text"))
            if "result" in science and isinstance(science["result"], dict):
                science = science["result"]
            result = await session.call_tool("ecosystem_knowledge_plan", {"config": config})
            if result.isError:
                raise RuntimeError(str(result.content))
            payload = result.structuredContent
            if payload is None:
                payload = json.loads(next(c.text for c in result.content if c.type == "text"))
            if "result" in payload and isinstance(payload["result"], dict):
                payload = payload["result"]
            return {"tools": [tool.name for tool in inventory.tools], "science": science, "report": payload}


def main() -> None:
    executed_code_hashes = {name: digest((ROOT / name).read_bytes()) for name in CORE_FILES}
    target = ROOT / "docs/evidence" / ("R663_R666_REAL_" + time.strftime("%Y%m%d_%H%M%S"))
    sources = target / "sources"
    sources.mkdir(parents=True, exist_ok=False)
    archive_url = "https://archive.ics.uci.edu/static/public/53/iris.zip"
    raw, download = fetch(archive_url)
    (sources / "iris.zip").write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        member = "bezdekIris.data"
        data = archive.read(member)
        names = archive.read("iris.names")
    (sources / member).write_bytes(data)
    rows = [row for row in csv.reader(io.StringIO(data.decode())) if row]
    if len(rows) != 150 or any(len(row) != 5 for row in rows):
        raise ValueError("Arquivo Iris inesperado")
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["sepal_length", "sepal_width", "petal_length", "petal_width", "species"])
    writer.writerows(rows)
    csv_bytes = buffer.getvalue().encode()
    dataset = sources / "iris.csv"
    dataset.write_bytes(csv_bytes)

    reference_urls = ["https://api.crossref.org/works/10.1111/j.1469-1809.1936.tb02137.x",
                      "https://api.crossref.org/works/10.1111/1740-9713.01589"]
    reference_sources = []
    retrievals = [download]
    reference_failures = []
    for index, url in enumerate(reference_urls):
        try:
            snapshot, receipt = fetch(url)
        except requests.RequestException as exc:
            reference_failures.append({"url": url, "status": "unavailable", "error_type": type(exc).__name__})
            continue
        (sources / f"crossref-{index}.json").write_bytes(snapshot)
        message = json.loads(snapshot)["message"]
        record = {"title": message["title"][0], "doi": message["DOI"],
                  "url": "https://doi.org/" + message["DOI"],
                  "authors": [" ".join([a.get("given", ""), a.get("family", "")]).strip()
                              for a in message.get("author", [])],
                  "year": message.get("published", {}).get("date-parts", [[None]])[0][0],
                  "evidence_kind": "retrieved_http_metadata"}
        normalized = {"status": "online", "evidence_kind": "retrieved_http_metadata",
                      "records": [record], "retrieved_at": receipt["retrieved_at"],
                      "upstream_sha256": receipt["sha256"]}
        normalized_path = sources / f"reference-{index}.json"
        normalized_bytes = json.dumps(normalized, ensure_ascii=False, indent=2).encode()
        normalized_path.write_bytes(normalized_bytes)
        reference_sources.append({"path": str(normalized_path), "source_url": url,
                                  "sha256": digest(normalized_bytes)})
        retrievals.append(receipt)

    if not reference_sources:
        # Bibliografia realmente obtida no arquivo oficial; nenhuma referência
        # fictícia substitui a consulta que falhou. Escopo: metadados, sem full text.
        match = re.search(r'"([^"\n]*taxonomic[^"\n]*)"', names.decode(), re.IGNORECASE)
        if match is None:
            raise ValueError("Documento público não contém a referência esperada")
        names_path = sources / "iris.names"
        names_path.write_bytes(names)
        normalized = {"status": "online", "evidence_kind": "retrieved_http_metadata",
                      "records": [{"title": match.group(1), "authors": ["R. A. Fisher"],
                                   "year": 1936, "url": "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.names",
                                   "evidence_scope": "bibliographic_metadata_from_dataset_documentation"}],
                      "retrieved_at": download["retrieved_at"], "upstream_sha256": download["sha256"],
                      "archive_member": "iris.names", "member_sha256": digest(names)}
        normalized_path = sources / "reference-uci.json"
        normalized_bytes = json.dumps(normalized, ensure_ascii=False, indent=2).encode()
        normalized_path.write_bytes(normalized_bytes)
        reference_sources.append({"path": str(normalized_path), "source_url": archive_url,
                                  "sha256": digest(normalized_bytes)})

    config = {"question": "Qual é a associação linear entre comprimento e largura da pétala no conjunto Iris da UCI?",
              "dataset_csv": str(dataset), "dataset_provenance": {
                  "title": "Iris UCI — bezdekIris.data", "source_url": archive_url,
                  "evidence_kind": "real_observations", "sha256": digest(csv_bytes),
                  "dataset_doi": "10.24432/C56C76", "license": "CC-BY-4.0",
                  "archive_sha256": digest(raw), "member_sha256": digest(data),
                  "transformation": "Cabeçalho CSV adicionado; registros preservados.",
                  "limitations": "Conjunto histórico; espécies têm origens distintas. Correlação agregada não prova causalidade."},
              "method": "pearson", "variables": {"x": "petal_length", "y": "petal_width"},
              "reference_sources": reference_sources, "output_dir": str(target / "research")}
    config_path = target / "run-config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    run = subprocess.run([sys.executable, "-m", "marceloclaro.cli", "ciencia", "executar",
                          "--config", str(config_path)], cwd=ROOT, capture_output=True, text=True, timeout=90)
    (target / "cli-stderr.txt").write_text(run.stderr, encoding="utf-8")
    report = json.loads(run.stdout)
    if run.returncode or report.get("status") != "completed":
        raise RuntimeError(json.dumps(report, ensure_ascii=False))

    from marceloclaro.knowledge_evolution import scientific_modules
    modules = scientific_modules()
    manifest = report["artifacts"]["manifest"]
    for capability in modules["scientific_provenance_pipeline"]:
        capability["state"] = "executed"
        capability["evidence"] = [{"kind": "execution", "success": True,
                                   "ref": manifest["path"], "sha256": manifest["sha256"],
                                   "scope": "Esta análise de Iris; não demonstra todas as áreas."}]
    modules["extension_hypothesis"] = [{"id": "external_replication", "state": "declared",
                                        "requires": ["reproducible_scientific_work"],
                                        "inputs": ["research_package"], "outputs": ["external_verdict"]}]
    plan_config = {"problem": "Replicar esta análise em outro ambiente e por revisor independente.",
                   "target_state": ["external_replication"], "modules": modules}
    selected_rows = [row for row in rows if row[4] in {"Iris-versicolor", "Iris-virginica"}]
    subset = io.StringIO(newline="")
    subset_writer = csv.writer(subset, lineterminator="\n")
    subset_writer.writerow(["sepal_length", "sepal_width", "petal_length", "petal_width", "species"])
    subset_writer.writerows(selected_rows)
    subset_bytes = subset.getvalue().encode()
    subset_path = sources / "iris-two-species.csv"
    subset_path.write_bytes(subset_bytes)
    science_config = {**config, "question": "Qual é a diferença observada de largura da pétala entre versicolor e virginica no Iris UCI?",
                      "method": "welch_t", "variables": {"value": "petal_width", "group": "species",
                                                         "groups": ["Iris-versicolor", "Iris-virginica"]},
                      "dataset_csv": str(subset_path),
                      "dataset_provenance": {**config["dataset_provenance"], "sha256": digest(subset_bytes),
                                             "transformation": "Subconjunto pré-especificado versicolor/virginica: 100 de 150 registros, valores preservados.",
                                             "parent_csv_sha256": digest(csv_bytes)},
                      "output_dir": str(target / "mcp_research_welch")}
    mcp_result = asyncio.run(mcp_plan(plan_config, science_config))
    plan = mcp_result["report"]
    checks = {"cli_completed": report["status"] == "completed",
              "reproduction_passed": report["reproduction"].get("matched") is True,
              "mcp_same_orchestrator": "metacognition" in plan,
              "mcp_welch_completed": mcp_result["science"].get("status") == "completed",
              "mcp_welch_reproduced": mcp_result["science"].get("reproduction", {}).get("matched") is True,
              "evidence_scope_preserved": plan["dna"]["capability_map"]["method_execution"]["evidence"][0].get("scope") == "Esta análise de Iris; não demonstra todas as áreas.",
              "manifest_hash_preserved_in_dna": plan["dna"]["capability_map"]["method_execution"]["evidence"][0].get("sha256") == manifest["sha256"],
              "no_external_promotion": plan.get("externally_validated") is False,
              "external_replication_remains_gap": "external_replication" in plan["evolution_gap"],
              "seven_scoped_capabilities_observed": len(plan["observed_capabilities"]) == 7,
              "code_unchanged_during_probe": executed_code_hashes == {name: digest((ROOT / name).read_bytes()) for name in CORE_FILES}}
    evidence = {"scope": "Execução local em dados públicos reais; sem validação externa ou descoberta inédita.",
                "executed_code_hashes": executed_code_hashes,
                "retrievals": retrievals, "reference_failures": reference_failures,
                "transformations": [{"input_sha256": digest(data), "output_sha256": digest(csv_bytes)},
                                    {"input_sha256": digest(csv_bytes), "output_sha256": digest(subset_bytes),
                                     "selection": ["Iris-versicolor", "Iris-virginica"], "rows": len(selected_rows)}],
                "cli_returncode": run.returncode, "science": report, "mcp": mcp_result,
                "checks": checks, "success": all(checks.values())}
    path = target / "probe.json"
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps({"path": str(path), "checks": checks, "analysis": report["analysis"]}, ensure_ascii=False))
    if not evidence["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
