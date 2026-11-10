# -*- coding: utf-8 -*-
"""Mapa explícito de funções cognitivas externalizadas pelo Core.

Cada entrada declara: função, módulo, mecanismo, falha endereçada, evidência e
limite. O mapa é um contrato de leitura, não uma prova de eficácia.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FUNCTIONS = frozenset(
    {
        "memory",
        "executive_function",
        "attention",
        "verification",
        "interruption",
        "reflection",
        "trust",
        "orientation",
    }
)

_REQUIRED_FIELDS = (
    "function",
    "module",
    "mechanism",
    "failure_addressed",
    "evidence",
    "limit",
)


@dataclass(frozen=True)
class CognitiveFunction:
    """Uma função cognitiva externalizada e seu contrato de leitura."""

    function: str
    module: str
    mechanism: str
    failure_addressed: str
    evidence: str
    limit: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def default_map_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "cognitive_function_map.json"


def _text(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"campo {field!r} deve ser texto não vazio")
    return value.strip()


def validate_map(data: Any) -> list[CognitiveFunction]:
    """Valida a estrutura do mapa e devolve entradas tipadas."""

    if not isinstance(data, list) or not data:
        raise ValueError("o mapa deve ser uma lista não vazia")

    functions: list[CognitiveFunction] = []
    seen: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("cada entrada do mapa deve ser um objeto")
        missing = [field for field in _REQUIRED_FIELDS if field not in item]
        if missing:
            raise ValueError(f"entrada incompleta; faltam: {sorted(missing)}")
        values = {field: _text(item[field], field=field) for field in _REQUIRED_FIELDS}
        name = values["function"]
        if name in seen:
            raise ValueError(f"função duplicada: {name}")
        seen.add(name)
        functions.append(CognitiveFunction(**values))
    return functions


def load_map(path: str | Path | None = None) -> list[CognitiveFunction]:
    target = Path(path) if path is not None else default_map_path()
    data = json.loads(target.read_text(encoding="utf-8"))
    return validate_map(data)


def to_dicts(functions: Iterable[CognitiveFunction]) -> list[dict[str, str]]:
    return [function.to_dict() for function in functions]


def audit(
    repo_root: str | Path,
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Audita cobertura, módulos existentes e limites declarados."""

    root = Path(repo_root)
    functions = load_map(path)
    present = {function.function for function in functions}
    missing_functions = sorted(REQUIRED_FUNCTIONS - present)
    missing_modules = sorted(
        {
            function.module
            for function in functions
            if not (root / function.module).exists()
        }
    )
    missing_limits = [function.function for function in functions if not function.limit.strip()]

    status = "pass"
    if missing_functions or missing_modules or missing_limits:
        status = "warn"

    return {
        "status": status,
        "total": len(functions),
        "required_functions": sorted(REQUIRED_FUNCTIONS),
        "missing_functions": missing_functions,
        "missing_modules": missing_modules,
        "missing_limits": missing_limits,
        "functions": [function.function for function in functions],
    }
