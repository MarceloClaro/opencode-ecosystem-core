# -*- coding: utf-8 -*-
"""Classificador de aplicabilidade da camada JavaScript do REA.

Mitigação da limitação observada em R1112: um alvo Python/Markdown submetido
a ``analyze_javascript_application`` retorna ``0 findings``, o que pode ser
lido erroneamente como "não há nada". Este módulo separa **ausência de
superfície** de **análise concluída**.

Uso:
    python3 -m integrations.rea_applicability /caminho/do/alvo

Códigos de saída: 0 = camada JS aplicável; 3 = não aplicável; 4 = indefinido.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence

JAVASCRIPT_SUFFIXES = {".js", ".mjs", ".cjs", ".jsx"}
TYPESCRIPT_SUFFIXES = {".ts", ".tsx"}
HTML_SUFFIXES = {".html", ".htm"}
PYTHON_SUFFIXES = {".py"}
MARKDOWN_SUFFIXES = {".md", ".markdown"}

SKIPPED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    "coverage",
    ".cache",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
}


def _bump(counts: dict[str, int], suffix: str) -> None:
    if suffix in JAVASCRIPT_SUFFIXES:
        counts["javascript"] += 1
    elif suffix in TYPESCRIPT_SUFFIXES:
        counts["typescript"] += 1
    elif suffix == ".asar":
        counts["asar"] += 1
    elif suffix in HTML_SUFFIXES:
        counts["html"] += 1
    elif suffix in PYTHON_SUFFIXES:
        counts["python"] += 1
    elif suffix in MARKDOWN_SUFFIXES:
        counts["markdown"] += 1


def classify_surface(path: Path, *, max_files: int = 50_000) -> dict[str, Any]:
    """Classifica a superfície de um arquivo ou diretório sem executá-lo."""
    target = Path(path).expanduser()
    if not target.exists():
        raise FileNotFoundError(f"caminho não encontrado: {target}")

    counts = {
        "javascript": 0,
        "typescript": 0,
        "asar": 0,
        "html": 0,
        "python": 0,
        "markdown": 0,
    }
    total = 0

    if target.is_file():
        _bump(counts, target.suffix.lower())
        total = 1
    else:
        for root, directories, files in os.walk(target):
            directories[:] = [
                name for name in directories if name not in SKIPPED_DIRECTORIES
            ]
            for name in files:
                if total >= max_files:
                    break
                _bump(counts, Path(name).suffix.lower())
                total += 1
            if total >= max_files:
                break

    javascript_surface = (
        counts["javascript"] + counts["typescript"] + counts["asar"]
    )
    if javascript_surface > 0:
        layer = "javascript"
        reason = (
            f"{javascript_surface} artefato(s) JavaScript/TypeScript/ASAR "
            "encontrados; a camada JS do REA é aplicável"
        )
    elif counts["python"] > 0:
        layer = "not_applicable"
        reason = (
            f"{counts['python']} arquivo(s) Python e nenhum artefato JS/TS/ASAR; "
            "a camada JS do REA não tem superfície (0 findings não significa "
            "'nada a analisar')"
        )
    elif counts["markdown"] > 0:
        layer = "not_applicable"
        reason = (
            "alvo somente de documentação (Markdown), sem artefato JS/TS/ASAR; "
            "a camada JS do REA não tem superfície"
        )
    else:
        layer = "unknown"
        reason = "nenhum arquivo reconhecido; classificação indefinida"

    return {
        "schema": "rea.applicability.v1",
        "path": str(target.resolve()),
        "counts": counts,
        "total_files": total,
        "recommended_layer": layer,
        "reason": reason,
        "confidence": "derived",
        "limits": [
            "Classificação por extensão; não prova conteúdo, execução ou ausência de código gerado.",
            "Diretórios de dependência e build são ignorados por padrão.",
            f"Limite de varredura: {max_files} arquivos.",
        ],
    }


def should_run_javascript_analysis(path: Path) -> bool:
    """Atalho booleano para pré-condicionar ``analyze_javascript_application``."""
    return classify_surface(path)["recommended_layer"] == "javascript"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Classifica a aplicabilidade da camada JS do REA"
    )
    parser.add_argument("path", help="arquivo ou diretório do alvo")
    args = parser.parse_args(argv)

    try:
        result = classify_surface(Path(args.path))
    except FileNotFoundError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return {
        "javascript": 0,
        "not_applicable": 3,
        "unknown": 4,
    }[result["recommended_layer"]]


if __name__ == "__main__":
    sys.exit(main())
