"""Laboratórios REAIS locais do RX — SPEC-935-R900.

Este pacote expõe, por API-JSON, o trabalho real já existente em
``odonto/local`` (datasets, treinos, autômatos celulares) sem prometer
inferência hospedada. Todo payload real traz ``real: true``; o nível de
alegação permanece ``descritivo_nao_causal`` (CA) ou ``comparacao_empirica``
(ML). Revisão humana obrigatória.
"""

from __future__ import annotations

from .paths import DATASETS, LOCAL, OUTPUTS, TABLE_S1, ensure_import_path

__all__ = ["DATASETS", "LOCAL", "OUTPUTS", "TABLE_S1", "ensure_import_path"]
