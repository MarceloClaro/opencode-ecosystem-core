# -*- coding: utf-8 -*-
"""Contestabilidade e saída (SPEC-935-R1132).

Auditoria estrutural de cinco portas: exportação, segunda pessoa, documentação,
apelação e saída. São proxies observáveis; não provam usabilidade, justiça ou
qualidade. Servem para recusar releases que não deixam portas abertas.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ContestabilityCheck:
    name: str
    passed: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContestabilityReport:
    checks: list[ContestabilityCheck]
    score: float
    gaps: list[str]
    structural_proxy: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [check.to_dict() for check in self.checks],
            "score": self.score,
            "gaps": self.gaps,
            "structural_proxy": self.structural_proxy,
        }


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return ""


def _check_export(root: Path) -> ContestabilityCheck:
    text = _read(root / "README.md") + "\n" + _read(root / "MANUAL.md")
    passed = any(term in text for term in ("export", "exportar", "backup", "distribuição"))
    return ContestabilityCheck(
        "export",
        passed,
        "Exportação/backup mencionada na documentação." if passed
        else "Documentação não menciona exportação, backup ou distribuição.",
    )


def _check_second_person(root: Path) -> ContestabilityCheck:
    required = ["README.md", "MANUAL.md", "install.sh"]
    missing = [name for name in required if not (root / name).exists()]
    return ContestabilityCheck(
        "second_person",
        not missing,
        "Instalação e operação documentadas para outra pessoa." if not missing
        else f"Faltam artefatos para segunda pessoa: {missing}.",
    )


def _check_documentation(root: Path) -> ContestabilityCheck:
    docs = root / "docs"
    count = len(list(docs.glob("*.md"))) if docs.exists() else 0
    passed = count >= 5 and (root / "MANUAL.md").exists()
    return ContestabilityCheck(
        "documentation",
        passed,
        f"{count} documentos em docs/ e MANUAL.md presente." if passed
        else f"Documentação insuficiente: {count} arquivos em docs/.",
    )


def _check_appeal(root: Path) -> ContestabilityCheck:
    passed = (root / "CORRIGENDUM.md").exists() and (
        root / "mci" / "metacognitive_gate.py"
    ).exists()
    return ContestabilityCheck(
        "appeal",
        passed,
        "Correção pública e gate metacognitivo presentes." if passed
        else "Falta CORRIGENDUM.md ou gate metacognitivo para contestação.",
    )


def _check_exit(root: Path) -> ContestabilityCheck:
    text = _read(root / "README.md") + "\n" + _read(root / "MANUAL.md")
    passed = (
        (root / "uninstall.sh").exists()
        and (root / "LICENSE").exists()
        and ((root / "DISTRIBUICAO.md").exists() or "uninstall" in text or "sair" in text)
    )
    return ContestabilityCheck(
        "exit",
        passed,
        "Saída documentada (uninstall, licença e distribuição)." if passed
        else "Saída incompleta: falta uninstall.sh, LICENSE ou menção a saída.",
    )


def audit(repo_root: str | Path) -> ContestabilityReport:
    root = Path(repo_root)
    checks = [
        _check_export(root),
        _check_second_person(root),
        _check_documentation(root),
        _check_appeal(root),
        _check_exit(root),
    ]
    score = round(sum(1 for check in checks if check.passed) / len(checks), 3)
    gaps = [check.name for check in checks if not check.passed]
    return ContestabilityReport(checks=checks, score=score, gaps=gaps)


def require(report: ContestabilityReport, *, min_score: float = 0.8) -> None:
    if not isinstance(report, ContestabilityReport):
        raise ValueError("report deve ser ContestabilityReport")
    if not 0.0 <= min_score <= 1.0:
        raise ValueError("min_score deve estar em [0, 1]")
    if report.score < min_score:
        raise ValueError(
            f"contestabilidade insuficiente: score {report.score} < {min_score}; lacunas: {report.gaps}"
        )
