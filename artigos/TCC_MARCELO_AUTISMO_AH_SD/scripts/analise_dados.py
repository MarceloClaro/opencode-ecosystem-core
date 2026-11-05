#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Série oficial do Censo Escolar (INEP) e cenários exploratórios.

Fontes:
- INEP. Sinopse Estatística da Educação Básica 2021, 2022, 2023 e 2024.
  Tabelas 1.43/1.49 (2021-2022) e 1.44/1.50 (2023-2024): matrículas da
  educação especial em classes comuns e exclusivas, por tipo de deficiência.
- INEP. Tabela 1.3: total de matrículas da educação básica.

Observação: as categorias do Censo não são mutuamente exclusivas; os totais
de TEA e AH/SD podem se sobrepor. Os números são de matrículas, não de
pessoas únicas.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
DADOS.mkdir(exist_ok=True)

# Matrículas em classes comuns e exclusivas, por categoria.
SERIE = [
    # ano, tea_comum, tea_exclusiva, ah_comum, ah_exclusiva, total_basica
    (2021, 273924, 20470, 23506, 252, 46668401),
    (2022, 405056, 24465, 26589, 226, 47382074),
    (2023, 607144, 29058, 37638, 381, 47304632),
    (2024, 884403, 34474, 43950, 221, 47088922),
]

REGIOES_2024 = [
    # regiao, tea, ah_sd, total_educacao_especial
    ("Norte", 89150, 3671, 198915),
    ("Nordeste", 282410, 6253, 649724),
    ("Sudeste", 340751, 11584, 701764),
    ("Sul", 144536, 17985, 361307),
    ("Centro-Oeste", 62030, 4678, 165115),
]


def ler_serie() -> list[dict]:
    saida = []
    for ano, tc, te, ac, ae, total in SERIE:
        tea = tc + te
        ah = ac + ae
        saida.append({
            "ano": ano,
            "tea_classes_comuns": tc,
            "tea_classes_exclusivas": te,
            "tea_total": tea,
            "ahsd_classes_comuns": ac,
            "ahsd_classes_exclusivas": ae,
            "ahsd_total": ah,
            "total_educacao_basica": total,
            "percentual_tea": 100 * tea / total,
            "percentual_ahsd": 100 * ah / total,
            "razao_tea_ahsd": tea / ah,
        })
    return saida


def ajuste_linear(anos: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    b, a = np.polyfit(anos, y, 1)
    yhat = a + b * anos
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return float(a), float(b), 1 - ss_res / ss_tot


def main() -> int:
    serie = ler_serie()

    with (DADOS / "serie_nacional.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(serie[0].keys()))
        w.writeheader()
        w.writerows(serie)

    with (DADOS / "regioes_2024.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["regiao", "tea", "ahsd", "razao_tea_ahsd", "total_educacao_especial"])
        for regiao, tea, ah, total in REGIOES_2024:
            w.writerow([regiao, tea, ah, round(tea / ah, 1), total])

    anos = np.array([r["ano"] for r in serie], dtype=float)
    tea = np.array([r["tea_total"] for r in serie], dtype=float)
    ah = np.array([r["ahsd_total"] for r in serie], dtype=float)
    a_tea, b_tea, r2_tea = ajuste_linear(anos, tea)
    a_ah, b_ah, r2_ah = ajuste_linear(anos, ah)

    # Cenários 2025-2027.
    cenarios = []
    ultimo_tea = float(tea[-1])
    ultimo_ah = float(ah[-1])
    for ano in (2025, 2026, 2027):
        linear_tea = a_tea + b_tea * ano
        linear_ah = a_ah + b_ah * ano
        mod_tea = ultimo_tea * (1.20 ** (ano - 2024))
        mod_ah = ultimo_ah * (1.15 ** (ano - 2024))
        conv_tea = ultimo_tea * (1.10 ** (ano - 2024))
        conv_ah = ultimo_ah * (1.25 ** (ano - 2024))
        cenarios.append({
            "ano": ano,
            "linear_tea": round(linear_tea),
            "linear_ahsd": round(linear_ah),
            "linear_razao": round(linear_tea / linear_ah, 1),
            "moderado_tea": round(mod_tea),
            "moderado_ahsd": round(mod_ah),
            "moderado_razao": round(mod_tea / mod_ah, 1),
            "convergencia_tea": round(conv_tea),
            "convergencia_ahsd": round(conv_ah),
            "convergencia_razao": round(conv_tea / conv_ah, 1),
        })

    with (DADOS / "cenarios.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cenarios[0].keys()))
        w.writeheader()
        w.writerows(cenarios)

    resumo = {
        "serie": serie,
        "regioes_2024": [
            {"regiao": r, "tea": t, "ahsd": a, "razao": round(t / a, 1), "total": tot}
            for r, t, a, tot in REGIOES_2024
        ],
        "ajuste_linear": {
            "tea": {"intercepto": a_tea, "inclinacao_ano": b_tea, "r2": r2_tea},
            "ahsd": {"intercepto": a_ah, "inclinacao_ano": b_ah, "r2": r2_ah},
        },
        "cenarios": cenarios,
        "aviso": "Cenários exploratórios; não são previsões. As categorias do Censo podem se sobrepor.",
    }
    (DADOS / "resumo_analise.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Série nacional")
    for r in serie:
        print(f"  {r['ano']}: TEA={r['tea_total']:,} | AH/SD={r['ahsd_total']:,} | "
              f"TEA%={r['percentual_tea']:.3f} | AH/SD%={r['percentual_ahsd']:.3f} | "
              f"razão={r['razao_tea_ahsd']:.1f}")
    print("\nRegiões 2024")
    for regiao, t, a, tot in REGIOES_2024:
        print(f"  {regiao:14s}: TEA={t:,} | AH/SD={a:,} | razão={t/a:.1f}")
    print("\nAjuste linear")
    print(f"  TEA: inclinação={b_tea:,.0f}/ano; R²={r2_tea:.4f}")
    print(f"  AH/SD: inclinação={b_ah:,.0f}/ano; R²={r2_ah:.4f}")
    print("\nCenários")
    for c in cenarios:
        print(f"  {c['ano']}: linear TEA={c['linear_tea']:,} AH={c['linear_ahsd']:,} "
              f"razão={c['linear_razao']} | moderado TEA={c['moderado_tea']:,} "
              f"AH={c['moderado_ahsd']:,} razão={c['moderado_razao']} | "
              f"convergência TEA={c['convergencia_tea']:,} AH={c['convergencia_ahsd']:,} "
              f"razão={c['convergencia_razao']}")
    print(f"\nOK: {DADOS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
