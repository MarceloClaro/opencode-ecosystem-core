#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrai os indicadores de TEA do Censo Escolar 2024 e monta as séries.

Fonte: INEP. Sinopse Estatística da Educação Básica 2024.
  - Tabela 1.3  — matrículas da educação básica por região/UF;
  - Tabela 1.44 — educação especial em classes comuns por tipo de deficiência;
  - Tabela 1.50 — educação especial em classes exclusivas por tipo de deficiência.

A série nacional 2021–2024 usa os totais publicados nas Sinopses de cada ano
(mesmos valores do TCC do Marcelo, extraídos das planilhas oficiais).

Uso:
    python3 scripts/extrair_dados_inep.py [caminho_do_xlsx]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parent.parent
DADOS = BASE / "dados"
DADOS.mkdir(exist_ok=True)

XLSX = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/tmp/inep/sinopse_estatistica_censo_escolar_2024/"
    "Sinopse_Estatistica_da_Educação_Basica_2024.xlsx"
)

# Série nacional oficial (Sinopses 2021–2024). O total de educação básica é o
# denominador publicado na Tabela 1.3 de cada ano.
REGIOES = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
UFS = [
    "Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins",
    "Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
    "Pernambuco", "Alagoas", "Sergipe", "Bahia", "Minas Gerais",
    "Espírito Santo", "Rio de Janeiro", "São Paulo", "Paraná",
    "Santa Catarina", "Rio Grande do Sul", "Mato Grosso do Sul",
    "Mato Grosso", "Goiás", "Distrito Federal",
]

SERIE = [
    (2021, 294394, 46668401),
    (2022, 429521, 47382074),
    (2023, 636202, 47304632),
    (2024, 918877, 47088922),
]


def linhas(ws, max_col=16):
    for row in ws.iter_rows(min_row=10, max_row=ws.max_row,
                            max_col=max_col, values_only=True):
        yield row


def extrair_2024():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    base = {}
    for row in linhas(wb["1.3"], max_col=5):
        reg = str(row[0]).strip() if row[0] else ""
        uf = str(row[1]).strip() if row[1] else ""
        mun = str(row[2]).strip() if row[2] else ""
        total = int(row[4] or 0)
        if mun:
            continue
        if uf:
            base.setdefault(uf, {})["basica"] = total
        elif reg:
            base.setdefault(reg, {})["basica"] = total

    for sheet, chave in (("1.44", "comum"), ("1.50", "exclusiva")):
        for row in linhas(wb[sheet], max_col=15):
            reg = str(row[0]).strip() if row[0] else ""
            uf = str(row[1]).strip() if row[1] else ""
            mun = str(row[2]).strip() if row[2] else ""
            if mun:
                continue
            total = int(row[4] or 0)
            tea = int(row[13] or 0)
            if uf:
                d = base.setdefault(uf, {})
            elif reg:
                d = base.setdefault(reg, {})
            else:
                continue
            d[chave] = d.get(chave, 0) + total
            d["tea"] = d.get("tea", 0) + tea
    return base


def escrever(nome, campos, registros):
    with (DADOS / nome).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        for r in registros:
            w.writerow({k: (round(v, 3) if isinstance(v, float) else v)
                        for k, v in r.items()})


def main() -> int:
    base = extrair_2024()

    # Série nacional
    serie = []
    anterior = None
    for ano, tea, total in SERIE:
        crescimento = None if anterior is None else (tea / anterior - 1) * 100
        serie.append({
            "ano": ano,
            "tea": tea,
            "total_educacao_basica": total,
            "percentual_tea": tea / total * 100,
            "tea_por_mil": tea / total * 1000,
            "crescimento_anual_pct": crescimento,
        })
        anterior = tea
    escrever("serie_nacional_tea.csv", list(serie[0]), serie)

    # Regiões
    reg = []
    for nome in REGIOES:
        d = base[nome]
        esp = d.get("comum", 0) + d.get("exclusiva", 0)
        reg.append({
            "regiao": nome,
            "tea": d["tea"],
            "total_educacao_basica": d["basica"],
            "total_educacao_especial": esp,
            "tea_por_mil": d["tea"] / d["basica"] * 1000,
            "participacao_na_especial_pct": d["tea"] / esp * 100,
        })
    escrever("regioes_2024_tea.csv", list(reg[0]), reg)

    # Unidades da federação
    ufs = [u for u in UFS if u in base]
    est = []
    for uf in ufs:
        d = base[uf]
        esp = d.get("comum", 0) + d.get("exclusiva", 0)
        est.append({
            "uf": uf,
            "tea": d["tea"],
            "total_educacao_basica": d["basica"],
            "total_educacao_especial": esp,
            "tea_por_mil": d["tea"] / d["basica"] * 1000,
            "participacao_na_especial_pct": d["tea"] / esp * 100,
        })
    est.sort(key=lambda r: r["tea_por_mil"], reverse=True)
    escrever("estados_2024_tea.csv", list(est[0]), est)

    # Cenários exploratórios 2025–2027
    tea24 = SERIE[-1][1]
    total = SERIE[-1][2]
    inclinacao = (SERIE[-1][1] - SERIE[0][1]) / (SERIE[-1][0] - SERIE[0][0])
    cenarios = []
    for nome, fator in (("linear", None), ("moderado", 0.15), ("acelerado", 0.25)):
        valor = tea24
        for ano in (2024, 2025, 2026, 2027):
            if ano > 2024:
                valor = valor + inclinacao if fator is None else valor * (1 + fator)
                cenarios.append({
                    "cenario": nome,
                    "ano": ano,
                    "tea_projetado": round(valor),
                    "percentual_educacao_basica": valor / total * 100,
                })
    escrever("cenarios_2025_2027.csv", list(cenarios[0]), cenarios)

    print(f"OK: {len(serie)} anos, {len(reg)} regiões, {len(est)} UFs, {len(cenarios)} cenários")
    print(f"Brasil 2024: TEA={base['Brasil']['tea']:,} | "
          f"taxa={base['Brasil']['tea']/base['Brasil']['basica']*1000:.2f}/mil")
    print("Maiores taxas:")
    for r in est[:5]:
        print(f"  {r['uf']:20s} {r['tea_por_mil']:5.2f}/mil  {r['participacao_na_especial_pct']:5.1f}% da especial")
    print("Menores taxas:")
    for r in est[-5:]:
        print(f"  {r['uf']:20s} {r['tea_por_mil']:5.2f}/mil  {r['participacao_na_especial_pct']:5.1f}% da especial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
