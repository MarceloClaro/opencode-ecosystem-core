# -*- coding: utf-8 -*-
"""Configuração de artigo para produção em escala (SPEC-935-R706, AC1)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


TIPOS = (
    "revisao-integrativa",
    "estudo-de-caso",
    "artigo-original",
    "tcc",
    "dissertacao",
)

NORMAS = ("ABNT", "APA", "Vancouver")

MODULOS_POR_TIPO: dict[str, list[str]] = {
    "revisao-integrativa": ["resumo", "introducao", "objetivos", "metodo",
                            "resultados", "discussao", "conclusao", "referencias"],
    "estudo-de-caso": ["resumo", "introducao", "objetivos", "metodo",
                       "relato", "discussao", "conclusao", "referencias"],
    "artigo-original": ["resumo", "introducao", "objetivos", "metodo",
                        "resultados", "discussao", "conclusao", "referencias"],
    "tcc": ["resumo", "introducao", "objetivos", "referencial",
            "metodo", "resultados", "discussao", "conclusao", "referencias"],
    "dissertacao": ["resumo", "introducao", "objetivos", "referencial",
                    "metodo", "resultados", "discussao", "conclusao", "referencias"],
}


def slugify(titulo: str) -> str:
    base = titulo.lower()
    base = re.sub(r"[àáâãä]", "a", base)
    base = re.sub(r"[èéêë]", "e", base)
    base = re.sub(r"[ìíîï]", "i", base)
    base = re.sub(r"[òóôõö]", "o", base)
    base = re.sub(r"[ùúûü]", "u", base)
    base = re.sub(r"[ç]", "c", base)
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base[:60] or "artigo"


@dataclass
class ArticleConfig:
    """Parâmetros de um artigo. Todos validados em __post_init__ (fail-closed)."""

    titulo: str
    autores: list[str]
    area: str
    nivel: str = "graduacao"
    tipo: str = "revisao-integrativa"
    norma: str = "ABNT"
    idioma: str = "pt-BR"
    periodico_alvo: str = ""
    saida_base: str = "artigos"

    slug: str = field(init=False)
    modulos: list[str] = field(init=False)

    def __post_init__(self) -> None:
        if not self.titulo or not self.titulo.strip():
            raise ValueError("titulo não pode ser vazio.")
        if not self.autores or not any(a.strip() for a in self.autores):
            raise ValueError("autores precisa de ao menos um nome não vazio.")
        if not self.area or not self.area.strip():
            raise ValueError("area não pode ser vazia.")
        if self.tipo not in TIPOS:
            raise ValueError(f"tipo inválido: {self.tipo!r}. Válidos: {list(TIPOS)}.")
        if self.norma not in NORMAS:
            raise ValueError(f"norma inválida: {self.norma!r}. Válidas: {list(NORMAS)}.")
        object.__setattr__(self, "slug", slugify(self.titulo))
        object.__setattr__(self, "modulos", list(MODULOS_POR_TIPO[self.tipo]))
