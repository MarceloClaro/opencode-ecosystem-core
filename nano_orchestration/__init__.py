"""Nano-Orquestração para Manuscritos de Grande Escala (R53).

Decompõe manuscritos de até 500 laudas em nanoblocos,
escreve em paralelo via pool LiteRT-LM, e funde com 3 passagens de coerência.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class BlockType(str, Enum):
    """Tipo funcional de cada nanobloco."""
    DESCRITIVO = "descritivo"
    ARGUMENTATIVO = "argumentativo"
    ANALITICO = "analitico"
    TRANSICAO = "transicao"
    CITAÇÃO = "citacao"
    METODOLOGIA = "metodologia"
    RESULTADO = "resultado"
    DISCUSSAO = "discussao"
    CONCLUSÃO = "conclusao"


class ModelTier(str, Enum):
    """Nível de modelo para execução."""
    QWEN3_0_6B = "litert-community/Qwen3-0.6B"
    GEMMA4_2B = "litert-community/gemma-4-E2B-it-litert-lm"
    GEMMA4_4B = "litert-community/gemma-4-E4B-it-litert-lm"


MODEL_TIER_BY_BLOCK_TYPE = {
    BlockType.DESCRITIVO: ModelTier.QWEN3_0_6B,
    BlockType.TRANSICAO: ModelTier.QWEN3_0_6B,
    BlockType.CITAÇÃO: ModelTier.QWEN3_0_6B,
    BlockType.ARGUMENTATIVO: ModelTier.GEMMA4_2B,
    BlockType.METODOLOGIA: ModelTier.GEMMA4_2B,
    BlockType.RESULTADO: ModelTier.GEMMA4_2B,
    BlockType.ANALITICO: ModelTier.GEMMA4_4B,
    BlockType.DISCUSSAO: ModelTier.GEMMA4_4B,
    BlockType.CONCLUSÃO: ModelTier.GEMMA4_4B,
}

TIMEOUT_BY_BLOCK_TYPE = {
    BlockType.DESCRITIVO: 30,
    BlockType.TRANSICAO: 20,
    BlockType.CITAÇÃO: 25,
    BlockType.ARGUMENTATIVO: 60,
    BlockType.METODOLOGIA: 60,
    BlockType.RESULTADO: 45,
    BlockType.ANALITICO: 120,
    BlockType.DISCUSSAO: 120,
    BlockType.CONCLUSÃO: 90,
}

LINE_RANGE = (80, 120)  # linhas por nanobloco
TOKEN_LIMIT_PER_BLOCK = 400  # contexto máximo por bloco
PARALLEL_WORKERS_DEFAULT = 5
MAX_RETRIES = 3
COHERENCE_SCORE_TARGET = 9.5
FIDELITY_THRESHOLD = 0.95


@dataclass
class Criterion:
    """Um critério de aceitação para um nanobloco."""
    id: str
    description: str
    weight: int = 3  # 1-5
    passed: Optional[bool] = None
    note: str = ""


@dataclass
class NanoBlock:
    """Um nanobloco individual de texto."""
    id: str = ""
    index: int = 0
    block_type: BlockType = BlockType.DESCRITIVO
    section: str = ""
    title: str = ""
    content: str = ""
    estimated_tokens: int = 300
    actual_tokens: int = 0
    dependencies: list[int] = field(default_factory=list)
    criteria: list[Criterion] = field(default_factory=list)
    model_used: Optional[ModelTier] = None
    retries: int = 0
    quality_score: float = 0.0
    coherence_score: float = 0.0
    status: str = "pending"  # pending|written|verified|failed
    error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NanoPlan:
    """Plano completo de nano-orquestração."""
    id: str = ""
    title: str = ""
    total_pages: int = 0
    total_blocks: int = 0
    blocks: list[NanoBlock] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    estimated_total_tokens: int = 0
    created_at: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "total_pages": self.total_pages,
            "total_blocks": self.total_blocks,
            "sections": self.sections,
            "estimated_total_tokens": self.estimated_total_tokens,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "blocks": [b.to_dict() for b in self.blocks],
        }


@dataclass
class QualityReport:
    """Relatório de qualidade de um nanobloco."""
    block_id: str
    criteria_passed: int
    criteria_total: int
    score: float
    retries: int
    model_used: ModelTier
    time_ms: float
    issues: list[str] = field(default_factory=list)
    passed: bool = False


@dataclass
class ValidationReport:
    """Relatório de validação cruzada."""
    total_blocks: int
    validated_pairs: int
    smooth_transitions: int
    contradictions: int
    term_consistency: float
    cohesion_score: float
    passed: bool = False
    details: list[dict] = field(default_factory=list)


def default_nano_block(index: int, block_type: BlockType = BlockType.DESCRITIVO,
                       section: str = "", title: str = "") -> NanoBlock:
    """Cria um nanobloco com valores padrão."""
    return NanoBlock(
        id=f"nb-{index:05d}-{uuid.uuid4().hex[:8]}",
        index=index,
        block_type=block_type,
        section=section,
        title=title,
        estimated_tokens=300,
    )
