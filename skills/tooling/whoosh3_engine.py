#!/usr/bin/env python3
"""
Whoosh3Engine — Motor de Busca Full-Text Local
===============================================
Busca lexical local para o MetaBus e o Blackboard; não produz embeddings.
Usa Whoosh3 (BM25F) para indexação e busca local determinística.

Uso:
    from skills.tooling.whoosh3_engine import Whoosh3Engine
    engine = Whoosh3Engine("metadata")
    engine.index({"id": "1", "title": "Spec sobre trust", "content": "..."})
    results = engine.search("trust engine")
"""

from __future__ import annotations

import logging
import tempfile
import time
from pathlib import Path
from threading import RLock
from typing import Any

# whoosh3 é instalado como 'whoosh' no site-packages
import whoosh.index as whoosh_index
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import Term
from whoosh.util.filelock import FileLock, try_for

# Cache global de índices (evita recriar por chamada)
_INDEX_CACHE: dict[str, whoosh_index.Index] = {}
_CACHE_LOCK = RLock()
_INIT_TIMEOUT = 5.0
_WRITE_TIMEOUT = 5.0
_LOGGER = logging.getLogger(__name__)


class Whoosh3Engine:
    """
    Motor de busca full-text local usando Whoosh3.

    Características:
    - Indexação lexical BM25F
    - Busca por múltiplos campos
    - Stemming conforme o analisador configurado do Whoosh
    - Cache em disco com persistência
    - Tempos e capacidade dependem da carga e do ambiente; sem SLA medido
    """

    def __init__(
        self,
        index_name: str = "default",
        storage_dir: str | None = None,
    ):
        self.index_name = index_name

        if storage_dir:
            self.index_dir = Path(storage_dir) / index_name
        else:
            self.index_dir = (
                Path(tempfile.gettempdir()) / "opencode_whoosh" / index_name
            )

        self.index_dir = self.index_dir.resolve()
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._schema = self._build_schema()
        self._ix = self._open_or_create()
        # O schema persistido é o contrato real; não migra índices legados.
        self._schema = self._ix.schema
        self._stats = {"documents": 0, "queries": 0, "avg_ms": 0.0}

    def _build_schema(self) -> Schema:
        """Schema padrão: id único, título, conteúdo, tags, metadados."""
        return Schema(
            id=ID(unique=True, stored=True),
            title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            tags=KEYWORD(stored=True, commas=True),
            source=TEXT(stored=True),
            doctype=TEXT(stored=True),
        )

    def _open_or_create(self) -> whoosh_index.Index:
        cache_key = str(self.index_dir)
        # O guard protege o cache e inicializações em threads do mesmo processo.
        # O lock de arquivo também serializa processos independentes.
        with _CACHE_LOCK:
            if cache_key in _INDEX_CACHE:
                return _INDEX_CACHE[cache_key]
            lock = FileLock(str(self.index_dir / "CORE_INITLOCK"))
            if not try_for(lock.acquire, timeout=_INIT_TIMEOUT, delay=0.05):
                raise TimeoutError("Prazo de inicialização do índice Whoosh excedido")
            try:
                if whoosh_index.exists_in(str(self.index_dir)):
                    ix = whoosh_index.open_dir(str(self.index_dir))
                else:
                    ix = whoosh_index.create_in(str(self.index_dir), self._schema)
                _INDEX_CACHE[cache_key] = ix
                return ix
            finally:
                lock.release()

    @staticmethod
    def _cancel_writer(writer) -> None:
        """Desfaz escrita incompleta e libera o lock mesmo se a limpeza falhar."""
        if writer is None or getattr(writer, "is_closed", False):
            return
        try:
            writer.cancel()
        except Exception:
            _LOGGER.warning(
                "Falha na limpeza do writer Whoosh; liberando lock próprio",
                exc_info=True,
            )
            lock = getattr(writer, "writelock", None)
            if lock is not None and getattr(lock, "fd", None) is not None:
                try:
                    lock.release()
                except Exception:
                    _LOGGER.warning(
                        "Falha ao liberar lock próprio do Whoosh", exc_info=True
                    )

    # ─── Indexação ────────────────────────────────────────────

    def index(self, doc: dict[str, Any]) -> bool:
        """Indexa documento com corpo textual; tipos não textuais são recusados."""
        writer = None
        try:
            content = doc.get("content", doc.get("description", doc.get("summary", "")))
            if not isinstance(content, str):
                raise TypeError("O conteúdo documental deve ser uma string.")
            writer = self._ix.writer(timeout=_WRITE_TIMEOUT, delay=0.05)
            writer.update_document(
                id=str(doc.get("id", doc.get("name", str(time.time())))),
                title=str(doc.get("title", doc.get("name", ""))),
                content=content,
                tags=",".join(doc.get("tags", doc.get("keywords", []))),
                source=str(doc.get("source", doc.get("source_agent", ""))),
                doctype=str(doc.get("type", doc.get("doctype", "general"))),
            )
            writer.commit()
            self._stats["documents"] += 1
            return True
        except Exception:
            _LOGGER.warning("Escrita Whoosh não confirmada", exc_info=True)
            self._cancel_writer(writer)
            return False

    def index_batch(self, docs: list[dict[str, Any]]) -> int:
        """Confirma o lote apenas com corpos textuais; tipo inválido cancela o lote."""
        count = 0
        writer = None
        try:
            writer = self._ix.writer(timeout=_WRITE_TIMEOUT, delay=0.05)
            for doc in docs:
                content = doc.get("content", doc.get("description", ""))
                if not isinstance(content, str):
                    raise TypeError("O conteúdo documental deve ser uma string.")
                writer.update_document(
                    id=str(doc.get("id", str(time.time()))),
                    title=str(doc.get("title", doc.get("name", ""))),
                    content=content,
                    tags=",".join(doc.get("tags", [])),
                    source=str(doc.get("source", "")),
                    doctype=str(doc.get("type", "general")),
                )
                count += 1
            writer.commit()
            self._stats["documents"] += count
            return count
        except Exception:
            _LOGGER.warning("Lote Whoosh não confirmado", exc_info=True)
            self._cancel_writer(writer)
            return 0

    def remove(self, doc_id: str) -> bool:
        """Remove documento pelo ID."""
        writer = None
        try:
            writer = self._ix.writer(timeout=_WRITE_TIMEOUT, delay=0.05)
            writer.delete_by_term("id", doc_id)
            writer.commit()
            self._stats["documents"] = max(0, self._stats["documents"] - 1)
            return True
        except Exception:
            _LOGGER.warning("Escrita Whoosh não confirmada", exc_info=True)
            self._cancel_writer(writer)
            return False

    # ─── Busca ────────────────────────────────────────────────

    def search(
        self,
        query_str: str,
        limit: int = 10,
        fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Busca documentos no índice.

        Args:
            query_str: termos de busca (ex: "trust engine spec")
            limit: max resultados
            fields: campos para buscar (padrão: title, content, tags)

        Returns:
            Lista de dicts com id, texto armazenado quando disponível e escopo da evidência
        """
        start = time.time()

        if not fields:
            fields = ["title", "content", "tags"]

        with self._ix.searcher() as searcher:
            parser = MultifieldParser(fields, self._schema, group=OrGroup)
            query = parser.parse(query_str)

            results = searcher.search(query, limit=limit)

            output = []
            for hit in results:
                content = hit.get("content", "")
                available = isinstance(content, str) and bool(content.strip())
                output.append(
                    {
                        "id": hit["id"],
                        "title": hit.get("title", ""),
                        "content": content if isinstance(content, str) else "",
                        "content_unavailable": not available,
                        "evidence_scope": "document_text" if available else "metadata",
                        "score": round(hit.score, 4),
                        "tags": hit.get("tags", ""),
                        "source": hit.get("source", ""),
                        "doctype": hit.get("doctype", ""),
                    }
                )

        elapsed = time.time() - start
        self._stats["queries"] += 1
        n = self._stats["queries"]
        self._stats["avg_ms"] = (self._stats["avg_ms"] * (n - 1) + elapsed * 1000) / n

        return output

    def search_by_tag(self, tag: str, limit: int = 20) -> list[dict[str, Any]]:
        """Busca documentos por tag exata."""
        with self._ix.searcher() as searcher:
            query = Term("tags", tag)
            results = searcher.search(query, limit=limit)
            return [
                {
                    "id": hit["id"],
                    "title": hit.get("title", ""),
                    "score": round(hit.score, 4),
                }
                for hit in results
            ]

    # ─── Utilitários ──────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
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
            _LOGGER.warning("Limpeza do índice Whoosh não concluída", exc_info=True)
            return False

    def __len__(self) -> int:
        return self._stats["documents"]


# Singleton padrão para uso no ecossistema
_default_engine: Whoosh3Engine | None = None


def get_engine() -> Whoosh3Engine:
    """Retorna instância singleton do motor Whoosh3."""
    global _default_engine
    with _CACHE_LOCK:
        if _default_engine is None:
            _default_engine = Whoosh3Engine("opencode_default")
        return _default_engine


# ─── Teste rápido ────────────────────────────────────────────

if __name__ == "__main__":
    eng = Whoosh3Engine("test")
    eng.index(
        {
            "id": "1",
            "title": "Trust Engine Spec",
            "content": "Cognitive guardrails and goal drift prevention",
            "tags": ["trust", "spec"],
            "source": "specs",
        }
    )
    eng.index(
        {
            "id": "2",
            "title": "Token Economy",
            "content": "Staking, slashing and fee market in OpenCode",
            "tags": ["economy", "token"],
            "source": "specs",
        }
    )

    results = eng.search("trust guardrails")
    print(f"Busca 'trust guardrails': {len(results)} resultados")
    for r in results:
        print(f"  [{r['score']}] {r['title']}")

    print(f"\nStats: {eng.stats()}")
