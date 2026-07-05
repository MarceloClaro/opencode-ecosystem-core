# -*- coding: utf-8 -*-
"""
Task Embedder — Camada de Embeddings
====================================
Analogia Transformer: converte tarefas e Agent Cards em vetores densos
(embeddings) para que o AttentionRouter possa calcular similaridade Q·K.

Implementação 100% stdlib (feature hashing + capacidades), sem dependências.

Inspiração:
- Token embeddings da arquitetura Transformer (Vaswani et al. 2017)
- Perceiver (deepmind-research): projeção de entradas heterogêneas num espaço latente comum

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import hashlib
import math
import re
from typing import Dict, List

D_MODEL = 64  # dimensão do espaço latente


def _hash_token(token: str, dim: int = D_MODEL) -> List[float]:
    """Feature hashing determinístico: token -> vetor esparso assinado."""
    vec = [0.0] * dim
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    # Usa pares de bytes para definir índice e sinal
    for i in range(0, 16, 2):
        idx = (digest[i] * 256 + digest[i + 1]) % dim
        sign = 1.0 if digest[i] % 2 == 0 else -1.0
        vec[idx] += sign
    return vec


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Zà-úÀ-Ú0-9_]+", text.lower())


def _normalize(vec: List[float]) -> List[float]:
    """LayerNorm simplificada: normalização L2 do vetor."""
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class TaskEmbedder:
    """Converte descrições de tarefas e Agent Cards em embeddings d=64."""

    def __init__(self, dim: int = D_MODEL):
        self.dim = dim

    def embed_text(self, text: str, positional_index: int = 0) -> List[float]:
        """Embedding de texto com codificação posicional senoidal."""
        vec = [0.0] * self.dim
        tokens = _tokenize(text)
        for token in tokens:
            token_vec = _hash_token(token, self.dim)
            for i in range(self.dim):
                vec[i] += token_vec[i]

        # Positional encoding (Vaswani et al. 2017, eq. senoidal)
        for i in range(0, self.dim, 2):
            angle = positional_index / (10000 ** (i / self.dim))
            vec[i] += 0.1 * math.sin(angle)
            if i + 1 < self.dim:
                vec[i + 1] += 0.1 * math.cos(angle)

        return _normalize(vec)

    def embed_task(self, description: str, required_capabilities: List[str],
                   positional_index: int = 0) -> List[float]:
        """Embedding de tarefa: descrição + capacidades requeridas (peso 2x)."""
        text = description + " " + " ".join(required_capabilities) * 2
        return self.embed_text(text, positional_index)

    def embed_agent(self, card: Dict) -> List[float]:
        """Embedding de Agent Card: nome + descrição + capacidades (peso 3x)."""
        caps = card.get("capabilities", [])
        text = (
            card.get("name", "") + " "
            + card.get("description", "") + " "
            + " ".join(caps) * 3
        )
        return self.embed_text(text)
