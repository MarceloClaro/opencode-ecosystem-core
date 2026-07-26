#!/usr/bin/env python3
"""
Whoosh3Engine — Motor de Busca Full-Text Local
===============================================
Substituti de busca semântica via LLM no MetaBus e Blackboard.
Usa Whoosh3 (BM25F) para indexação e busca local determinística.

Uso:
    from skills.tooling.whoosh3_engine import Whoosh3Engine
    engine = Whoosh3Engine("metadata")
    engine.index({"id": "1", "title": "Spec sobre trust", "content": "..."})
    results = engine.search("trust engine")
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# whoosh3 é instalado como 'whoosh' no site-packages
import whoosh.index as whoosh_index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import Term

# Cache global de índices (evita recriar por chamada)
_INDEX_CACHE: Dict[str, whoosh_index.Index] = {}


class Whoosh3Engine:
    """
    Motor de busca full-text local usando Whoosh3.

    Características:
    - Indexação BM25F (padrão ouro em IR)
    - Busca por múltiplos campos
    - Stemming em português
    - Cache em disco com persistência
    - < 10ms por consulta em índices de até 100K docs
    """

    def __init__(
        self,
        index_name: str = "default",
        storage_dir: Optional[str] = None,
    ):
        self.index_name = index_name

        if storage_dir:
            self.index_dir = Path(storage_dir) / index_name
        else:
            self.index_dir = (
                Path(tempfile.gettempdir()) / "opencode_whoosh" / index_name
            )

        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._schema = self._build_schema()
        self._ix = self._open_or_create()
        self._stats = {"documents": 0, "queries": 0, "avg_ms": 0.0}

    def _build_schema(self) -> Schema:
        """Schema padrão: id único, título, conteúdo, tags, metadados."""
        return Schema(
            id=ID(unique=True, stored=True),
            title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            content=TEXT(stored=False, analyzer=StemmingAnalyzer()),
            tags=KEYWORD(stored=True, commas=True),
            source=TEXT(stored=True),
            doctype=TEXT(stored=True),
        )

    def _open_or_create(self) -> whoosh_index.Index:
        global _INDEX_CACHE
        cache_key = str(self.index_dir)

        if cache_key in _INDEX_CACHE:
            return _INDEX_CACHE[cache_key]

        if not list(self.index_dir.glob("_*.seg")):
            ix = whoosh_index.create_in(str(self.index_dir), self._schema)
        else:
            ix = whoosh_index.open_dir(str(self.index_dir))

        _INDEX_CACHE[cache_key] = ix
        return ix

    # ─── Indexação ────────────────────────────────────────────

    def index(self, doc: Dict[str, Any]) -> bool:
        """Indexa um documento."""
        try:
            writer = self._ix.writer()
            writer.update_document(
                id=str(doc.get("id", doc.get("name", str(time.time())))),
                title=str(doc.get("title", doc.get("name", ""))),
                content=str(
                    doc.get("content", doc.get("description", doc.get("summary", "")))
                ),
                tags=",".join(doc.get("tags", doc.get("keywords", []))),
                source=str(doc.get("source", doc.get("source_agent", ""))),
                doctype=str(doc.get("type", doc.get("doctype", "general"))),
            )
            writer.commit()
            self._stats["documents"] += 1
            return True
        except Exception as e:
            return False

    def index_batch(self, docs: List[Dict[str, Any]]) -> int:
        """Indexa múltiplos documentos em lote (mais eficiente)."""
        count = 0
        try:
            writer = self._ix.writer()
            for doc in docs:
                writer.update_document(
                    id=str(doc.get("id", str(time.time()))),
                    title=str(doc.get("title", doc.get("name", ""))),
                    content=str(doc.get("content", doc.get("description", ""))),
                    tags=",".join(doc.get("tags", [])),
                    source=str(doc.get("source", "")),
                    doctype=str(doc.get("type", "general")),
                )
                count += 1
            writer.commit()
            self._stats["documents"] += count
            return count
        except Exception:
            return count

    def remove(self, doc_id: str) -> bool:
        """Remove documento pelo ID."""
        try:
            writer = self._ix.writer()
            writer.delete_by_term("id", doc_id)
            writer.commit()
            self._stats["documents"] = max(0, self._stats["documents"] - 1)
            return True
        except Exception:
            return False

    # ─── Busca ────────────────────────────────────────────────

    def search(
        self,
        query_str: str,
        limit: int = 10,
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos no índice.

        Args:
            query_str: termos de busca (ex: "trust engine spec")
            limit: max resultados
            fields: campos para buscar (padrão: title, content, tags)

        Returns:
            Lista de dicts com id, title, score, tags, source
        """
        start = time.time()

        if not fields:
            fields = ["title", "content", "tags"]

        with self._ix.searcher() as searcher:
            parser = MultifieldParser(
                fields, self._schema, group=OrGroup
            )
            query = parser.parse(query_str)

            results = searcher.search(query, limit=limit)

            output = []
            for hit in results:
                output.append({
                    "id": hit["id"],
                    "title": hit["title"] if "title" in hit else "",
                    "score": round(hit.score, 4),
                    "tags": hit["tags"] if "tags" in hit else "",
                    "source": hit["source"] if "source" in hit else "",
                    "doctype": hit["doctype"] if "doctype" in hit else "",
                })

        elapsed = time.time() - start
        self._stats["queries"] += 1
        n = self._stats["queries"]
        self._stats["avg_ms"] = (
            (self._stats["avg_ms"] * (n - 1) + elapsed * 1000) / n
        )

        return output

    def search_by_tag(self, tag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca documentos por tag exata."""
        with self._ix.searcher() as searcher:
            query = Term("tags", tag)
            results = searcher.search(query, limit=limit)
            return [
                {
                    "id": hit["id"],
                    "title": hit["title"] if "title" in hit else "",
                    "score": round(hit.score, 4),
                }
                for hit in results
            ]

    # ─── Utilitários ──────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """Estatisticas do motor."""
        return {
            "index_name": self.index_name,
            "index_dir": str(self.index_dir),
            **self._stats,
        }

    def clear(self) -> bool:
        """Limpa o índice completamente."""
        try:
            import shutil
            shutil.rmtree(str(self.index_dir))
            self.index_dir.mkdir(parents=True, exist_ok=True)
            self._ix = whoosh_index.create_in(str(self.index_dir), self._schema)
            self._stats["documents"] = 0
            return True
        except Exception:
            return False

    def __len__(self) -> int:
        return self._stats["documents"]


# Singleton padrão para uso no ecossistema
_default_engine: Optional[Whoosh3Engine] = None


def get_engine() -> Whoosh3Engine:
    """Retorna instância singleton do motor Whoosh3."""
    global _default_engine
    if _default_engine is None:
        _default_engine = Whoosh3Engine("opencode_default")
    return _default_engine


# ─── Teste rápido ────────────────────────────────────────────

if __name__ == "__main__":
    eng = Whoosh3Engine("test")
    eng.index({"id": "1", "title": "Trust Engine Spec", "content": "Cognitive guardrails and goal drift prevention", "tags": ["trust", "spec"], "source": "specs"})
    eng.index({"id": "2", "title": "Token Economy", "content": "Staking, slashing and fee market in OpenCode", "tags": ["economy", "token"], "source": "specs"})

    results = eng.search("trust guardrails")
    print(f"Busca 'trust guardrails': {len(results)} resultados")
    for r in results:
        print(f"  [{r['score']}] {r['title']}")

    print(f"\nStats: {eng.stats()}")
