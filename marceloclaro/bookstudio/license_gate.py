"""Gate de licença para adaptadores e bibliotecas do Book Studio.

Regra central: GPL/AGPL não entram como biblioteca nem como código nativo.
Elas só podem ser chamadas como processo externo (adapter) ou estudadas
(reference). Licenças fracas (LGPL/MPL) exigem revisão e linkagem dinâmica.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List


class LicenseViolation(RuntimeError):
    """O manifesto contém uma combinação de licença e integração proibida."""


class LicenseClass(str, Enum):
    PERMISSIVE = "permissive"
    WEAK_COPYLEFT = "weak_copyleft"
    STRONG_COPYLEFT = "strong_copyleft"
    SOURCE_AVAILABLE = "source_available"
    UNKNOWN = "unknown"


class IntegrationMode(str, Enum):
    CORE_NATIVE = "core-native"
    ADAPTER = "adapter"
    LIBRARY = "library"
    REFERENCE = "reference"
    AVOID = "avoid"


CODE_MODES = {IntegrationMode.CORE_NATIVE, IntegrationMode.LIBRARY}


def classify_license(name: str) -> LicenseClass:
    if not isinstance(name, str) or not name.strip():
        return LicenseClass.UNKNOWN
    upper = name.upper()
    if "REMOTION" in upper or "TLDRAW" in upper or "NÃO OSI" in upper or "NON-OSI" in upper:
        return LicenseClass.SOURCE_AVAILABLE
    if "AGPL" in upper:
        return LicenseClass.STRONG_COPYLEFT
    if "LGPL" in upper:
        return LicenseClass.WEAK_COPYLEFT
    if "GPL" in upper:
        return LicenseClass.STRONG_COPYLEFT
    if "MPL" in upper or "EPL" in upper:
        return LicenseClass.WEAK_COPYLEFT
    if any(token in upper for token in (
        "MIT", "APACHE", "BSD", "ISC", "CC0", "LPPL",
        "IMAGEMAGICK", "PUBLIC DOMAIN", "UNLICENSE",
    )):
        return LicenseClass.PERMISSIVE
    return LicenseClass.UNKNOWN


@dataclass(frozen=True)
class LicenseDecision:
    repo: str
    license: str
    license_class: LicenseClass
    mode: IntegrationMode
    allowed: bool
    review_required: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repo": self.repo,
            "license": self.license,
            "license_class": self.license_class.value,
            "mode": self.mode.value,
            "allowed": self.allowed,
            "review_required": self.review_required,
            "reason": self.reason,
        }


def evaluate(repo: str, license_name: str, mode: str | IntegrationMode) -> LicenseDecision:
    mode = mode if isinstance(mode, IntegrationMode) else IntegrationMode(mode)
    klass = classify_license(license_name)

    if mode == IntegrationMode.AVOID:
        return LicenseDecision(repo, license_name, klass, mode, True, False,
                               "modo avoid: não integrado")

    if klass == LicenseClass.STRONG_COPYLEFT and mode in CODE_MODES:
        return LicenseDecision(
            repo, license_name, klass, mode, False, True,
            "GPL/AGPL não pode ser library nem core-native; usar CLI externo ou referência",
        )
    if klass == LicenseClass.SOURCE_AVAILABLE and mode in CODE_MODES:
        return LicenseDecision(
            repo, license_name, klass, mode, False, True,
            "licença source-available com restrição comercial; não usar como código central",
        )
    if klass == LicenseClass.UNKNOWN and mode in CODE_MODES:
        return LicenseDecision(
            repo, license_name, klass, mode, False, True,
            "licença desconhecida; exigir revisão jurídica antes de importar",
        )
    if klass == LicenseClass.WEAK_COPYLEFT and mode == IntegrationMode.LIBRARY:
        return LicenseDecision(
            repo, license_name, klass, mode, True, True,
            "copyleft fraco: permitido com linkagem dinâmica e revisão",
        )
    if klass == LicenseClass.UNKNOWN:
        return LicenseDecision(
            repo, license_name, klass, mode, True, True,
            "licença desconhecida: permitido apenas como CLI/referência com revisão",
        )
    return LicenseDecision(repo, license_name, klass, mode, True, False,
                           "combinação permitida")


def validate_landscape(path: str | Path) -> Dict[str, Any]:
    target = Path(path).expanduser().resolve()
    data = json.loads(target.read_text(encoding="utf-8"))
    repos = data.get("repos")
    if not isinstance(repos, list):
        raise LicenseViolation("manifesto sem lista 'repos'")

    decisions: List[LicenseDecision] = []
    for row in repos:
        if not isinstance(row, dict):
            raise LicenseViolation("entrada de repositório inválida")
        decisions.append(evaluate(
            str(row.get("repo", "?")),
            str(row.get("license", "")),
            str(row.get("integration", "unknown")),
        ))

    violations = [d for d in decisions if not d.allowed]
    review = [d for d in decisions if d.allowed and d.review_required]
    by_class: Dict[str, int] = {}
    for decision in decisions:
        by_class[decision.license_class.value] = by_class.get(decision.license_class.value, 0) + 1
    return {
        "status": "ok" if not violations else "violations",
        "path": str(target),
        "count": len(decisions),
        "by_class": by_class,
        "violations": [d.to_dict() for d in violations],
        "review_required": [d.to_dict() for d in review],
    }


def assert_landscape(path: str | Path) -> Dict[str, Any]:
    result = validate_landscape(path)
    if result["status"] != "ok":
        raise LicenseViolation(
            "violações de licença: " + ", ".join(v["repo"] for v in result["violations"])
        )
    return result
