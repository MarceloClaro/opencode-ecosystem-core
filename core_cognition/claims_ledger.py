# -*- coding: utf-8 -*-
"""Claims ledger estruturado (SPEC-935-R1132).

Cada claim tem status, evidência, falsificador, validação externa e histórico.
A promoção a ``externally_validated`` exige verificador independente e hash de
artefato. O ledger organiza evidência; não a produz.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
VALID_STATUSES = frozenset(
    {
        "observation",
        "inference",
        "hypothesis",
        "tested",
        "externally_validated",
        "refuted",
    }
)
_REQUIRED = ("claim_id", "text", "status", "falsifier")


@dataclass(frozen=True)
class Claim:
    claim_id: str
    text: str
    status: str
    falsifier: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    source_sha256: str = ""
    external_validation: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(value: Any, field_name: str, *, limit: int = 4000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{field_name} deve ser texto não vazio e <= {limit} caracteres")
    return value.strip()


def _valid_external(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and value.get("independent") is True
        and isinstance(value.get("verifier"), str)
        and bool(value["verifier"].strip())
        and isinstance(value.get("artifact_sha256"), str)
        and bool(_HEX64.fullmatch(value["artifact_sha256"]))
    )


def validate_claim(data: dict[str, Any]) -> Claim:
    if not isinstance(data, dict):
        raise ValueError("claim deve ser um objeto")
    missing = [field for field in _REQUIRED if field not in data]
    if missing:
        raise ValueError(f"claim incompleto; faltam: {sorted(missing)}")

    claim_id = _text(data["claim_id"], "claim_id", limit=120)
    text = _text(data["text"], "text")
    falsifier = _text(data["falsifier"], "falsifier")
    status = _text(data["status"], "status", limit=40).lower()
    if status not in VALID_STATUSES:
        raise ValueError(f"status inválido: {status}")

    evidence = data.get("evidence", [])
    if not isinstance(evidence, list) or any(not isinstance(item, dict) for item in evidence):
        raise ValueError("evidence deve ser lista de objetos")

    source_sha256 = data.get("source_sha256", "")
    if source_sha256:
        if not isinstance(source_sha256, str) or not _HEX64.fullmatch(source_sha256):
            raise ValueError("source_sha256 deve ser sha256 hexadecimal de 64 caracteres")

    external = data.get("external_validation")
    if status == "externally_validated" and not _valid_external(external):
        raise ValueError(
            "status externally_validated exige external_validation independente, "
            "verifier e artifact_sha256"
        )

    history = data.get("history", [])
    if not isinstance(history, list) or any(not isinstance(item, dict) for item in history):
        raise ValueError("history deve ser lista de objetos")

    return Claim(
        claim_id=claim_id,
        text=text,
        status=status,
        falsifier=falsifier,
        evidence=list(evidence),
        source_sha256=source_sha256,
        external_validation=external,
        history=list(history),
    )


def load_ledger(path: str | Path) -> list[Claim]:
    target = Path(path)
    if not target.exists():
        return []
    claims: list[Claim] = []
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"linha {line_number} não é JSON válido") from exc
        claims.append(validate_claim(payload))
    return claims


def append_claim(path: str | Path, data: dict[str, Any]) -> Claim:
    claim = validate_claim(data)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(claim.to_dict(), ensure_ascii=False) + "\n")
    return claim


def promote(
    claim: Claim | dict[str, Any],
    external_validation: dict[str, Any],
    *,
    note: str = "",
) -> Claim:
    current = claim if isinstance(claim, Claim) else validate_claim(claim)
    if not _valid_external(external_validation):
        raise ValueError("promoção exige validação externa independente, verifier e artifact_sha256")
    history = list(current.history)
    history.append(
        {
            "action": "promote",
            "from": current.status,
            "to": "externally_validated",
            "verifier": external_validation["verifier"],
            "artifact_sha256": external_validation["artifact_sha256"],
            "note": note.strip(),
        }
    )
    return Claim(
        claim_id=current.claim_id,
        text=current.text,
        status="externally_validated",
        falsifier=current.falsifier,
        evidence=list(current.evidence),
        source_sha256=current.source_sha256,
        external_validation=external_validation,
        history=history,
    )


def overclaims(claims: Iterable[Claim]) -> list[Claim]:
    return [
        claim
        for claim in claims
        if claim.status == "externally_validated" and not _valid_external(claim.external_validation)
    ]


def audit_ledger(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {
            "status": "warn",
            "total": 0,
            "message": "ledger ausente; use claims_template() para iniciar.",
            "overclaims": [],
            "invalid": [],
        }

    claims: list[Claim] = []
    invalid: list[dict[str, Any]] = []
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            claims.append(validate_claim(json.loads(line)))
        except (ValueError, json.JSONDecodeError) as exc:
            invalid.append({"line": line_number, "error": str(exc)})

    bad = overclaims(claims)
    counts: dict[str, int] = {}
    for claim in claims:
        counts[claim.status] = counts.get(claim.status, 0) + 1
    return {
        "status": "fail" if bad or invalid else "pass",
        "total": len(claims),
        "counts": counts,
        "overclaims": [claim.claim_id for claim in bad],
        "invalid": invalid,
    }


def claims_template() -> dict[str, Any]:
    return {
        "claim_id": "CLAIM-001",
        "text": "Descreva a alegação de forma verificável.",
        "status": "hypothesis",
        "falsifier": "Descreva o resultado que refutaria a alegação.",
        "evidence": [],
        "source_sha256": "",
        "external_validation": None,
        "history": [],
    }


def write_template(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(claims_template(), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target
