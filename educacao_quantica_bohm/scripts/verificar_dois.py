#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica os DOIs da base de referências via Crossref/DataCite.

Não inventa DOI: registra status, título e fonte. Se um DOI falhar, o relatório
mostra o fallback (URL) para revisão humana.
"""
from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LIVRO = RAIZ / "livro_pixel"
sys.path.insert(0, str(LIVRO))

from base.base_referencias import REFERENCIAS  # noqa: E402

SAIDA = RAIZ / "dados_referencias"
SAIDA.mkdir(parents=True, exist_ok=True)


def limpar_titulo(texto: str) -> str:
    """Remove HTML da resposta do Crossref e compacta o espaçamento."""
    texto = re.sub(r"<[^>]+>", "", str(texto))
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def consultar(url: str):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def verificar(doi: str):
    for fonte, base in (
        ("Crossref", "https://api.crossref.org/works/"),
        ("DataCite", "https://api.datacite.org/dois/"),
    ):
        try:
            d = consultar(base + urllib.parse.quote(doi))
        except Exception:
            continue
        if fonte == "Crossref":
            msg = d.get("message", {})
            titulo = msg.get("title", [""])
            titulo = titulo[0] if isinstance(titulo, list) and titulo else str(titulo)
            return {"status": "ok", "fonte": fonte, "titulo": limpar_titulo(titulo)[:160]}
        attrs = d.get("data", {}).get("attributes", {})
        titulos = attrs.get("titles", [{}])
        titulo = titulos[0].get("title", "") if titulos else ""
        return {"status": "ok", "fonte": fonte, "titulo": limpar_titulo(titulo)[:160]}
    return {"status": "falhou", "fonte": "", "titulo": ""}


def main() -> None:
    resultados = {}
    for nome, r in REFERENCIAS.items():
        doi = r.get("doi", "")
        if not doi:
            resultados[nome] = {
                "status": "sem_doi",
                "fonte": "",
                "titulo": limpar_titulo(r["titulo"]),
                "url": r.get("url", ""),
            }
            print(f"{nome:14s} sem DOI  {r['url']}")
            continue
        info = verificar(doi)
        info["doi"] = doi
        info["url"] = f"https://doi.org/{doi}"
        resultados[nome] = info
        print(f"{nome:14s} {info['status']:7s} {info['fonte']:9s} {info['titulo'][:70]}")

    dados = {
        "data_verificacao": "2026-11-07",
        "total": len(resultados),
        "ok": sum(1 for v in resultados.values() if v["status"] == "ok"),
        "sem_doi": sum(1 for v in resultados.values() if v["status"] == "sem_doi"),
        "falhas": sum(1 for v in resultados.values() if v["status"] == "falhou"),
        "referencias": resultados,
    }
    (SAIDA / "dois_verificados.json").write_text(
        json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    linhas = [
        "# Verificação de DOIs {#verificacao-dois}",
        "",
        f"Data: 2026-11-07. Total: {dados['total']}; OK: {dados['ok']}; "
        f"sem DOI: {dados['sem_doi']}; falhas: {dados['falhas']}.",
        "",
        "| Referência | DOI | Status | Título verificado |",
        "|---|---|---|---|",
    ]
    for nome, info in resultados.items():
        doi = info.get("doi", "—")
        titulo = limpar_titulo(info.get("titulo", "")).replace("|", "&#124;")
        linhas.append(f"| {nome} | {doi} | {info['status']} | {titulo} |")
    linhas += [
        "",
        "> **Limite:** a verificação confirma que o DOI resolve em Crossref/DataCite",
        "> na data acima. Não garante acesso ao texto completo nem revisão por pares.",
        "",
    ]
    (SAIDA / "RELATORIO_DOIS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Relatório: {SAIDA / 'RELATORIO_DOIS.md'}")


if __name__ == "__main__":
    main()