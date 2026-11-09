#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Leitor estruturado das 100 fichas de evidência.

As fichas em ``fichas/F001..F100`` são a fonte de evidência por conceito.
Este módulo extrai campos estáveis para que o gerador das 3000 laudas
distribua evidência específica por lente, em vez de repetir o mesmo
dossiê nas dez lentes do mesmo conceito.

O parser é deliberadamente conservador: se um campo obrigatório faltar,
o carregamento falha em vez de produzir uma lauda com evidência vazia.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FICHAS_DIR = RAIZ / "fichas"


def _texto(valor: str) -> str:
    """Converte um fragmento HTML em texto normalizado."""
    valor = re.sub(r"<br\s*/?>", " ", valor, flags=re.I)
    valor = re.sub(r"<[^>]+>", " ", valor)
    valor = html.unescape(valor)
    return re.sub(r"\s+", " ", valor).strip()


def _campo(texto: str, rotulo: str) -> str:
    padrao = rf"<p><strong>{re.escape(rotulo)}:</strong>\s*(.*?)</p>"
    encontrado = re.search(padrao, texto, flags=re.S)
    return encontrado.group(1).strip() if encontrado else ""


def _campo_mini(texto: str, rotulo: str) -> str:
    padrao = rf'<p class="mini"><strong>{re.escape(rotulo)}:</strong>\s*(.*?)</p>'
    encontrado = re.search(padrao, texto, flags=re.S)
    return encontrado.group(1).strip() if encontrado else ""


def _resultado(texto: str) -> str:
    bloco = re.search(r'<div class="resultado">(.*?)</div>', texto, flags=re.S)
    if not bloco:
        return ""
    interior = bloco.group(1)
    partes: list[str] = []
    for rotulo in ("Experimento", "Simulado", "Backend", "Sobreposição"):
        encontrado = re.search(
            rf"<strong>{rotulo}:</strong>\s*(.*?)(?:<br\s*/?>|</p>|$)",
            interior,
            flags=re.S,
        )
        if encontrado:
            partes.append(f"{rotulo}: {_texto(encontrado.group(1))}")
    return "; ".join(partes)


def _autor_ano_doi(fonte_html: str) -> tuple[str, str, str]:
    texto = _texto(fonte_html)
    autor = ""
    encontrado = re.match(
        r"([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][A-ZÁÀÂÃÉÊÍÓÔÕÚÇ'\-]+)", texto
    )
    if encontrado:
        autor = encontrado.group(1)
    elif texto:
        autor = texto.split()[0]
    ano = ""
    encontrado = re.search(r"\b(?:19|20)\d{2}\b", texto)
    if encontrado:
        ano = encontrado.group(0)
    doi = ""
    encontrado = re.search(r"10\.\d{4,9}/[^\s<]+", texto)
    if encontrado:
        doi = encontrado.group(0).rstrip(".,;)")
    return autor, ano, doi


@dataclass(frozen=True)
class Ficha:
    """Campos estáveis de uma ficha de evidência."""

    codigo: str
    numero: int
    conceito: str
    frase: str
    fonte: str
    fonte_html: str
    medido: str
    nao_prova: str
    pratica: str
    resultado: str
    grau: str
    grau_texto: str
    citar: str
    citar_html: str
    leitura: str
    leitura_html: str
    autor: str
    ano: str
    doi: str

    @property
    def fonte_curta(self) -> str:
        partes = [self.autor]
        if self.ano:
            partes.append(f"({self.ano})")
        if self.doi:
            partes.append(f"DOI {self.doi}")
        return " ".join(parte for parte in partes if parte)

    @property
    def leitura_curta(self) -> str:
        autor, ano, doi = _autor_ano_doi(self.leitura_html)
        partes = [autor]
        if ano:
            partes.append(f"({ano})")
        if doi:
            partes.append(f"DOI {doi}")
        return " ".join(parte for parte in partes if parte)

    @property
    def fonte_link(self) -> str:
        if self.doi:
            return (
                f'<a href="https://doi.org/{html.escape(self.doi, quote=True)}">'
                f"{html.escape(self.doi)}</a>"
            )
        return html.escape(self.fonte_curta)

    @property
    def leitura_link(self) -> str:
        _, _, doi = _autor_ano_doi(self.leitura_html)
        if doi:
            return (
                f'<a href="https://doi.org/{html.escape(doi, quote=True)}">'
                f"{html.escape(doi)}</a>"
            )
        return html.escape(self.leitura_curta)


def carregar_ficha(caminho: Path) -> Ficha:
    texto = caminho.read_text(encoding="utf-8")
    codigo = ""
    encontrado = re.search(r'<span class="cod">(F\d{3})</span>', texto)
    if encontrado:
        codigo = encontrado.group(1)
    conceito = ""
    encontrado = re.search(
        r'<span class="conc">C\d{3}\s*·\s*(.*?)</span>', texto
    )
    if encontrado:
        conceito = _texto(encontrado.group(1))

    fonte_html = _campo(texto, "Fonte primária")
    citar_html = _campo_mini(texto, "Para citar")
    leitura_html = _campo_mini(texto, "Leitura complementar")
    if not citar_html:
        citar_html = fonte_html
    if not leitura_html:
        leitura_html = fonte_html
    autor, ano, doi = _autor_ano_doi(fonte_html)

    grau = ""
    grau_texto = ""
    encontrado = re.search(
        r'<div class="grau"><strong>Grau de evidência:\s*([A-E])</strong>'
        r"\s*—\s*(.*?)</div>",
        texto,
        flags=re.S,
    )
    if encontrado:
        grau = encontrado.group(1)
        grau_texto = _texto(encontrado.group(2))

    numero = int(codigo[1:]) if codigo else 0
    ficha = Ficha(
        codigo=codigo,
        numero=numero,
        conceito=conceito,
        frase=_texto(_campo(texto, "Em uma frase")),
        fonte=_texto(fonte_html),
        fonte_html=fonte_html,
        medido=_texto(_campo(texto, "O que foi medido")),
        nao_prova=_texto(_campo(texto, "O que não prova")),
        pratica=_texto(_campo(texto, "Prática")),
        resultado=_resultado(texto),
        grau=grau,
        grau_texto=grau_texto,
        citar=_texto(citar_html),
        citar_html=citar_html,
        leitura=_texto(leitura_html),
        leitura_html=leitura_html,
        autor=autor,
        ano=ano,
        doi=doi,
    )
    obrigatorios = {
        "código": ficha.codigo,
        "conceito": ficha.conceito,
        "frase": ficha.frase,
        "fonte": ficha.fonte,
        "medido": ficha.medido,
        "não prova": ficha.nao_prova,
        "prática": ficha.pratica,
        "grau": ficha.grau,
        "grau_texto": ficha.grau_texto,
        "leitura": ficha.leitura,
    }
    faltando = [nome for nome, valor in obrigatorios.items() if not valor]
    if faltando:
        raise ValueError(f"{caminho.name}: campos vazios: {', '.join(faltando)}")
    return ficha


def carregar_fichas() -> dict[int, Ficha]:
    fichas: dict[int, Ficha] = {}
    for caminho in sorted(FICHAS_DIR.glob("F*.md")):
        ficha = carregar_ficha(caminho)
        fichas[ficha.numero] = ficha
    if sorted(fichas) != list(range(1, 101)):
        faltando = sorted(set(range(1, 101)) - set(fichas))
        raise ValueError(f"fichas ausentes ou fora de ordem: {faltando}")
    return fichas


FICHAS = carregar_fichas()
