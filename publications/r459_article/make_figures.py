# -*- coding: utf-8 -*-
"""Regenera a figura de resultados do artigo R459 com 4 estratÃ©gias
(top-k, MMR, RecamÃ¡n, HABD) usando os valores REAIS de cohort_report.json.

Uso:
    python3 publications/r459_article/make_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parent.parent / "benchmarks" / "cohort_report.json"
OUT = ROOT / "figures" / "cohort_results.png"


def main() -> None:
    data = json.load(open(REPORT))
    ps = data["per_strategy"]

    strategies = ["top-k", "MMR", "Recam\u00e1n", "HABD"]
    order = ["atual", "mmr", "recaman", "habd"]
    diversity = [ps[k]["diversity"] for k in order]
    grounded = [ps[k]["groundedness"] for k in order]
    coverage = [ps[k]["coverage"] for k in order]

    x = np.arange(len(strategies))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x - width, diversity, width, label="Diversidade Div(S)", color="#2c7fb8")
    b2 = ax.bar(x, grounded, width, label="Groundedness (relev\u00e2ncia)", color="#31a354")
    b3 = ax.bar(x + width, coverage, width, label="Cobertura de \u00e2ngulos", color="#de2d26")

    ax.set_ylabel("M\u00e9dia sobre 4 queries")
    ax.set_title("Coorte R458/R460 \u2014 diversifica\u00e7\u00e3o p\u00f3s-ranqueamento no RAG (corpus-piloto)")
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.set_ylim(0, 1.08)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # r\u00f3tulos de valor
    for bars in (b1, b2, b3):
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02,
                f"{bar.get_height():.3f}",
                ha="center", va="bottom", fontsize=7,
            )

    ax.text(
        0.01, 0.02,
        "Valores reais de benchmarks/cohort_report.json. Veredito H3: refuta (queda "
        "de groundedness do HABD > 5%). Escopo: corpus-piloto; n\u00e3o generaliza.",
        transform=ax.transAxes, fontsize=7, color="#555555",
    )

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200)
    print(f"Figura salva: {OUT}")


if __name__ == "__main__":
    main()
