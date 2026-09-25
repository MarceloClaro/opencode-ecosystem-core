# -*- coding: utf-8 -*-
"""
Executor: minuta de ofício-resposta e planilha de controle
===========================================================
Gera, a partir do checklist da auditoria, os artefatos que a unidade
executora usará para responder à diligência:
  - minuta de ofício item-a-item (campos a preencher com providência + documento)
  - planilha CSV de controle

Os artefatos são MINUTAS: o preenchimento final (providência adotada,
documento comprobatório, assinaturas) é responsabilidade humana.
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any, Dict, List


_MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def _data_por_extenso() -> str:
    hoje = date.today()
    return f"{hoje.day} de {_MESES_PT[hoje.month - 1]} de {hoje.year}"


def _aplicar_sugestao(item: Dict[str, Any], sugestoes_by_id: Dict[str, Dict[str, Any]],
                      campo: str) -> str:
    """Retorna texto com sugestão marcada: '[SUGESTÃO – REVISAR] ...'"""
    if not sugestoes_by_id:
        return ""
    sugestao = sugestoes_by_id.get(item["id"])
    if not sugestao:
        return ""
    base = sugestao.get(campo, "")
    if not base:
        return ""
    return f"[SUGESTÃO – REVISAR] {base}"


def gerar_minuta(
    doc: Dict[str, Any],
    checklist: List[Dict[str, Any]],
    sugestoes: List[Dict[str, Any]] | None = None,
) -> str:
    """Monta minuta de ofício-resposta em markdown (formato administrativo).

    Inspirada no modelo editorial de resposta do plugin
    ``contas-escolares-airam-veras``: cabeçalho formal, tabela
    Item | Exigência | Resposta | Anexo | Pendência e rodapé de assinatura.
    É MINUTA — o preenchimento final é responsabilidade humana.

    Se ``sugestoes`` for fornecido, as células Resposta/Anexo recebem o texto
    proposto com o marcador ``[SUGESTÃO – REVISAR]`` (nunca como definitivo).
    """
    sugestoes_by_id = {s["id"]: s for s in (sugestoes or [])}
    cab = doc.get("cabecalho", {})
    unidade = cab.get("unidade_executora", "[UNIDADE EXECUTORA]")
    municipio = cab.get("municipio", "[MUNICÍPIO]")
    processo = cab.get("processo", "[PROCESSO]")
    ne = cab.get("ne", "[NE]")
    ano = cab.get("ano", "[ANO]")

    linhas: List[str] = [
        "**MINUTA PARA REVISÃO E ASSINATURA**",
        "",
        f"Ofício nº [PENDENTE: número]/{ano}",
        f"{municipio}, {_data_por_extenso()}.",
        "",
        f"Ao Exmo./À Célula de Gestão Administrativo-Financeira — 13ª CREDE",
        "Secretaria da Educação do Estado do Ceará (SEDUC/CE)",
        "",
        "**Assunto:** Resposta à diligência do processo "
        f"{processo} referente à prestação de contas do Prêmio Escola Nota Dez.",
        "",
        f"**Referência:** NE {ne}/{ano} — FECOP — {unidade}.",
        "",
        "Prezados(as),",
        "",
        "Em atenção à diligência, apresentamos os esclarecimentos e documentos "
        "relacionados no quadro a seguir, com indicação das providências "
        "concluídas e daquelas que ainda dependem de documentação:",
        "",
        "| Item | Exigência e origem | Resposta comprovada ou esclarecimento | "
        "Anexo efetivamente disponível | Pendência remanescente |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in checklist:
        exigencia = item["demanda"]
        if item["pagina"]:
            exigencia += f" (pag. {item['pagina']})"
        resposta = item.get("providencia") or _aplicar_sugestao(item, sugestoes_by_id, "providencia_sugerida") or "________________________"
        anexo = item.get("documento") or _aplicar_sugestao(item, sugestoes_by_id, "fundamento_sugerido") or "________________________"
        pendencia = "nenhuma no escopo examinado" if item["status"] == "atendido" else "a regularizar"
        linhas.append(
            f"| {item['id']} | {exigencia} | {resposta} | {anexo} | {pendencia} |"
        )

    linhas += [
        "",
        f"[Se pertinente: pedido objetivo de esclarecimento ou de prazo, sem "
        f"inventar deferimento, motivo ou prazo legal.]",
        "",
        "Atenciosamente,",
        "",
        "________________________________________",
        "[nome do responsável competente informado]",
        "[cargo/função comprovado para o ato]",
        f"{unidade} — {municipio}/CE",
        "",
        "## Índice de anexos",
        "",
        "> Relacionar somente arquivos efetivamente disponíveis (número, título, "
        "data/versão, páginas e itens atendidos). Lista separada de documentos em "
        "obtenção pode ser mantida no controle interno.",
        "",
        "> **Aviso anti-overclaim:** esta é uma MINUTA de trabalho. A aprovação da "
        "prestação de contas é decisão exclusiva da SEDUC/13ª CREDE, após análise "
        "da documentação original. O presente documento não substitui parecer do "
        "órgão concedente nem certifica regularidade.",
    ]
    return "\n".join(linhas)


def gerar_controle_csv(checklist: List[Dict[str, Any]], destino: Path) -> None:
    """Planilha de controle (UTF-8) com um item por linha (estados inclusos)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "id",
                "bloco",
                "demanda",
                "pagina",
                "estado_documental",
                "estado_tramitacao",
                "providencia",
                "documento",
                "status",
            ]
        )
        for item in checklist:
            writer.writerow(
                [
                    item["id"],
                    item["bloco"],
                    item["demanda"],
                    item["pagina"],
                    item.get("estado_documental", ""),
                    item.get("estado_tramitacao", ""),
                    item["providencia"],
                    item["documento"],
                    item["status"],
                ]
            )


def gerar_minuta_arquivo(
    doc: Dict[str, Any],
    checklist: List[Dict[str, Any]],
    destino: Path,
    sugestoes: List[Dict[str, Any]] | None = None,
) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_minuta(doc, checklist, sugestoes=sugestoes), encoding="utf-8")