# -*- coding: utf-8 -*-
"""
Motor de produção em escala de artigos científicos (SPEC-935-R706).

Converte o pipeline pontual do relato TDAH (R689–R705) em motor genérico:
qualquer artigo (revisão, estudo de caso, original, TCC, dissertação) a
partir de ArticleConfig, com os mesmos gates e sem conteúdo codificado.

O motor NÃO gera conteúdo científico (texto dos módulos) — isso pertence ao
orquestrador/LLM e aos agentes. O motor fornece: estrutura, validação,
conversão e montagem.
"""
from research.manuscript.config import ArticleConfig, TIPOS, NORMAS
from research.manuscript.scaffold import scaffold_workspace
from research.manuscript.gates import run_gates
from research.manuscript.pipeline import produzir, produzir_lote

__all__ = ["ArticleConfig", "TIPOS", "NORMAS", "scaffold_workspace",
           "run_gates", "produzir", "produzir_lote"]
