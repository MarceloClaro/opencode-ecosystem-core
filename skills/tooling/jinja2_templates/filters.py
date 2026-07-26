#!/usr/bin/env python3
"""
Filtros Customizados Jinja2 para Geração de Documentos
=========================================================
Filtros para transformar dados durante renderização de templates.

Uso nos templates:
    {{ texto | markdown }}
    {{ dados | table('nome', 'valor') }}
    {{ data | format_date }}
    {{ numero | round(2) }}
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import markdown as md_lib

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def filter_markdown(text: str) -> str:
    """Converte Markdown para HTML."""
    if HAS_MARKDOWN:
        return md_lib.markdown(text, extensions=["extra", "codehilite"])
    # Fallback simples
    html = text
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
    html = html.replace("*", "<em>", 1).replace("*", "</em>", 1)
    html = f"<p>{html}</p>"
    return html


def filter_table(
    data: List[Dict[str, Any]], *columns: str, header: bool = True
) -> str:
    """
    Cria tabela Markdown a partir de lista de dicionários.

    Args:
        data: lista de dicionários
        columns: nomes das colunas a incluir (se vazio, usa todas)
        header: se True, inclui linha de cabeçalho

    Returns:
        String com tabela Markdown
    """
    if not data:
        return "*(sem dados)*"

    # Determinar colunas
    if not columns:
        columns = tuple(data[0].keys())

    # Cabeçalho
    lines = []
    if header:
        lines.append("| " + " | ".join(str(c) for c in columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")

    # Linhas
    for row in data:
        vals = []
        for col in columns:
            v = row.get(col, "")
            # Formatação
            if isinstance(v, float):
                vals.append(f"{v:.2f}")
            elif isinstance(v, (int, bool)):
                vals.append(str(v))
            elif v is None:
                vals.append("")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")

    return "\n".join(lines)


def filter_format_date(
    value: Any, fmt: str = "%d/%m/%Y"
) -> str:
    """Formata data para string."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return str(value)


def filter_json(value: Any, indent: int = 2) -> str:
    """Converte valor para JSON formatado."""
    return json.dumps(value, ensure_ascii=False, indent=indent)


def filter_truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """Trunca texto no comprimento especificado."""
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


def filter_pluralize(
    count: int, singular: str = "", plural: str = "s"
) -> str:
    """Retorna sufixo singular/plural."""
    return singular if count == 1 else plural


def filter_pct(value: float, decimals: int = 1) -> str:
    """Formata como percentual."""
    return f"{value * 100:.{decimals}f}%"


def filter_abnt_author(author: str) -> str:
    """Formata nome de autor no padrão ABNT: SOBRENOME, Nome."""
    parts = author.strip().split()
    if len(parts) >= 2:
        return f"{parts[-1].upper()}, {' '.join(parts[:-1])}"
    return author.upper()


# Registro de todos os filtros
CUSTOM_FILTERS = {
    "markdown": filter_markdown,
    "table": filter_table,
    "format_date": filter_format_date,
    "json": filter_json,
    "truncate": filter_truncate,
    "pluralize": filter_pluralize,
    "pct": filter_pct,
    "abnt_author": filter_abnt_author,
}


# ─── Teste ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Filtros Customizados ===")

    # markdown
    print(f"\nmarkdown:")
    print(filter_markdown("# Título\n\n**negrito**"))

    # table
    print(f"\ntable:")
    dados = [{"nome": "João", "nota": 9.5}, {"nome": "Maria", "nota": 8.7}]
    print(filter_table(dados, "nome", "nota"))

    # format_date
    print(f"\nformat_date: {filter_format_date('2024-07-25')}")

    # pct
    print(f"pct: {filter_pct(0.856)}")

    # abnt_author
    print(f"abnt: {filter_abnt_author('João Silva')}")
