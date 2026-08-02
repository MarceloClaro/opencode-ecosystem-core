#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o manifesto de deriva R361→R362 sem reescrever o predecessor."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "projetos" / "molambudos" / "Molambudos_VictoriaRegia"
BASE = ROOT / "validacao_externa" / "cultural_episteme"
MATRIX_PATH = BASE / "molambudos_r361_decision_matrix.json"
DRIFT_PATH = BASE / "molambudos_r361_provenance_drift.json"
SOURCES_PATH = BASE / "molambudos_r361_sources.json"
CONTROL_PATH = BASE / "molambudos_r361_control_gates.json"
R360_REVIEWS_PATH = BASE / "molambudos_r360_reviews.json"
OUTPUT_PATH = BASE / "molambudos_r362_change_manifest.json"

EXPECTED_BLOCKERS = {
    "patu_1915_chronology",
    "hospital_closed_1980",
    "rasga_mortalha_beak_etiology",
    "molambudo_absolute_neologism",
    "victim_count_category_drift",
    "pseudoarchive_authenticity",
    "fictional_victim_insertion",
    "living_memory_erasure",
    "psychiatric_stigma_horror",
    "reader_consent_visual_provenance",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _workspace_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"caminho fora do workspace: {relative}")
    return path


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        directory_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


def _verifiable_records(r361_drift: dict[str, Any]) -> list[dict[str, Any]]:
    """Usa somente baselines SHA-256 realmente publicados pela R361."""

    records = []
    for predecessor in r361_drift.get("records", []):
        relative = predecessor["path"]
        path = _workspace_path(relative)
        if not path.is_file():
            raise FileNotFoundError(path)
        old_hash = predecessor["new_sha256"]
        new_hash = _sha256(path)
        if old_hash == new_hash:
            raise RuntimeError(f"arquivo esperado como derivado não mudou após R361: {relative}")
        records.append(
            {
                "path": relative,
                "change_class": "route_a_historical_rewrite_after_r361",
                "old_sha256": old_hash,
                "new_sha256": new_hash,
                "baseline_source": "molambudos_r361_provenance_drift.json::records[].new_sha256",
                "predecessor_change_class": predecessor.get("change_class"),
                "snapshot_preserved": True,
                "scope": "hash integral alterado pela rota A; o snapshot e o parecer R361 não foram reatribuídos ao corpus R362",
            }
        )
    if len(records) != 3:
        raise RuntimeError(f"esperados três hashes de deriva R361; encontrados {len(records)}")

    # A R361 declarou que somente os três arquivos acima sofreram correção
    # mecânica. Portanto, locators R360 dos demais arquivos continuaram sendo
    # a baseline efetiva R361. Reaproveitá-los é verificável; inventar hashes
    # para qualquer outro arquivo não é.
    known_paths = {item["path"] for item in records}
    r360 = _load(R360_REVIEWS_PATH)
    inherited: dict[str, dict[str, Any]] = {}
    for review in r360.get("reviews", []):
        for locator_role, locator in review.get("source_locators", {}).items():
            relative = locator["path"]
            if relative in known_paths:
                continue
            path = _workspace_path(relative)
            if not path.is_file():
                raise FileNotFoundError(path)
            current = _sha256(path)
            if current == locator["sha256"]:
                continue
            entry = inherited.setdefault(
                relative,
                {
                    "path": relative,
                    "change_class": "route_a_historical_rewrite_after_inherited_r360_snapshot",
                    "old_sha256": locator["sha256"],
                    "new_sha256": current,
                    "baseline_source": "molambudos_r360_reviews.json::reviews[].source_locators (inalterado pela R361)",
                    "snapshot_preserved": True,
                    "scope": "a R361 limitou edições mecânicas a outros três caminhos; este digest R360 foi herdado como baseline R361",
                    "affected_reviews": [],
                },
            )
            if entry["old_sha256"] != locator["sha256"] or entry["new_sha256"] != current:
                raise RuntimeError(f"locators R360 conflitantes para {relative}")
            affected = {"review_id": review["review_id"], "locator_role": locator_role}
            if affected not in entry["affected_reviews"]:
                entry["affected_reviews"].append(affected)
    records.extend(inherited[path] for path in sorted(inherited))
    return records


