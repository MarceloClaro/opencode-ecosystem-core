"""R1054 — gate de validação externa, aceite editorial e autorização.

O módulo não valida ciência por conta própria, não emite aceite e não publica.
Ele exige artefatos externos assinados, confere hashes e registra o estado.
Sem artefato independente e decisão editorial verificável, o gate fica blocked.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scientific_lab.native.common import dump, load, now, sha256_file

SCHEMA_VERSION = "1.0"


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise ValueError(f"artefato ausente: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"artefato ilegível: {path}") from exc
    if not isinstance(data, dict):
        raise ValueError("artefato deve ser objeto")
    return data


def _manuscript(out: Path) -> Path:
    path = out / "06_manuscript/manuscript.md"
    if not path.exists():
        raise ValueError("manuscrito ausente")
    return path


def attach_external_validation(out: str | Path, artifact_path: str | Path) -> dict:
    out = Path(out).resolve()
    manuscript = _manuscript(out)
    artifact = _load_json(Path(artifact_path))
    if artifact.get("independent") is not True:
        raise ValueError("validação externa exige independent=true")
    if not isinstance(artifact.get("verifier"), str) or not artifact["verifier"].strip():
        raise ValueError("validação externa exige verifier")
    if artifact.get("verdict") not in {"passed", "failed", "partial"}:
        raise ValueError("verdict deve ser passed, failed ou partial")
    if not isinstance(artifact.get("scope"), str) or not artifact["scope"].strip():
        raise ValueError("validação externa exige scope")
    if not isinstance(artifact.get("signed_at"), str) or len(artifact["signed_at"]) < 10:
        raise ValueError("validação externa exige signed_at")
    expected = sha256_file(manuscript)
    if artifact.get("artifact_sha256") != expected:
        raise ValueError("hash do manuscrito não corresponde ao artefato externo")
    record = {
        "schema_version": SCHEMA_VERSION,
        "validation_id": artifact.get("validation_id"),
        "attached_at": now(),
        "source_path": str(artifact_path),
        "artifact_sha256": expected,
        "verifier": artifact["verifier"],
        "independent": True,
        "verdict": artifact["verdict"],
        "scope": artifact["scope"],
        "signed_at": artifact["signed_at"],
        "evidence": artifact.get("evidence", []),
        "truth_claim": False,
        "external_validation": True,
        "human_review_required": True,
        "limitations": [
            "O gate confere o artefato; não reproduz a validação externa.",
            "Validação externa não é verdade absoluta.",
        ],
    }
    dump(out / "09_provenance/external-validation.json", record)
    return record


def attach_acceptance(out: str | Path, artifact_path: str | Path) -> dict:
    out = Path(out).resolve()
    _manuscript(out)
    artifact = _load_json(Path(artifact_path))
    if artifact.get("decision") != "accepted":
        raise ValueError("aceite editorial exige decision=accepted")
    for field in ("journal", "decision_date", "editor"):
        if not isinstance(artifact.get(field), str) or not artifact[field].strip():
            raise ValueError(f"aceite editorial exige {field}")
    letter = Path(artifact.get("letter_path", ""))
    if not letter.is_absolute():
        letter = (Path(artifact_path).parent / letter).resolve()
    if not letter.exists():
        raise ValueError("carta de aceite ausente")
    if artifact.get("letter_sha256") != sha256_file(letter):
        raise ValueError("hash da carta de aceite não corresponde")
    record = {
        "schema_version": SCHEMA_VERSION,
        "acceptance_id": artifact.get("acceptance_id"),
        "attached_at": now(),
        "source_path": str(artifact_path),
        "journal": artifact["journal"],
        "decision": "accepted",
        "decision_date": artifact["decision_date"],
        "editor": artifact["editor"],
        "letter_path": str(letter),
        "letter_sha256": artifact["letter_sha256"],
        "doi": artifact.get("doi"),
        "truth_claim": False,
        "external_validation": True,
        "human_review_required": True,
        "limitations": [
            "O gate confere a carta; não emite aceite.",
            "Aceite editorial não é publicação.",
        ],
    }
    dump(out / "09_provenance/editorial-acceptance.json", record)
    return record


def attach_authorization(out: str | Path, artifact_path: str | Path) -> dict:
    out = Path(out).resolve()
    manuscript = _manuscript(out)
    artifact = _load_json(Path(artifact_path))
    if artifact.get("human_confirmation") is not True:
        raise ValueError("autorização exige human_confirmation=true")
    for field in ("author_name", "authorized_at"):
        if not isinstance(artifact.get(field), str) or not artifact[field].strip():
            raise ValueError(f"autorização exige {field}")
    if artifact.get("manuscript_sha256") != sha256_file(manuscript):
        raise ValueError("autorização não corresponde ao manuscrito atual")
    record = {
        "schema_version": SCHEMA_VERSION,
        "attached_at": now(),
        "source_path": str(artifact_path),
        "author_name": artifact["author_name"],
        "authorized_at": artifact["authorized_at"],
        "manuscript_sha256": artifact["manuscript_sha256"],
        "human_confirmation": True,
        "truth_claim": False,
        "human_review_required": True,
    }
    dump(out / "09_provenance/publication-authorization.json", record)
    return record


def publication_gate(out: str | Path) -> dict:
    out = Path(out).resolve()
    manuscript = _manuscript(out)
    current_hash = sha256_file(manuscript)
    external = (
        load(out / "09_provenance/external-validation.json")
        if (out / "09_provenance/external-validation.json").exists()
        else None
    )
    acceptance = (
        load(out / "09_provenance/editorial-acceptance.json")
        if (out / "09_provenance/editorial-acceptance.json").exists()
        else None
    )
    authorization = (
        load(out / "09_provenance/publication-authorization.json")
        if (out / "09_provenance/publication-authorization.json").exists()
        else None
    )
    reasons = []
    if external is None:
        reasons.append("external_validation_missing")
    elif external.get("verdict") != "passed":
        reasons.append("external_validation_not_passed")
    elif external.get("artifact_sha256") != current_hash:
        reasons.append("external_validation_hash_mismatch")
    if acceptance is None:
        reasons.append("editorial_acceptance_missing")
    elif acceptance.get("decision") != "accepted":
        reasons.append("editorial_acceptance_not_accepted")
    if authorization is None:
        reasons.append("authorization_missing")
    elif authorization.get("manuscript_sha256") != current_hash:
        reasons.append("authorization_hash_mismatch")
    cleared = not reasons
    return {
        "schema_version": SCHEMA_VERSION,
        "gate_id": "R1054-PUBLICATION-GATE",
        "generated_at": now(),
        "status": "cleared_for_publication" if cleared else "blocked",
        "reasons": reasons,
        "manuscript_sha256": current_hash,
        "external_validation": bool(
            external and external.get("verdict") == "passed"
            and external.get("artifact_sha256") == current_hash
        ),
        "external_validation_artifact": external,
        "editorial_acceptance_artifact": acceptance,
        "authorization_artifact": authorization,
        "publication_performed": False,
        "truth_claim": False,
        "human_review_required": True,
        "limitations": [
            "O gate não publica, não submete e não emite aceite.",
            "Cleared_for_publication significa apenas que os artefatos exigidos estão presentes e coerentes.",
            "A decisão editorial e a publicação pertencem ao periódico e ao autor.",
        ],
    }


def write_gate(out: str | Path, result: dict) -> Path:
    path = Path(out) / "09_provenance/publication-gate.json"
    dump(path, result)
    return path
