# -*- coding: utf-8 -*-
"""
Parsing de diligências do Prêmio Escola Nota Dez (SEDUC/CE)
============================================================
Extrai, de um texto OCR de diligência, a estrutura:
  - cabeçalho (processo, unidade executora, município, CNPJ, NE, valor, ano)
  - blocos (por licitação/objeto: "COMUM A TODAS AS LICITAÇÕES",
    "DISPENSA DE LICITAÇÃO...", etc.)
  - demandas (itens apontados no texto, com referência de página quando houver)

O parser é tolerante a ruído de OCR (linhas quebradas, marcadores trocados
por letras como "*", "+", "e", "o") e preserva o texto original de cada item.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

_MARCADORES_ITEM = ("*", "+", "•", "-", "e", "o", "0", "€", "&")
_RE_PAGINA = re.compile(r"\(?\s*PAG\.\s*([0-9]+(?:\s*[eE]\s*[0-9]+)?)\s*\)?", re.I)


def _normalizar_linhas(texto: str) -> List[str]:
    """Quebra em linhas, remove linhas vazias e espaços redundantes."""
    linhas = []
    for raw in texto.splitlines():
        linha = re.sub(r"\s+", " ", raw).strip()
        if linha:
            linhas.append(linha)
    return linhas


def _extrair_cabecalho(linhas: List[str]) -> Dict[str, str]:
    cab = {}
    bloco = "\n".join(linhas[:60])
    for chave, padrao in (
        ("processo", r"PROCESSO\s*[:=]\s*([0-9]+)"),
        ("unidade_executora", r"UNIDADE\s+EXECUTORA\s*[:=]\s*([^\n|]+)"),
        ("endereco", r"ENDEREÇO\s*[:=]\s*([^\n|]+)"),
        ("municipio", r"MUNICÍPIO\s*[:=]\s*([A-ZÁ-Ú\s]+?)(?=\s+CREDOR|\s+CNPJ|\s*\n|$)"),
        ("cnpj", r"CNPJ\s*[:=]\s*([0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2})"),
        ("ne", r"\bNE\s*[:=]\s*([0-9]+)"),
        ("valor", r"VALOR\s*[:=]\s*((?:R\$\s*)?[0-9][0-9.,]*)"),
        ("ano", r"\bANO\s*[:=]\s*([0-9]{4})"),
    ):
        m = re.search(padrao, bloco, re.I)
        if m:
            cab[chave] = m.group(1).strip()
    return cab


def _extrair_metadados_bloco(linhas: List[str]) -> Dict[str, str]:
    """Metadados do bloco de licitação: OBJETO DA AÇÃO, VALOR ESTIMADO,
    DATA DA LICITAÇÃO — quando presentes no texto OCR."""
    metadados: Dict[str, str] = {}
    texto = "\n".join(linhas)
    for chave, padrao in (
        ("objeto", r"OBJETO\s+DA\s+AÇÃO\s*[:=]\s*([^\n]+)"),
        ("valor_estimado", r"VALOR\s+ESTIMADO\s+DA\s+AÇÃO/OBJETOS?\s*[:=]\s*([^\n]+)"),
        ("data_licitacao", r"DATA\s+DA\s+LICITAÇÃO\s*[:=]\s*([^\n]+)"),
    ):
        m = re.search(padrao, texto, re.I)
        if m:
            metadados[chave] = m.group(1).strip()
    return metadados


def _extrair_demandas_do_bloco(linhas: List[str]) -> List[Dict[str, Any]]:
    """Captura itens de demanda dentro de um bloco já delimitado."""
    demandas: List[Dict[str, Any]] = []
    atual: List[str] = []
    pagina_atual: str = ""

    def fecha_atual():
        nonlocal atual, pagina_atual
        if atual:
            texto = " ".join(atual)
            texto = re.sub(r"\s+", " ", texto).strip(" *+•-e o,:;")
            if texto:
                demandas.append({"texto": texto, "pagina": pagina_atual})
            atual, pagina_atual = [], ""

    for linha in linhas:
        m_pag = _RE_PAGINA.search(linha)
        primeiro = linha.lstrip()[:1]
        if atual and primeiro in _MARCADORES_ITEM:
            # Novo item começando com marcador
            fecha_atual()
        if atual or primeiro in _MARCADORES_ITEM:
            if m_pag:
                pagina_atual = m_pag.group(1).replace(" ", "")
            atual.append(linha)
        # Linhas sem marcador após itens são continuação; linhas soltas
        # (títulos de seção) não entram.
        elif primeiro not in _MARCADORES_ITEM and not atual:
            # trecho de cabeçalho; ignora
            continue
    fecha_atual()
    return demandas


def parse_diligencia(texto: str, fonte: str = "") -> Dict[str, Any]:
    """Converte o texto OCR de uma diligência em estrutura JSON serializável."""
    linhas = _normalizar_linhas(texto)
    cabecalho = _extrair_cabecalho(linhas)

    # Divide em blocos por marcadores de seção (linhas em MAIÚSCULAS curtas
    # como "COMUM A TODAS AS LICITAÇÕES/OBJETO" ou "DISPENSA DE LICITAÇÃO ...").
    blocos: List[Dict[str, Any]] = []
    atual: Dict[str, Any] | None = None
    dentro_demandas = False

    for i, linha in enumerate(linhas):
        eh_titulo = (
            len(linha) <= 90
            and linha.upper() == linha
            and not linha.lstrip().startswith(('"', "'", "[", "(", "»", "CONVITE", "PARA", "DO ", "DOS ", "MAPA"))
            and (
                "DISPENSA DE LICITAÇÃO" in linha.upper()
                or linha.upper().startswith("COMUM A TODAS")
            )
            and not re.search(
                r"DEMANDAS|PROCESSO|NE\s*[:=]|OBJETO DA|VALOR ESTIMADO|DATA DA|"
                r"MAPA COMPARATIVO|REFERÊNCIA DA|CARTA CONVITE|REPRESENTANTES|PROPOSTAS|"
                r"EDITAL DE LICITAÇÃO",
                linha,
                re.I,
            )
        )
        if eh_titulo:
            if atual:
                atual["demandas"] = _extrair_demandas_do_bloco(atual["_linhas_demanda"])
                atual["metadados"] = _extrair_metadados_bloco(atual["_linhas_bloco"])
            atual = {"titulo": linha.strip(), "demandas": [], "metadados": {}, "_linhas_demanda": [], "_linhas_bloco": []}
            blocos.append(atual)
            dentro_demandas = False
            continue

        if atual is not None:
            if re.search(r"^DEMANDAS\s*[:]?\s*$", linha, re.I):
                dentro_demandas = True
                continue
            m_demanda = re.search(r"^DEMANDAS\s*[:]?\s*(.+)$", linha, re.I)
            if m_demanda and m_demanda.group(1).strip():
                dentro_demandas = True
                atual["_linhas_demanda"].append(m_demanda.group(1).strip())
                continue
            if dentro_demandas and not re.search(r"DEMANDAS", linha, re.I):
                atual["_linhas_demanda"].append(linha)
            elif not dentro_demandas:
                atual["_linhas_bloco"].append(linha)

    if atual:
        atual["demandas"] = _extrair_demandas_do_bloco(atual["_linhas_demanda"])
        atual["metadados"] = _extrair_metadados_bloco(atual["_linhas_bloco"])
    for b in blocos:
        b.pop("_linhas_demanda", None)
        b.pop("_linhas_bloco", None)

    return {
        "fonte": fonte,
        "cabecalho": cabecalho,
        "blocos": blocos,
        "total_demandas": sum(len(b["demandas"]) for b in blocos),
    }


def extrair_demandas(texto: str) -> List[Dict[str, Any]]:
    """Retorna todas as demandas da diligência (independe de blocos)."""
    doc = parse_diligencia(texto)
    return [d for b in doc["blocos"] for d in b["demandas"]]