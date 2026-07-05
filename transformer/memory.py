# -*- coding: utf-8 -*-
"""
Hierarchical Memory — Memória Hierárquica de Longo Prazo
========================================================
Analogia Transformer: KV-cache hierárquico. Inspirado no
Hierarchical Transformer Memory (HTM, deepmind-research): eventos são
agrupados em *chunks*, cada chunk recebe um sumário (embedding médio),
e a recuperação faz atenção em dois níveis:
1. Atenção grossa sobre sumários de chunks (barato)
2. Atenção fina apenas dentro dos top-k chunks relevantes

Opera sobre a memória episódica da MetacognitiveMemory (camada MCI).

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from typing import Dict, List, Any

from .embedder import TaskEmbedder
from .attention import _dot


CHUNK_SIZE = 8  # eventos por chunk


class HierarchicalMemory:
    """Recuperação hierárquica em dois níveis sobre a memória episódica."""

    def __init__(self, metacognitive_memory):
        self.memory = metacognitive_memory
        self.embedder = TaskEmbedder()

    def _entry_text(self, entry: Dict[str, Any]) -> str:
        return f"{entry.get('agent_id', '')} {entry.get('context', '')} {entry.get('reflection', '')}"

    def _build_chunks(self) -> List[Dict[str, Any]]:
        """Agrupa a memória episódica em chunks com sumário vetorial."""
        episodic = self.memory.episodic
        chunks = []
        for start in range(0, len(episodic), CHUNK_SIZE):
            entries = episodic[start:start + CHUNK_SIZE]
            vectors = [self.embedder.embed_text(self._entry_text(e)) for e in entries]
            dim = len(vectors[0]) if vectors else 0
            summary = [
                sum(v[i] for v in vectors) / len(vectors) if vectors else 0.0
                for i in range(dim)
            ]
            chunks.append({"entries": entries, "vectors": vectors, "summary": summary})
        return chunks

    def retrieve(self, query: str, top_chunks: int = 2, top_entries: int = 5) -> List[Dict[str, Any]]:
        """
        Recuperação em dois níveis (HTM):
        1. Rankeia chunks pelo sumário (atenção grossa)
        2. Rankeia eventos dentro dos melhores chunks (atenção fina)
        """
        chunks = self._build_chunks()
        if not chunks:
            return []

        query_vec = self.embedder.embed_text(query)

        # Nível 1 — atenção grossa sobre sumários
        chunk_scores = [
            (_dot(query_vec, c["summary"]), c) for c in chunks if c["summary"]
        ]
        chunk_scores.sort(key=lambda x: x[0], reverse=True)
        selected = [c for _, c in chunk_scores[:top_chunks]]

        # Nível 2 — atenção fina dentro dos chunks selecionados
        scored_entries = []
        for chunk in selected:
            for entry, vec in zip(chunk["entries"], chunk["vectors"]):
                scored_entries.append((_dot(query_vec, vec), entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [
            {"relevance": round(score, 4), **entry}
            for score, entry in scored_entries[:top_entries]
        ]