def _unhashed_inventory(skip_paths: set[str]) -> list[dict[str, Any]]:
    """Explicita arquivos sem hash-base R361, sem inventar um digest antigo."""

    route_files = (
        "mem/MEM-02.tex", "mem/MEM-04.tex", "mem/MEM-06.tex",
        "doc/DOC-02.tex", "doc/DOC-05.tex", "doc/DOC-08.tex",
        "doc/DOC-15.tex", "doc/DOC-17.tex", "doc/DOC-18.tex", "luc/LUC-10.tex",
    )
    candidates = []
    for root in ("fragmentos", "en/fragmentos", "zh/fragmentos"):
        candidates.extend(f"{root}/{relative}" for relative in route_files)
    candidates.extend(
        (
            "frontmatter/glossario_historico.tex",
            "en/frontmatter/glossario_historico.tex",
            "zh/frontmatter/glossario_historico.tex",
            "tri/frontmatter/glossario.tex",
            "frontmatter/nota_historica.tex",
            "en/frontmatter/nota_historica.tex",
            "zh/frontmatter/nota_historica.tex",
            "tri/frontmatter/nota_historica.tex",
            "main.tex",
            "en/main_en.tex",
            "zh/main_zh.tex",
            "tri/main_tri.tex",
            "frontmatter/titlepage.tex",
            "en/frontmatter/titlepage.tex",
            "zh/frontmatter/titlepage.tex",
            "tri/frontmatter/titlepage.tex",
            "frontmatter/cuidado.tex",
            "en/frontmatter/cuidado.tex",
            "zh/frontmatter/cuidado.tex",
            "tri/frontmatter/cuidado.tex",
            "misc/options.sty",
            "misc/options_zh.sty",
        )
    )
    seen: set[str] = set()
    inventory = []
    for relative in candidates:
        if relative in seen:
            continue
        seen.add(relative)
        path = BOOK / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rooted_relative = str(path.relative_to(ROOT))
        if rooted_relative in skip_paths:
            continue
        inventory.append(
            {
                "path": rooted_relative,
                "current_sha256": _sha256(path),
                "baseline_sha256_available": False,
                "reason": "R361 não publicou hash integral deste arquivo; nenhum hash antigo foi fabricado.",
            }
        )
    return inventory


