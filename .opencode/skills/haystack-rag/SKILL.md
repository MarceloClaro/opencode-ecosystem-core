---
name: haystack-rag
description: >
  Integração do framework Haystack (deepset-ai/haystack, Apache-2.0) como
  componente orquestrável de RAG (SPEC-935-R604). Use para verificar
  disponibilidade/versão do haystack-ai, construir pipeline RAG mínimo
  (DocumentStore + SentenceTransformers + Retriever) via
  integrations.haystack_cli, executar retrieva sobre documentos e checar saúde
  (`/haystack status`, `/haystack doctor`, `/haystack install`). NÃO substitui
  o orquestrador marceloclaro: geração com LLM exige provedor explícito e o
  ciclo SDD/TDD permanece sob controle do Core. Não usar para pipelines RAG
  que exijam API key sem instrução explícita do operador.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R604
spec: SPEC-935-R604-haystack.md
---

# Skill: Haystack RAG (SPEC-935-R604)

Framework Python open-source para pipelines de RAG/agentes em produção.
Pacote importável (`pip install haystack-ai`) — NÃO é CLI no PATH; não entra
no `EXTERNAL_CLIS` do doctor (20 checks preservados).

## Comandos

| Comando | Ação |
|---|---|
| `/haystack status` | Pacote instalado? versão semver (importlib.metadata) |
| `/haystack doctor` | Health check: import + Pipeline smoke — pass/warn |
| `/haystack install` | Instruções pip + escolha de provedor LLM |
| `/haystack --help` | Uso completo |

## Uso programático

```python
from integrations.haystack_cli import (
    haystack_available, haystack_version,
    build_rag_pipeline, run_retrieval, doctor_check,
)

if not haystack_available():
    print(install_instructions())
else:
    build = build_rag_pipeline(
        [{"content": "texto", "meta": {"fonte": "x"}}],
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        top_k=3,
    )
    if build["ok"]:
        ret = run_retrieval(build["pipeline"], "pergunta")
        print(ret["count"], [d["content"] for d in ret["documents"]])
```

## Instalação (opcional, fora do CI)

```bash
pip install haystack-ai          # Apache-2.0, Python >= 3.10
# embedding local por padrão — sem chave de API
# geração (LLM) exige provedor: OPENAI_API_KEY, Anthropic, HF, local...
```

## Regras

- Nunca declarar pipeline RAG completo (geração) sem provedor explícito;
  a integração cobre indexação + retrieva com embedding local.
- Com o pacote ausente, todos os caminhos retornam warn/ok=False — nunca
  lançam exceção na orquestração (padrão M7).
- Resultados nunca são "verificados" sem validação do Core (anti-overclaim R110).
- Telemetria do Haystack desabilitável via `HAYSTACK_TELEMETRY_ENABLED=False`
  quando a instalação real for usada.