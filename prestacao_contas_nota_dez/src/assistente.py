# -*- coding: utf-8 -*-
"""
Assistente de preenchimento da minuta (SUGESTÕES para revisão humana)
=======================================================================
Classifica cada item do checklist por tema, localiza trechos do Manual de
Orientações 2019 (OCR auxiliar) e propõe providência + fundamento.

TUDO AQUI É SUGESTÃO: nenhum campo é preenchido como definitivo. As células
geradas vêm com o marcador ``[SUGESTÃO – REVISAR]`` e o texto proposto deve ser
conferido contra a imagem do PDF (o OCR manual-2019-ocr.md é auxiliar: "a
imagem prevalece sobre o OCR") e contra a norma aplicável ao exercício.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

_MANUAL = Path(__file__).resolve().parent.parent / "references" / "manual-2019-ocr.md"

# (regex, tema, página do formulário do manual, modelo de providência)
TEMAS = [
    (r"ATESTO|ATESTAR|ORDENADOR", "Atesto/documento fiscal",
     31, "Incluir atesto identificado, datado e emitido por pessoa competente, conforme item 9.2 do manual."),
    (r"CHEQUE|CARIMBO.*PAGO|PAGO COM RECURSO|RECIBO", "Comprovação de pagamento",
     31, "Conferir carimbo de pagamento com identif. do recurso (NE/ano) e anexar recibo/cheque correspondente."),
    (r"NOTA FISCAL|NF\b|DOCUMENTO FISCAL|FATURA", "Documento fiscal",
     31, "Conferir NF em nome da UEx, vinculada ao programa, com atesto e comprovante de pagamento (item 9.4)."),
    (r"MAPA COMPARATIVO", "Mapa comparativo",
     27, "Refazer mapa comparativo conforme modelo do manual (p. 27), com quantidades, unidades, totais e critério."),
    (r"PROPOSTA|PREÇO|PRECO|VALOR ESTIMADO", "Propostas de preço",
     26, "Verificar propostas com objeto, quantidades, preços, validade e modalidade; corrigir por via formal cabível."),
    (r"ATA DA LICITA|ATA\b|ADJUDICA|HOMOLOGA", "Ata e resultado da licitação",
     27, "Conferir ata com valores, participantes, resultado, assinaturas e cronologia (itens 8.14–8.15)."),
    (r"EDITAL|INSTRUMENTO CONVOCAT|CONVITE|DISPENSA|LICITAÇÃO|LICITACAO",
     "Procedimento licitatório",
     26, "Conferir edital/instrumento convocatório, modalidade, publicidade e documentação do certame (cap. 8)."),
    (r"VISITA|COOPERAÇÃO|COOPERACAO TÉCNICA|COOPERACAO TECNICA",
     "Relatórios de cooperação",
     21, "Conferir relatórios por visita e relatório final com evidências (capítulo 6, escola apoiada/premiada)."),
    (r"PLANO DE APLICAÇÃO|PLANO APLICACAO|PLANO DE RECURSOS",
     "Plano de aplicação",
     33, "Conferir plano aprovado e versão executada; eventuais alterações exigem autorização (item 9.13)."),
    (r"CONCILIA|EXTRATO|SALDO", "Conciliação bancária",
     30, "Conferir extratos de todo o período e conciliação bancária com pendências explicadas (item 9.2)."),
    (r"FÍSICO-FINANCEIRO|FISICO-FINANCEIRO|ANEXO [IVX]+|EXECUÇÃO DA RECEITA|RELAÇÃO DE PAGAMENTO|RELAÇÃO DA EXECUÇÃO",
     "Demonstrativos da execução",
     30, "Conferir relação de pagamentos, execução físico-financeira e receita/despesa conforme item 9.2 e anexos."),
    (r"DECLARAÇÃO DE REGULARIDADE|DECLARACAO DE REGULARIDADE|REPRESENTANTE DOS ALUNOS|SEGMENTO|MANDATO|ELEIÇÃO|POSSE",
     "Governança e representação",
     30, "Conferir ata de eleição/posse, mandatos, segmentos e declaração de regularidade (item 9.2)."),
    (r"BEM|PERMANENTE|TOMBAMENTO|PATRIMÔNIO|PATRIMONIO",
     "Bens e patrimônio",
     31, "Conferir relação de bens, tombamento e destinação (item 9.6)."),
    (r"INSS|IRRF|ISS|RETENÇÃO|RETENCAO|TRIBUTO|ENCARGO",
     "Tributos e encargos",
     28, "Verificar retenções/recolhimentos devidos; exemplo do manual de 2019 é referência histórica — confirmar regra atual."),
    (r"PRAZO|VIGÊNCIA|VIGENCIA|PRORROGA",
     "Prazo e vigência",
     31, "Conferir vigência e eventuais prorrogações por ato competente (item 9.7)."),
    (r"LEI 8666|8.666|8666/93|LEI N", "Base legal (8.666/93)",
     28, "Citar a norma correta e aplicável ao exercício; conferir edição vigente."),
    (r"ORIGINAL|XEROX|CÓPIA|COPIA|AUTENTICA", "Originalidade e autenticação",
     31, "Substituir cópia por via original ou autenticada, conforme item 9.8 do manual."),
]


def _paginas_manual() -> Dict[int, str]:
    if not _MANUAL.exists():
        return {}
    texto = _MANUAL.read_text(encoding="utf-8", errors="ignore")
    blocos: Dict[int, str] = {}
    atual: int = 0
    for linha in texto.splitlines():
        m = re.match(r"^## PDF page (\d+)$", linha.strip())
        if m:
            atual = int(m.group(1))
            blocos[atual] = []
        elif atual and atual in blocos:
            blocos[atual].append(linha)
    return {k: "\n".join(v) for k, v in blocos.items()}


def classificar_item(texto: str) -> Dict[str, Any]:
    """Classifica uma demanda numa das categorias do manual."""
    t = texto.upper()
    for regex, tema, pagina, providencia in TEMAS:
        if re.search(regex, t):
            return {"tema": tema, "pagina_manual": pagina, "providencia_base": providencia}
    return {"tema": "Outro", "pagina_manual": None, "providencia_base": ""}


def _excerto_manual(pagina: int | None, limite: int = 500) -> str:
    if not pagina:
        return ""
    blocos = _paginas_manual()
    bloco = blocos.get(pagina, "")
    # remove cabeçalhos repetidos e compacta espaços
    sem_cab = re.sub(r"^\s*(Secretaria da Educacao.*|Eliana Nunes Estrela.*|.*Elaboragao.*)$",
                     "", bloco, flags=re.M)
    normalizado = re.sub(r"\s+", " ", sem_cab).strip()
    return normalizado[:limite]


def gerar_sugestoes(checklist: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Para cada item, proposta de providência + fundamento (sempre como sugestão)."""
    sugestoes: List[Dict[str, Any]] = []
    for item in checklist:
        cls = classificar_item(item.get("demanda", ""))
        pagina = cls["pagina_manual"]
        base = cls["providencia_base"]
        fundamento = f"Manual de Orientações 2019 (PDF p. {pagina})" if pagina else "Conferir norma aplicável ao exercício"
        sugestoes.append(
            {
                "id": item["id"],
                "demanda": item.get("demanda", ""),
                "pagina_diligencia": item.get("pagina", ""),
                "tema": cls["tema"],
                "pagina_manual": pagina,
                "excerto_manual": _excerto_manual(pagina),
                "providencia_sugerida": base,
                "fundamento_sugerido": fundamento,
                "revisar": True,
            }
        )
    return sugestoes