def _artifact_merkle(records: list[dict[str, Any]]) -> str:
    material = "".join(
        f"{item['path']}\0{item['sha256']}\n"
        for item in sorted(records, key=lambda item: item["path"])
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def validate_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    """Revalida cada elo publicado; a âncora é interna, não notarizada."""

    errors: list[str] = []
    matrix = _load(MATRIX_PATH)
    drift = _load(DRIFT_PATH)
    r360 = _load(R360_REVIEWS_PATH)
    mechanical_paths = {item["path"] for item in matrix.get("mechanical_changes", [])}
    expected_mechanical_paths = {item["path"] for item in drift.get("records", [])}
    if mechanical_paths != expected_mechanical_paths:
        errors.append("caminhos mecânicos R361 divergem do manifesto de deriva R361")

    predecessor_records = payload.get("predecessor_artifacts", [])
    for record in predecessor_records:
        try:
            path = _workspace_path(record["path"])
            if not path.is_file() or _sha256(path) != record.get("sha256"):
                errors.append(f"artefato predecessor divergente: {record.get('path')}")
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
    if _artifact_merkle(predecessor_records) != payload.get("predecessor_artifact_merkle_sha256"):
        errors.append("raiz Merkle dos artefatos predecessor diverge")

    drift_by_path = {item["path"]: item for item in drift.get("records", [])}
    locators: dict[str, list[dict[str, Any]]] = {}
    for review in r360.get("reviews", []):
        for role, locator in review.get("source_locators", {}).items():
            locators.setdefault(locator["path"], []).append(
                {
                    "sha256": locator["sha256"],
                    "review_id": review["review_id"],
                    "locator_role": role,
                }
            )

    record_paths: set[str] = set()
    for record in payload.get("records", []):
        relative = record.get("path", "")
        try:
            path = _workspace_path(relative)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if relative in record_paths:
            errors.append(f"registro de deriva duplicado: {relative}")
        record_paths.add(relative)
        if not path.is_file() or _sha256(path) != record.get("new_sha256"):
            errors.append(f"new_sha256 divergente: {relative}")
        if record.get("old_sha256") == record.get("new_sha256"):
            errors.append(f"deriva vazia: {relative}")
        if record.get("baseline_source", "").startswith("molambudos_r361"):
            predecessor = drift_by_path.get(relative)
            if predecessor is None or predecessor.get("new_sha256") != record.get("old_sha256"):
                errors.append(f"old_sha256 não ancora no R361 drift: {relative}")
        elif record.get("baseline_source", "").startswith("molambudos_r360"):
            matching = [
                item for item in locators.get(relative, [])
                if item["sha256"] == record.get("old_sha256")
            ]
            if not matching or relative in mechanical_paths:
                errors.append(f"baseline R360 não herdável pela R361: {relative}")
        else:
            errors.append(f"baseline não reconhecida: {relative}")
        if record.get("snapshot_preserved") is not True:
            errors.append(f"snapshot não preservado: {relative}")

    inventory_paths: set[str] = set()
    for item in payload.get("unhashed_change_inventory", []):
        relative = item.get("path", "")
        try:
            path = _workspace_path(relative)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if relative in record_paths or relative in inventory_paths:
            errors.append(f"inventário sobreposto/duplicado: {relative}")
        inventory_paths.add(relative)
        if not path.is_file() or _sha256(path) != item.get("current_sha256"):
            errors.append(f"hash atual do inventário diverge: {relative}")
        if item.get("baseline_sha256_available") is not False:
            errors.append(f"item sem baseline marcado incorretamente: {relative}")

    return {
        "passed": not errors,
        "errors": errors,
        "validated_record_count": len(record_paths),
        "validated_unhashed_inventory_count": len(inventory_paths),
        "validated_predecessor_artifact_count": len(predecessor_records),
        "externally_notarized": False,
        "scope": "âncora criptográfica interna; não substitui assinatura, commit ou notarização externa",
    }


def generate_manifest() -> dict[str, Any]:
    matrix = _load(MATRIX_PATH)
    drift = _load(DRIFT_PATH)
    blockers = matrix.get("historical_blockers", [])
    ids = {item.get("blocker_id") for item in blockers}
    if ids != EXPECTED_BLOCKERS or len(blockers) != 10:
        raise RuntimeError("inventário de bloqueios R361 divergente do contrato R362")

    updated_blockers = []
    for original in blockers:
        item = dict(original)
        if item["blocker_id"] == "patu_1915_chronology":
            item.update(
                {
                    "status": "implemented_pending_external_review",
                    "automatic_change_applied": True,
                    "author_decision": "route_a",
                    "external_review_pending": True,
                    "release_conferred": False,
                }
            )
        else:
            item["status"] = "blocked_author_decision"
            item["automatic_change_applied"] = False
        updated_blockers.append(item)

    predecessor_paths = (
        MATRIX_PATH,
        DRIFT_PATH,
        SOURCES_PATH,
        CONTROL_PATH,
        R360_REVIEWS_PATH,
    )
    records = _verifiable_records(drift)
    predecessor_artifacts = [
        {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
        for path in predecessor_paths
    ]
    payload = {
        "spec_id": "SPEC-935-R362",
        "predecessor_spec_id": "SPEC-935-R361",
        "generated_at": "2026-08-01",
        "predecessor_artifact_mutated": False,
        "predecessor_integrity_scope": "âncora interna capturada na R362; sem notarização externa",
        "external_validation": False,
        "human_review_required": True,
        "release_gate": "blocked",
        "quality_verdict_allowed": False,
        "predecessor_artifacts": predecessor_artifacts,
        "predecessor_artifact_merkle_sha256": _artifact_merkle(predecessor_artifacts),
        "records": records,
        "unhashed_change_inventory": _unhashed_inventory({item["path"] for item in records}),
        "blockers": updated_blockers,
        "route_a_contract": {
            "origin": "Senador Pompeu, Ceará, 1915",
            "displacement": "retirada em direção a Fortaleza",
            "confinement": "Campo do Alagadiço, Fortaleza, 1915",
            "patu_historical_period": "1932--1933",
            "fictional_transfer": "1917; sem alegar funcionamento contínuo do Alagadiço",
            "status": "implemented_pending_external_review",
        },
        "safe_claim": (
            "A decisão autoral da rota A foi implementada internamente e permanece "
            "pendente de revisão externa. Os outros nove bloqueios R361 continuam "
            "fechados e impedem o release."
        ),
    }
    payload["provenance_validation"] = validate_manifest(payload)
    if not payload["provenance_validation"]["passed"]:
        raise RuntimeError(
            f"manifesto de proveniência R362 reprovado: {payload['provenance_validation']}"
        )
    _atomic_write(OUTPUT_PATH, payload)
    return payload


def main() -> int:
    payload = generate_manifest()
    print(
        f"R362 manifest: {len(payload['records'])} baselines verificáveis; "
        f"{len(payload['unhashed_change_inventory'])} arquivos sem hash-base inventado; "
        "release bloqueado."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
