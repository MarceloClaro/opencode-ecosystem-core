"""R1150 — auditoria de duplicidade do catálogo de agentes e MCPs.

Compara:

- `agents/catalog/*.md` (fonte) com `opencode.json` (configuração compilada);
- ids e nomes repetidos no catálogo;
- prompts repetidos em agentes diferentes;
- comandos/URLs de MCP repetidos;
- descrições quase idênticas (Jaccard de tokens);
- spec/test ausentes referenciados pelo catálogo.

Não remove, funde ou reescreve agentes. A saída é um relatório para revisão
humana; duplicidade textual não prova duplicidade funcional.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "agents" / "catalog"
DEFAULT_CONFIG = ROOT / "opencode.json"
DEFAULT_BASELINE = ROOT / "agents" / "lifecycle_baseline.json"
DEFAULT_OUTPUT = ROOT / "reports" / "r1150" / "catalog_audit.json"

LIMITS = (
    "Auditoria textual e estrutural. Não avalia qualidade, trust, execução ou "
    "equivalência funcional. Duplicidade de descrição não autoriza remoção; "
    "toda fusão exige revisão humana e teste de contrato."
)
_WORD = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ]+")
REVIEWED_NEAR_DUPLICATES = {
    ("gjq-backend-guoji-04", "gjq-backend-guoji-07"): (
        "Backends distintos de 100 qubits; similaridade textual não implica "
        "equivalência funcional. Não fundir sem calibração e revisão."
    ),
}


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except ValueError:
            return value.strip('"')
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    payload = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key and key not in payload:
            payload[key] = _scalar(value)
    return payload


def _norm(text: str) -> str:
    return " ".join(_WORD.findall(str(text).lower()))


def _tokens(text: str) -> set[str]:
    return set(_norm(text).split())


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _canonical_mcp(mcp: dict) -> tuple[str, str] | None:
    if not isinstance(mcp, dict):
        return None
    if mcp.get("type") == "remote" or mcp.get("url"):
        url = str(mcp.get("url", "")).strip()
        return ("remote", url) if url else None
    command = mcp.get("command")
    if isinstance(command, list):
        return ("local", json.dumps([str(item) for item in command]))
    if isinstance(command, str):
        return ("local", command)
    return None


def audit_catalog(
    *,
    catalog_dir: str | Path = DEFAULT_CATALOG,
    config_path: str | Path = DEFAULT_CONFIG,
    baseline_path: str | Path = ROOT / "agents" / "lifecycle_baseline.json",
    near_duplicate_threshold: float = 0.9,
    max_near_duplicates: int = 50,
    max_missing_examples: int = 50,
    reviewed_near_duplicates: dict | None = None,
) -> dict:
    catalog_dir = Path(catalog_dir)
    config_path = Path(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    baseline_files = {}
    baseline_path = Path(baseline_path)
    if baseline_path.exists():
        baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))
        baseline_files = baseline_payload.get("files", {})
        if not isinstance(baseline_files, dict):
            raise ValueError("lifecycle_baseline files deve ser objeto")
    reviewed = reviewed_near_duplicates
    if reviewed is None:
        reviewed = REVIEWED_NEAR_DUPLICATES
    reviewed_pairs = {
        tuple(sorted((str(left), str(right)))): str(reason)
        for (left, right), reason in reviewed.items()
    }
    agents = config.get("agent", {})
    mcps = config.get("mcp", {})
    if not isinstance(agents, dict) or not isinstance(mcps, dict):
        raise ValueError("opencode.json exige agent e mcp como objetos")

    records = []
    for path in sorted(catalog_dir.glob("*.md")):
        raw = path.read_bytes()
        front = parse_frontmatter(path)
        declared = str(front.get("agent_id") or path.stem).strip()
        records.append({
            "file": path.name,
            "agent_id": path.stem,
            "declared_agent_id": declared,
            "name": str(front.get("name", "")).strip(),
            "description": str(front.get("description", "")).strip(),
            "spec_file": str(front.get("spec_file", "")).strip(),
            "test_file": str(front.get("test_file", "")).strip(),
            "source": str(front.get("source", "")).strip(),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })

    by_id: dict[str, list[str]] = {}
    by_declared: dict[str, list[str]] = {}
    by_name: dict[str, list[str]] = {}
    metadata_id_mismatches = []
    legacy_baseline_mismatches = []
    for record in records:
        by_id.setdefault(record["agent_id"], []).append(record["file"])
        by_declared.setdefault(record["declared_agent_id"], []).append(record["file"])
        if record["declared_agent_id"] != record["agent_id"]:
            relative = f"agents/catalog/{record['file']}"
            baseline_hash = baseline_files.get(relative)
            item = {
                "file": record["file"],
                "declared_agent_id": record["declared_agent_id"],
                "canonical_agent_id": record["agent_id"],
                "sha256": record["sha256"],
            }
            if baseline_hash == record["sha256"]:
                item["reason"] = (
                    "bytes históricos preservados pelo lifecycle_baseline; "
                    "migração exige contrato managed-v1 e atualização de baseline"
                )
                legacy_baseline_mismatches.append(item)
            else:
                item["reason"] = "agent_id declarado diverge do nome do arquivo"
                metadata_id_mismatches.append(item)
        if record["name"]:
            by_name.setdefault(_norm(record["name"]), []).append(record["file"])
    catalog_ids = set(by_id)
    config_ids = set(agents)

    prompt_groups: dict[str, list[str]] = {}
    for name, payload in agents.items():
        if isinstance(payload, dict):
            prompt = str(payload.get("prompt", ""))
            if prompt:
                prompt_groups.setdefault(prompt, []).append(name)
    mcp_groups: dict[tuple[str, str], list[str]] = {}
    for name, payload in mcps.items():
        signature = _canonical_mcp(payload)
        if signature:
            mcp_groups.setdefault(signature, []).append(name)

    token_cache = {
        record["agent_id"]: _tokens(record["description"])
        for record in records
        if len(_tokens(record["description"])) >= 8
    }
    near_duplicates = []
    reviewed_near = []
    ids = sorted(token_cache)
    for index, left in enumerate(ids):
        for right in ids[index + 1:]:
            if left == right:
                continue
            score = _jaccard(token_cache[left], token_cache[right])
            if score >= float(near_duplicate_threshold):
                item = {
                    "left": left,
                    "right": right,
                    "jaccard": round(score, 6),
                }
                key = tuple(sorted((left, right)))
                if key in reviewed_pairs:
                    item["rationale"] = reviewed_pairs[key]
                    reviewed_near.append(item)
                else:
                    near_duplicates.append(item)
    near_duplicates.sort(key=lambda item: item["jaccard"], reverse=True)
    reviewed_near.sort(key=lambda item: item["jaccard"], reverse=True)
    near_duplicates = near_duplicates[: int(max_near_duplicates)]
    reviewed_near = reviewed_near[: int(max_near_duplicates)]

    missing = []
    for record in records:
        for field in ("spec_file", "test_file"):
            value = record[field]
            if value and not (ROOT / value).exists():
                missing.append({
                    "agent_id": record["agent_id"],
                    "field": field,
                    "path": value,
                })

    duplicate_ids = [
        {"agent_id": key, "files": files}
        for key, files in sorted(by_id.items()) if len(files) > 1
    ]
    duplicate_declared_ids = [
        {"declared_agent_id": key, "files": files}
        for key, files in sorted(by_declared.items()) if len(files) > 1
    ]
    duplicate_names = [
        {"name": key, "files": files}
        for key, files in sorted(by_name.items()) if len(files) > 1
    ]
    duplicate_prompts = [
        {"prompt": key, "agents": names}
        for key, names in sorted(prompt_groups.items()) if len(names) > 1
    ]
    duplicate_mcp = [
        {"signature": list(key), "names": names}
        for key, names in sorted(mcp_groups.items()) if len(names) > 1
    ]
    catalog_not_in_config = sorted(catalog_ids - config_ids)
    config_not_in_catalog = sorted(config_ids - catalog_ids)

    recommendations = []
    if duplicate_ids:
        recommendations.append("Unificar ou renomear ids repetidos no catálogo.")
    if duplicate_declared_ids:
        recommendations.append(
            "Revisar agent_id declarado repetido; o nome do arquivo é o id canônico."
        )
    if metadata_id_mismatches:
        recommendations.append(
            "Migrar agent_id divergente do nome do arquivo; há divergência "
            "não coberta pelo baseline."
        )
    if legacy_baseline_mismatches:
        recommendations.append(
            "Manter os agent_id legados preservados pelo baseline ou migrar "
            "para managed-v1 com atualização explícita de hash."
        )
    if duplicate_names:
        recommendations.append("Revisar nomes de exibição repetidos.")
    if duplicate_prompts:
        recommendations.append("Investigar agentes distintos com o mesmo prompt.")
    if duplicate_mcp:
        recommendations.append("Consolidar ou justificar MCPs com a mesma assinatura.")
    if near_duplicates:
        recommendations.append("Revisar descrições quase idênticas antes de fundir.")
    if reviewed_near:
        recommendations.append(
            "Pares quase idênticos revisados: manter separados e registrar "
            "justificativa; similaridade textual não é equivalência."
        )
    if catalog_not_in_config or config_not_in_catalog:
        recommendations.append("Sincronizar catálogo e opencode.json.")
    if missing:
        recommendations.append("Corrigir spec/test ausentes ou remover referências.")
    if not recommendations:
        recommendations.append("Nenhuma duplicidade textual detectada; revisão humana ainda é necessária.")

    payload = {
        "schema_version": 1,
        "catalog_dir": str(catalog_dir),
        "config_path": str(config_path),
        "counts": {
            "catalog_files": len(records),
            "catalog_ids": len(catalog_ids),
            "config_agents": len(agents),
            "config_mcps": len(mcps),
        },
        "duplicates": {
            "catalog_ids": duplicate_ids,
            "declared_agent_ids": duplicate_declared_ids,
            "metadata_id_mismatches": metadata_id_mismatches,
            "legacy_baseline_mismatches": legacy_baseline_mismatches,
            "catalog_names": duplicate_names,
            "config_prompts": duplicate_prompts,
            "mcp_signatures": duplicate_mcp,
        },
        "near_duplicate_agents": near_duplicates,
        "reviewed_near_duplicates": reviewed_near,
        "drift": {
            "catalog_not_in_config": catalog_not_in_config,
            "config_not_in_catalog": config_not_in_catalog,
        },
        "missing_artifacts": missing[: int(max_missing_examples)],
        "missing_artifacts_total": len(missing),
        "recommendations": recommendations,
        "limits": LIMITS,
        "auto_removed": False,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    payload["report_sha256"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Audita duplicidade de agentes e MCPs (R1150)."
    )
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--threshold", type=float, default=0.9)
    parser.add_argument("--max-near", type=int, default=50)
    args = parser.parse_args(argv)
    report = audit_catalog(
        catalog_dir=args.catalog,
        config_path=args.config,
        baseline_path=args.baseline,
        near_duplicate_threshold=args.threshold,
        max_near_duplicates=args.max_near,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary = {
        "counts": report["counts"],
        "duplicate_ids": len(report["duplicates"]["catalog_ids"]),
        "duplicate_declared_ids": len(report["duplicates"]["declared_agent_ids"]),
        "metadata_id_mismatches": len(report["duplicates"]["metadata_id_mismatches"]),
        "legacy_baseline_mismatches": len(
            report["duplicates"]["legacy_baseline_mismatches"]
        ),
        "duplicate_names": len(report["duplicates"]["catalog_names"]),
        "duplicate_prompts": len(report["duplicates"]["config_prompts"]),
        "duplicate_mcp": len(report["duplicates"]["mcp_signatures"]),
        "near_duplicates": len(report["near_duplicate_agents"]),
        "reviewed_near_duplicates": len(report["reviewed_near_duplicates"]),
        "drift": {
            key: len(value)
            for key, value in report["drift"].items()
        },
        "missing_artifacts": report["missing_artifacts_total"],
        "report": str(output),
        "report_sha256": report["report_sha256"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
