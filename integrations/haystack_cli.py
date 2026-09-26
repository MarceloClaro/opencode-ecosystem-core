# -*- coding: utf-8 -*-
"""Integração Haystack (deepset-ai/haystack) — SPEC-935-R604.

Haystack é um framework Python open-source (Apache-2.0) para pipelines de RAG
e agentes em produção: `pip install haystack-ai`. Não é um CLI executável —
a integração assina como *pacote importável e orquestrável*: disponibilidade,
versão (importlib.metadata), dicas de construção de pipeline RAG (DocumentStore
+ Retriever + Generator) e health check tolerante.

Nunca lança exceções no caminho de orquestração; falhas viram dicts com ok=False.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Any, Dict, List, Optional

_PKG_NAME = "haystack_ai"
_DIST_NAME = "haystack-ai"
_AVAILABLE_CACHE: Optional[bool] = None
_VERSION_CACHE: Optional[str] = None


def _installed() -> bool:
    """True se haystack_ai está instalado (importável) no ambiente atual."""
    global _AVAILABLE_CACHE
    if _AVAILABLE_CACHE is not None:
        return _AVAILABLE_CACHE
    try:
        _AVAILABLE_CACHE = importlib.util.find_spec(_PKG_NAME) is not None
    except (ImportError, ValueError):
        _AVAILABLE_CACHE = False
    return _AVAILABLE_CACHE


def haystack_available() -> bool:
    return _installed()


def haystack_version() -> Optional[str]:
    """Versão semver do haystack-ai via importlib.metadata (tolerante)."""
    global _VERSION_CACHE
    if _VERSION_CACHE is not None:
        return _VERSION_CACHE or None
    if not _installed():
        _VERSION_CACHE = ""
        return None
    try:
        from importlib import metadata  # Python >= 3.8

        versao = metadata.version(_DIST_NAME)
        if versao:
            _VERSION_CACHE = versao
            return versao
    except Exception:  # noqa: BLE001
        pass
    _VERSION_CACHE = ""
    return None


def _import_haystack():
    """Importa o pacote haystack_ai ou levanta ImportError com mensagem clara."""
    try:
        import haystack_ai  # noqa: F401
        from haystack import Pipeline, Document  # noqa: F401
        return Pipeline, Document
    except ImportError:
        raise ImportError(
            "haystack_ai não está instalado. Rode `pip install haystack-ai` "
            "(detalhes: haystack_rag.install_instructions())."
        ) from None


def _import_components():
    """Importa os componentes Haystack usados no pipeline RAG mínimo.

    Separado de _import_haystack para que testes possam mockar um único ponto
    sem depender de sys.modules fake (estratégia M7).
    """
    from haystack.document_stores.in_memory import InMemoryDocumentStore
    from haystack.components.retrievers.in_memory import (
        InMemoryEmbeddingRetriever,
    )
    from haystack.components.embedders import (
        SentenceTransformersDocumentEmbedder,
    )
    from haystack.components.embedders import (
        SentenceTransformersTextEmbedder,
    )

    return {
        "store": InMemoryDocumentStore,
        "retriever": InMemoryEmbeddingRetriever,
        "doc_embedder": SentenceTransformersDocumentEmbedder,
        "text_embedder": SentenceTransformersTextEmbedder,
    }


def build_rag_pipeline(
    documents: List[Dict[str, str]],
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 3,
) -> dict:
    """Constrói um pipeline RAG mínimo (InMemoryDocumentStore + Retriever).

    Retorna dict com ok, pipeline (se ok) ou mensagem de erro. O pipeline
    concreto usa apenas componentes da própria Haystack (sem chave de API):
    - InMemoryDocumentStore + EmbeddingRetriever
    - O passo de geração (LLM/Generator) fica a cargo do usuário, porque exige
      provedor (OpenAI, Anthropic, HF, local...) — documentado na spec.

    Em ambientes sem haystack_ai, retorna ok=False SEM lançar exceção
    (padrão M7: orquestração nunca explode).
    """
    if not _installed():
        return {
            "ok": False,
            "pipeline": None,
            "error": "haystack_ai não instalado",
            "install": install_instructions(),
        }
    try:
        Pipeline, Document = _import_haystack()
        comp = _import_components()
        store = comp["store"]()

        docs = []
        for item in documents:
            content = item.get("content", "")
            if not isinstance(content, str) or not content.strip():
                continue
            meta = dict(item.get("meta") or {})
            doc = Document(content=content, meta=meta)
            # Embedding do documento (modelo local por padrão; sem API key)
            docs.append(doc)

        # Pipeline: embed(docs) -> store -> retriever(top_k)
        pipe = Pipeline()
        doc_embedder = comp["doc_embedder"](model=embedding_model)
        retriever = comp["retriever"](
            document_store=store, top_k=top_k
        )
        text_embedder = comp["text_embedder"](model=embedding_model)
        pipe.add_component("doc_embedder", doc_embedder)
        pipe.add_component("retriever", retriever)
        pipe.add_component("text_embedder", text_embedder)
        pipe.connect("doc_embedder.documents", "retriever.documents")

        if docs:
            embedded = doc_embedder.run({"documents": docs})
            store.write_documents(embedded["documents"])

        return {
            "ok": True,
            "pipeline": pipe,
            "documents_indexed": len(docs),
            "top_k": top_k,
            "components": ["doc_embedder", "retriever", "text_embedder"],
            "generator_pending": "LLM de geração exige provedor explícito",
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "pipeline": None, "error": str(exc)}


def run_retrieval(pipeline: Any, query: str) -> dict:
    """Executa a etapa de retrieva de um pipeline Haystack para uma query.

    Retorna dict com ok, documents (lista de {content, score}) ou erro.
    Se o pipeline não for um Pipeline Haystack (ou query vazia), ok=False.
    """
    if not query or not query.strip():
        return {"ok": False, "documents": [], "error": "query vazia"}
    if pipeline is None:
        return {"ok": False, "documents": [], "error": "pipeline ausente"}
    try:
        # Pipeline.connect já expõe 'text_embedder' e 'retriever'
        result = pipeline.run(
            {"text_embedder": {"text": query.strip()}}
        )
        retrieved = result.get("retriever", {}).get("documents", [])
        docs = [
            {
                "content": getattr(d, "content", ""),
                "score": getattr(d, "score", None),
                "meta": getattr(d, "meta", {}),
            }
            for d in retrieved
        ]
        return {"ok": True, "documents": docs, "count": len(docs)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "documents": [], "error": str(exc)}


def doctor_check() -> dict:
    """Health check estilo doctor global: pass/warn (nunca fail)."""
    if not _installed():
        return {
            "name": "haystack",
            "status": "warn",
            "detail": "não instalado — pip install haystack-ai",
        }
    versao = haystack_version() or "desconhecida"
    try:
        Pipeline, _ = _import_haystack()
        # Smoke: Pipeline vazio instancia sem problemas
        _ = Pipeline()
        return {
            "name": "haystack",
            "status": "pass",
            "detail": f"v{versao} — Pipeline ok",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "name": "haystack",
            "status": "warn",
            "detail": f"v{versao} — erro ao instanciar Pipeline: {exc}",
        }


def install_instructions() -> str:
    return (
        "Instalação Haystack (deepset-ai/haystack, Apache-2.0):\n"
        "  1. pip install haystack-ai            # framework Python (não CLI)\n"
        "  2. python -c \"import haystack; print(haystack.__version__)\"\n"
        "  3. Geradores (LLM) exigem provedor:\n"
        "     - OpenAI:   HAYSTACK_TELEMETRY_ENABLED=False + OPENAI_API_KEY\n"
        "     - Anthropic/Cohere/HF/Bedrock/local: componentes no cookbook\n"
        "     https://haystack.deepset.ai/cookbook\n"
        "Requisitos: Python >= 3.10 (instalado). License Apache-2.0.\n"
    )


# ---------------------------------------------------------------------------
# CLI orquestrada (comando /haystack)
# ---------------------------------------------------------------------------

_USO = """\
Uso: python -m integrations.haystack_cli SUBCOMANDO [OPCOES]

Subcomandos:
  status          Pacote, versão e disponibilidade
  doctor          Health check (import, Pipeline smoke)
  install         Instruções de instalação (pip + provedor LLM)
  --help          Esta ajuda

Exemplos:
  python -m integrations.haystack_cli status
  python -m integrations.haystack_cli doctor
"""


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] in ("--help", "-h"):
        print(_USO)
        return 0

    sub = argv[0]
    if sub == "status":
        if not _installed():
            print("haystack: NÃO INSTALADO (framework Python; pip install haystack-ai)")
            print(install_instructions())
            return 1
        print(f"haystack: disponível  pacote={_PKG_NAME}")
        print(f"haystack: versão      {haystack_version() or 'desconhecida'}")
        return 0

    if sub == "install":
        print(install_instructions())
        return 0

    if sub == "doctor":
        check = doctor_check()
        print(f"{check['name']}: {check['status']} — {check['detail']}")
        return 0 if check["status"] == "pass" else 1

    print(f"Erro: subcomando desconhecido: {sub}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())