# -*- coding: utf-8 -*-
"""
Relatório de conferência da prestação de contas
================================================
Gera um relatório em Markdown com identificação/escopo, síntese, cobertura e
limitações, achados (itens pendentes) e consolidação de estados — seguindo a
estrutura editorial do plugin ``contas-escolares-airam-veras``.

ANTI-OVERCLAIM: o relatório relata quantos itens foram conferidos/pendentes com
denominador definido; **não** transforma percentual de cobertura em
probabilidade de aprovação nem declara aceite pelo órgão concedente.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from .auditor import consolidar_estados


def gerar_relatorio(
    doc: Dict[str, Any],
    checklist: List[Dict[str, Any]],
    score: Dict[str, Any],
    fonte: str = "",
) -> str:
    cab = doc.get("cabecalho", {})
    unidade = cab.get("unidade_executora", "[UNIDADE EXECUTORA]")
    municipio = cab.get("municipio", "[MUNICÍPIO]")
    processo = cab.get("processo", "[PROCESSO]")
    ne = cab.get("ne", "[NE]")
    ano = cab.get("ano", "[ANO]")

    estados = consolidar_estados(checklist)
    if not estados["documental"] and not estados["tramitacao"]:
        # JSONs gerados antes dos campos de estado (retrocompatibilidade)
        estados = {"documental": {"não examinado (legado)": len(checklist)},
                   "tramitacao": {"identificado (legado)": len(checklist)}}
    conclusao_doc = estados["documental"].get("conferido", 0)
    conclusao_tram = estados["tramitacao"].get("aceite comprovado pelo órgão", 0)

    linhas: List[str] = [
        "# Relatório de conferência — Prestação de Contas (Prêmio Escola Nota Dez)",
        "",
        f"**Unidade Executora:** {unidade}",
        f"**Município/CE:** {municipio}",
        f"**Processo:** {processo}",
        f"**Referência:** NE {ne}/{ano}",
        f"**Data do relatório:** {date.today().isoformat()}",
        f"**Fonte analisada:** {fonte or doc.get('fonte', '—')}",
        "",
        "## 1. Identificação e escopo",
        "",
        "O presente relatório é produto de **apoio computacional** à organização da "
        "resposta à diligência. A verificação documental foi feita por OCR do PDF "
        "escaneado; **documentos citados na diligência não foram automaticamente "
        "examinados** — trata-se de extração parcial de exigências.",
        "",
        "## 2. Síntese do que foi conferido",
        "",
        f"- Total de itens extraídos da diligência: **{score['total']}**.",
        f"- Itens com providência e documento preenchidos (cobertura interna): "
        f"**{score['atendidos']}**.",
        f"- Itens pendentes de providência: **{score['pendentes']}**.",
        "",
        "## 3. Cobertura e limitações",
        "",
        f"- Cobertura interna: **{score['cobertura']:.1%}** — medida de organização "
        "da resposta, **não** é probabilidade de aprovação nem aceite do órgão.",
        f"- Estado documental consolidado: **{dict(estados['documental'])}**.",
        f"- Estados de tramitação consolidados: **{dict(estados['tramitacao'])}**.",
        f"- Itens com documental 'conferido': {conclusao_doc}; itens com aceite "
        f"comprovado pelo órgão: {conclusao_tram}.",
        "- Limitação: OCR pode conter erros; valores/números/datas devem ser "
        "confirmados visualmente no PDF original.",
        "",
        "## 4. Achados e providências",
        "",
        "| ID | Bloco | Exigência (resumo) | Pag. | Estado |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in checklist:
        exig = item["demanda"] if len(item["demanda"]) <= 80 else item["demanda"][:77] + "..."
        estado = item.get("estado_tramitacao") or item.get("status") or "identificado"
        linhas.append(
            f"| {item['id']} | {item['bloco'][:30]} | {exig} | {item['pagina']} | "
            f"{estado} |"
        )

    linhas += [
        "",
        "## 5. Providências sugeridas",
        "",
        "1. Preencher cada item do checklist com a providência adotada e o "
        "documento comprobatório, conferindo a evidência original.",
        "2. Confirmar a norma aplicável (manual do exercício, legislação) antes "
        "de qualquer conclusão jurídica ou fiscal.",
        "3. Revisar a minuta, substituir campos [PENDENTE] e obter assinatura da "
        "pessoa competente.",
        "",
        "> **Anti-overclaim:** este relatório não declara aprovação pelo órgão "
        "concedente, não certifica regularidade e não substitui parecer da "
        "SEDUC/13ª CREDE. O aceite depende do órgão competente após análise dos "
        "documentos originais.",
    ]
    return "\n".join(linhas)


def gerar_relatorio_arquivo(
    doc: Dict[str, Any], checklist: List[Dict[str, Any]], score: Dict[str, Any], destino: Any
) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_relatorio(doc, checklist, score), encoding="utf-8")