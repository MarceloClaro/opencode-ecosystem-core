#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoria de repetições nas 3000 laudas."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SECOES = RAIZ / "educacao_quantica_bohm" / "livro_pixel" / "secoes"
SAIDA = RAIZ / "educacao_quantica_bohm" / "livro_pixel" / "RELATORIO_REPETICOES.md"


def limpar(html: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", html)
    texto = re.sub(r"&[a-zA-Z#0-9]+;", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def main() -> None:
    arquivos = sorted(SECOES.glob("[0-9][0-9][0-9][0-9]_*.md"))
    paragrafos = Counter()
    ngramas = Counter()
    por_lente = Counter()
    total_palavras = 0
    for p in arquivos:
        texto = p.read_text(encoding="utf-8")
        m = re.search(r"lente-([a-z]+)", texto)
        if m:
            por_lente[m.group(1)] += 1
        corpo = limpar(texto)
        total_palavras += len(corpo.split())
        for par in re.split(r"(?<=[.!?])\s+", corpo):
            par = par.strip()
            if len(par) >= 45:
                paragrafos[par] += 1
        palavras = re.findall(r"[a-záàâãéêíóôõúç]+", corpo.lower())
        for i in range(len(palavras) - 4):
            ngramas[" ".join(palavras[i:i + 5])] += 1

    top_par = paragrafos.most_common(30)
    top_ng = ngramas.most_common(30)
    repetidos = sum(v for k, v in paragrafos.items() if v > 1)
    linhas = [
        "# Relatório de repetições {#repeticoes}",
        "",
        "> Auditoria automática das 3000 laudas. Mede repetição textual, não",
        "> qualidade pedagógica. Repetição intencional de template não é erro;",
        "> repetição editorial sem função é candidata a corte na edição enxuta.",
        "",
        f"- Laudas analisadas: **{len(arquivos)}**",
        f"- Palavras (texto limpo): **{total_palavras:,}**".replace(",", "."),
        f"- Parágrafos repetidos (≥ 2 ocorrências): **{repetidos:,}**".replace(",", "."),
        f"- N-gramas distintos: **{len(ngramas):,}**".replace(",", "."),
        "",
        "## 1. Laudas por lente",
        "",
        "| Lente | Laudas |",
        "|---|---:|",
    ]
    for lente, n in sorted(por_lente.items(), key=lambda x: (-x[1], x[0])):
        linhas.append(f"| {lente} | {n} |")
    linhas += ["", "## 2. Parágrafos mais repetidos", "",
               "| Ocorrências | Parágrafo |", "|---:|---|"]
    for par, n in top_par:
        curto = par if len(par) <= 220 else par[:217] + "…"
        linhas.append(f"| {n} | {curto.replace('|', '&#124;')} |")
    linhas += ["", "## 3. N-gramas mais repetidos (5 palavras)", "",
               "| Ocorrências | N-grama |", "|---:|---|"]
    for ng, n in top_ng:
        linhas.append(f"| {n} | {ng} |")
    linhas += [
        "",
        "## 4. Leitura",
        "",
        "- A repetição de **template** (topo, ponte, resultado, rodapé) é",
        "  estrutural: ela ajuda a navegar. Não deve ser cortada sem substituição.",
        "- A repetição de **frases de transição** e **micropráticas** é a principal",
        "  candidata a compressão na edição enxuta.",
        "- A repetição de **nomes de experimentos** é necessária para rastrear",
        "  E01–E18; não é redundância.",
        "- A edição enxuta deve manter **uma** ocorrência de cada template por",
        "  módulo e usar remissões para o restante.",
        "",
        "## 5. Ações recomendadas",
        "",
        "1. Substituir micropráticas repetidas por uma lista de 10 micropráticas",
        "   por módulo.",
        "2. Usar `ver seção X` em vez de repetir a explicação de uma lente.",
        "3. Manter a Ponte Sonora apenas uma vez por módulo na edição enxuta.",
        "4. Manter as notas de cálculo específicas; remover as genéricas.",
        "5. Revisar os 30 parágrafos acima com um editor humano.",
        "",
        "> **Limite:** esta auditoria é lexical. Ela não decide o que é pedagogicamente",
        "> necessário. A decisão de corte é humana e deve preservar a sequência",
        "> didática.",
        "",
    ]
    SAIDA.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Relatório: {SAIDA}")
    print(f"Laudas: {len(arquivos)} | palavras: {total_palavras} | repetidos: {repetidos}")


if __name__ == "__main__":
    main()
