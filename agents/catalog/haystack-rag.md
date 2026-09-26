# Haystack RAG Specialist

- **ID**: haystack-rag
- **Nome**: Especialista em RAG e pipelines Haystack (SPEC-935-R604)
- **Categoria**: Biblioteca/Integração · **Família**: M7 (pacote importável)

## Descrição

Integração do framework Haystack (deepset-ai/haystack, Apache-2.0) ao
ecossistema: verificação de disponibilidade/versão (`haystack-ai` via PyPI),
construção de pipeline RAG mínimo (InMemoryDocumentStore +
SentenceTransformers Document/Text Embedder + InMemoryEmbeddingRetriever) e
health check tolerante — sem exigir instalação para a suíte passar.

## Capacidades

- `available` / `version` — detecta pacote e semver (importlib).
- `build_rag_pipeline` — indexa documentos e monta pipeline de retrieva
  (embedding local, sem API key).
- `run_retrieval` — executar retrieva para uma query; nunca lança.
- `doctor_check` — pass/warn (nunca fail), simétrico aos demais M7.
- CLI `/haystack status|doctor|install`.

## Uso

```bash
python3 -m integrations.haystack_cli status   # disponibilidade/versão
python3 -m integrations.haystack_cli doctor   # health check
python3 -m integrations.haystack_cli install  # instruções pip + LLM provider
```

Instalação real (opcional, fora do CI):

```bash
pip install haystack-ai
```

## Limites de uso (anti-overclaim)

- NÃO é CLI executável no PATH — não entra em `EXTERNAL_CLIS` do doctor.
- Pipeline construído faz **indexação/retrieva**; **geração (LLM) exige
  provedor explícito** (OpenAI/Anthropic/HF/local) — a integração nunca
  inventa provider default, nem promete RAG completo sem chave.
- Health check com o pacote ausente é `warn`, nunca `fail`.
- Ver `specs/SPEC-935-R604-haystack.md` para detalhes e limites.

## Verificação

```bash
python3 -m pytest tests/test_r604_haystack.py -q   # 22 passed (1 skipped)
```