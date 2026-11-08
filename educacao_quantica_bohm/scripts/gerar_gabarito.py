#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o gabarito comentado dos 100 checkpoints.

Cada conceito tem um checkpoint único (repetido nas 10 lentes e nos 3 níveis).
O gabarito traz: pergunta, resposta esperada, critério, onde conferir e o
resultado do experimento. Perguntas abertas recebem critério, não resposta única.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
sys.path.insert(0, str(LIVRO))

from base.base_conceitos import CONCEITOS  # noqa: E402
from base.base_experimentos import EXPERIMENTOS, MAPA  # noqa: E402
from gerar_secoes import LIMITE  # noqa: E402

DADOS = RAIZ / "dados_experimentos"


def carregar(exp_id: str) -> dict:
    p = DADOS / f"{exp_id}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def main() -> None:
    linhas = [
        "# Gabarito comentado: 100 checkpoints {#gabarito}",
        "",
        "<p class=\"parte-zh\">答案 · dá àn</p>",
        "",
        "Cada conceito tem **um checkpoint**, repetido nas 10 lentes e nos 3 níveis.",
        "Muitas perguntas são abertas: a resposta é um **critério de qualidade**, não",
        "uma frase única. Se a sua resposta não citar o conceito e um limite, volte",
        "à lauda indicada.",
        "",
        "> **Como usar:** tente responder sem consultar; depois leia a resposta",
        "> esperada e o critério. O objetivo não é acertar a frase do livro; é",
        "> conseguir explicar, aplicar e reconhecer o limite.",
        "",
    ]
    for idx, c in enumerate(CONCEITOS, 1):
        gid = f"G{idx:03d}"
        first = (idx - 1) * 10 + 1
        exp_id = MAPA[c["id"]]
        exp = EXPERIMENTOS[exp_id]
        d = carregar(exp_id)
        sim = (d.get("simulado") or {}).get("leitura", "—").replace(".", ",")
        real = (d.get("real") or {}).get("leitura", "—").replace(".", ",")
        ov = d.get("sobreposicao")
        ov_txt = f"{ov*100:.1f}%".replace(".", ",") if isinstance(ov, (int, float)) else "—"
        resposta = c["ideia"]
        criterio = c["limite"] or LIMITE[c["parte"]]
        alem = c["alem"] or "A lauda de laboratório mostra a aplicação."
        linhas += [
            f"## {gid} — {c['titulo']} {{#g-{idx:03d}}}",
            "",
            f"**Pergunta:** {c['checkpoint']}",
            "",
            f"**Resposta esperada:** {resposta}",
            "",
            f"**Critério:** a resposta deve citar o conceito e um limite. Limite do "
            f"conceito: {criterio}",
            "",
            f"**Onde conferir:** [ideia](#l-{first:04d}) · "
            f"[além](#l-{first+5:04d}) · [prática](#l-{first+2:04d}) · "
            f"[checkpoint](#l-{first+9:04d})",
            "",
            f"**Experimento {exp_id} — {exp['nome']}:** simulado {sim}; "
            f"backend {real}; sobreposição {ov_txt}.",
            "",
            f"**Complemento:** {alem}",
            "",
        ]
    linhas += [
        "> **Limite do gabarito:** ele não substitui a prática. Se você só ler a",
        "> resposta, não aprende; se fizer a prática e explicar o resultado, aprende.",
        "",
    ]
    (LIVRO / "GABARITO.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"Gabarito: {LIVRO / 'GABARITO.md'}")


if __name__ == "__main__":
    main()
