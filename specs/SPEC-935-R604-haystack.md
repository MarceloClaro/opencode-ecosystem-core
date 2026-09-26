# SPEC-935-R604 — Integração Haystack (deepset-ai/haystack, Apache-2.0)

**Round:** R604 · **Data:** 2026-09-26 · **Estado:** Implementado e verde

## Objetivo

Expor o framework Haystack (deepset-ai/haystack) como componente orquestrável
no ecossistema — disponibilidade, versão, pipeline RAG mínimo (DocumentStore +
Embedders + Retriever) e health check — sem exigir que o pacote esteja
instalado para a suíte passar (padrão M7: import opcional, testes com mocks).

## Contexto

Haystack é um framework Python open-source (Apache-2.0) para aplicações LLM
em produção: pipelines modulares de RAG, agents, memória, roteamento e
geração. Ao contrário dos executores externos M7 recentes (goose, plandex,
reasonix, gemini-cli — CLIs no PATH), **Haystack não é CLI executável**; é
pacote importável (`pip install haystack-ai`). Portanto NÃO entra na lista
`EXTERNAL_CLIS` do doctor global (que permanece com 20 checks — contratos
R448/R449/R455 intactos), mas recebe `doctor_check` próprio no módulo.

## Mudanças

- `integrations/haystack_cli.py` (novo):
  - `haystack_available()` — `importlib.util.find_spec("haystack_ai")`, com
    cache de ausência (nunca re-consulta em loop).
  - `haystack_version()` — `importlib.metadata.version("haystack-ai")`
    (semver), tolerante (None se ausente/erro), com cache.
  - `_import_haystack()` / `_import_components()` — pontos únicos de import
    (facilitam mock M7 sem sys.modules fake).
  - `build_rag_pipeline(documents, embedding_model, top_k)` — pipeline RAG
    mínimo: InMemoryDocumentStore + SentenceTransformersDocumentEmbedder +
    InMemoryEmbeddingRetriever + SentenceTransformersTextEmbedder; indexa
    documentos e retorna dict ok=True com pipeline pronto para retrieva;
    **sem chave de API por padrão** (embedding local); passo de geração
    (LLM) fica explícito como pendente (exige provedor).
  - `run_retrieval(pipeline, query)` — executa retrieva; dict ok/documents/
    count; valida query vazia e pipeline ausente; nunca lança.
  - `doctor_check()` — pass se pipeline instancia; warn (nunca fail) se
    ausente — simétrico aos demais M7.
  - CLI `main()`: `status`, `doctor`, `install` (comando `/haystack`).
- `tests/test_r604_haystack.py` (novo): 22 testes (disponibilidade/versão,
  build com mock, entrada vazia, retrieva, doctor, CLI, smoke opcional se
  instalado) — **22 passed, 1 skipped** sem o pacote instalado.
- Agent Card `agents/catalog/haystack-rag.md`.
- Skill `.opencode/skills/haystack-rag/SKILL.md`.

Não alterado: `marceloclaro/doctor.py` (Haystack não é CLI PATH), contratos
R448/R449/R455 (20 checks / 7 MCPs / 215 agentes permanecem). Contrato
R380 atualizado para catálogo **212** (novo card haystack-rag.md) —
`integrations.opencode_cli` regenerou opencode.json com **216 agentes**,
7 MCPs e 14 comandos (215 delegações + haystack-rag).

## Critérios de aceitação

1. `python3 -m pytest tests/test_r604_haystack.py -q` → 22 passed (1 skipped).
2. `python3 -m integrations.haystack_cli status` → exit 0 (ou 1 com
   instruções quando ausente; nunca lança).
3. `marceloclaro/doctor.py::_check_external_clis` inalterado → 20 checks.
4. Suíte completa verde com os novos testes.

## Resultado observado

- `tests/test_r604_haystack.py`: **22 passed, 1 skipped** em ~0,2s.
- Suíte completa (R603 fechado): **4527 passed, 80 skipped, 0 failed**.
- Pesquisa fonte: README oficial (deepset-ai/haystack) salvo em
  `/tmp/opencode/haystack_readme.md`; versão alvo `haystack-ai` (PyPI),
  Apache-2.0, Python ≥ 3.10.

## Lições

- Framework Python orquestrável ≠ CLI executável: a família M7 precisa de
  dois padrões — CLIs no PATH (EXTERNAL_CLIS do doctor) e pacotes importáveis
  (doctor_check interno, nunca fail). Misturar os dois inflaria checks e
  quebraria contratos de contagem.
- Import único via `_import_*` facilita mock (evita sys.modules fake frágil).
- Embedding local por padrão (SentenceTransformers) permite pipeline RAG
  functional sem chave de API; geração exige provedor explícito — nunca
  inventar provider default (anti-overclaim).