def gerar_relatorio_sugestoes(
    doc: Dict[str, Any], sugestoes: List[Dict[str, Any]]
) -> str:
    cab = doc.get("cabecalho", {})
    linhas = [
        "# Sugestões de preenchimento — PARA REVISÃO HUMANA",
        "",
        f"**Unidade Executora:** {cab.get('unidade_executora', '—')}",
        f"**Processo:** {cab.get('processo', '—')}  ·  **NE:** {cab.get('ne', '—')}/{cab.get('ano', '—')}",
        "",
        "As propostas abaixo são **sugestões de organização da resposta**. Antes de "
        "adotar qualquer providência: (1) confira o trecho citado do manual na "
        "imagem do PDF — o OCR auxiliar pode conter erros e **a imagem prevalece**; "
        "(2) confirme a norma aplicável ao exercício; (3) não fabrique documentos, "
        "assinaturas, carimbos ou datas.",
        "",
        "| ID | Tema | Sugestão de providência | Fundamento sugerido | Pág. dilig. | Pág. manual |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for s in sugestoes:
        linhas.append(
            f"| {s['id']} | {s['tema']} | {s['providencia_sugerida'] or '—'} | "
            f"{s['fundamento_sugerido']} | {s['pagina_diligencia'] or '—'} | "
            f"{s['pagina_manual'] or '—'} |"
        )
    linhas += [
        "",
        "> **Anti-overclaim:** estas sugestões não regularizam o processo nem "
        "declaram aprovação da SEDUC/13ª CREDE. O aceite depende do órgão "
        "competente após análise da documentação original.",
    ]
    return "\n".join(linhas)


def gerar_sugestoes_arquivo(
    doc: Dict[str, Any], sugestoes: List[Dict[str, Any]], destino: Path
) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(gerar_relatorio_sugestoes(doc, sugestoes), encoding="utf-8")