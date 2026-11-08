#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera 100 fichas de evidência e prática (F001–F100), uma por conceito.

Cada ficha reúne:
- a ideia em uma frase;
- a fonte primária com DOI/URL e status de verificação;
- o que foi medido e o que não prova;
- a prática com o resultado simulado × backend;
- o grau de evidência (A/B/C/D) e a ficha de citação.

As fichas são um apêndice: não alteram as 3000 laudas L0001–L3000.
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
from base.base_referencias import (  # noqa: E402
    GRAU_PARTE, REFERENCIAS, abnt, link, refs_conceito,
)
from gerar_secoes import esc, resultado_html  # noqa: E402

SAIDA = LIVRO / "fichas"
SAIDA.mkdir(parents=True, exist_ok=True)
STATUS = RAIZ / "dados_referencias" / "dois_verificados.json"


def status_doi(nome: str) -> str:
    if not STATUS.exists():
        return "DOI/URL não verificado nesta edição"
    d = json.loads(STATUS.read_text(encoding="utf-8"))["referencias"].get(nome, {})
    if d.get("status") == "ok":
        return f"DOI verificado via {d.get('fonte', 'Crossref')} em 2026-11-07"
    if d.get("status") == "sem_doi":
        return "URL oficial; sem DOI estável"
    return "DOI não verificado nesta edição"


def ficha(c: dict, numero: int) -> str:
    nomes = refs_conceito(c)
    prim = nomes[0]
    sec = nomes[1] if len(nomes) > 1 else None
    r = REFERENCIAS[prim]
    exp_id = MAPA[c["id"]]
    exp = EXPERIMENTOS[exp_id]
    idx = [x['id'] for x in CONCEITOS if x['parte'] == c['parte']].index(c['id'])
    inicio = (c['parte'] - 1) * 1000 + idx * 10 + 1
    fim = inicio + 9
    grau, justificativa = GRAU_PARTE[c["parte"]]
    if c["id"] in ("vqc_xor", "ruido_benefico"):
        grau = "C"
        justificativa = "VQC com amostra pequena e um único desenho; resultado exploratório."
    if c["id"] == "ghz_real":
        grau = "B"
        justificativa = "Execução em backend com 1024 tiros; não é prova de hardware nem de emaranhamento."

    fonte = abnt(prim)
    fonte += f' <span class="mini">({status_doi(prim)})</span>' 

    leitura = ""
    if sec:
        leitura = f'<p class="mini"><strong>Leitura complementar:</strong> {abnt(sec)}</p>'

    return f"""::: {{.lauda .ficha}}
<div class="topo">
  <span class="cod">F{numero:03d}</span>
  <span class="lente">FICHA DE EVIDÊNCIA</span>
  <span class="conc">C{(c['parte']-1)*10 + idx + 1:03d} · {esc(c['titulo']).upper()}</span>
</div>
<h2 id="f-{numero:03d}" class="titulo">{esc(c['titulo'])} — o que a evidência mostra</h2>
<div class="corpo">
<p><strong>Em uma frase:</strong> {esc(c['ideia'])}</p>
<p><strong>Fonte primária:</strong> {fonte}</p>
<p><strong>O que foi medido:</strong> {esc(c['alem'] or 'A fonte discute o conceito e suas consequências.')}</p>
<p><strong>O que não prova:</strong> {esc(c['limite'] or 'Não há garantia de generalização para outros contextos.')}</p>
<p><strong>Prática:</strong> {esc(c['pratica'])}</p>
{resultado_html(c)}
<div class="grau"><strong>Grau de evidência: {grau}</strong> — {esc(justificativa)}</div>
<p class="mini"><strong>Para citar:</strong> {abnt(prim)}</p>
{leitura}
</div>
<div class="rodape">F{numero:03d}/100 · {exp_id} · L{inicio:04d}–L{fim:04d}</div>
:::
"""


def indice() -> None:
    linhas = [
        "# Fichas de evidência e prática {#fichas}",
        "",
        "Cada ficha liga um conceito a uma fonte primária, ao que foi medido, ao que",
        "não prova, a uma prática e ao grau de evidência. As fichas são um apêndice:",
        "as 3000 laudas L0001–L3000 continuam sendo o corpo principal.",
        "",
        "::: {.tabela-longa}",
        "",
        "| Ficha | Conceito | Fonte primária | DOI | Grau |",
        "|---|---|---|---|---|",
    ]
    for i, c in enumerate(CONCEITOS, 1):
        prim = refs_conceito(c)[0]
        r = REFERENCIAS[prim]
        doi = r.get("doi", "—")
        grau = GRAU_PARTE[c["parte"]][0]
        if c["id"] in ("vqc_xor", "ruido_benefico"):
            grau = "C"
        if c["id"] == "ghz_real":
            grau = "B"
        linhas.append(
            f"| [F{i:03d}](#f-{i:03d}) | {c['titulo']} | {r['autores']} ({r['ano']}) | {doi} | {grau} |"
        )
    linhas += [
        "",
        ":::",
        "",
        "> **Limite:** o grau A/B/C/D é uma síntese editorial inspirada em GRADE;",
        "> não substitui uma revisão sistemática. Um DOI ativo não é sinônimo de",
        "> resultado verdadeiro: ele apenas identifica a fonte.",
        "",
    ]
    (LIVRO / "FICHAS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> None:
    for p in SAIDA.glob("F*.md"):
        p.unlink()
    for i, c in enumerate(CONCEITOS, 1):
        (SAIDA / f"F{i:03d}_{c['id']}.md").write_text(ficha(c, i), encoding="utf-8")
    indice()
    print(f"Fichas: {len(list(SAIDA.glob('F*.md')))}")
    print(f"Índice: {LIVRO / 'FICHAS.md'}")


if __name__ == "__main__":
    main()