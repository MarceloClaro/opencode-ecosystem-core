---
spec_id: SPEC-935-R1114
component: rag.evidence_ledger
title: RAG Evidence Ledger para proveniência de embeddings e perguntas
version: 1.0.0
status: implemented
test_file: tests/test_rag_evidence_ledger.py
---

# SPEC-935-R1114 — RAG Evidence Ledger

## Objetivo

Portar para `rag/evidence_ledger.py` três padrões auditáveis do `renumics-rag`: guarda de compatibilidade de embeddings, identificador estável de documento e log de perguntas com junção documentos↔perguntas.

## Motivação

O `renumics-rag` demonstra um RAG que registra a identidade do modelo de embeddings na metadata da coleção e persiste cada pergunta/resposta como documento, permitindo calcular quais trechos foram usados por quais perguntas. O Core precisa desse substrato de proveniência sem adotar a stack LangChain/Streamlit nem o monkeypatch global de `sqlite3`.

## Escopo

### Em escopo
- Módulo `rag/evidence_ledger.py` apenas com biblioteca padrão.
- `EmbeddingModelMismatch`, `collection_metadata`, `assert_embedding_compatible`.
- `stable_document_id`, `QuestionRecord`, `question_record_to_document`.
- `join_documents_questions` com `used_by_questions` e `used_by_num_questions`.
- Exportação em `rag/__init__.py`.
- Testes em `tests/test_rag_evidence_ledger.py`.

### Fora de escopo
- Instalar ChromaDB, LangChain ou Spotlight.
- Alterar `rag/scientific.py` ou o comportamento do RAG científico existente.
- Declarar avaliação de qualidade ou causalidade.

## Requisitos

1. A guarda compara `model_name` e `model_type`; metadata ausente não bloqueia.
2. `openai` e `azure` com o mesmo nome são equivalentes; tipos diferentes com mesmo nome não são.
3. `stable_document_id` é determinístico e insensível à ordem das chaves.
4. `question_record_to_document` serializa `sources` de forma estável.
5. `join_documents_questions` preserva documentos sem uso e calcula contagens inteiras.
6. Entradas vazias ou fontes desconhecidas não lançam exceção.
7. Nenhuma dependência externa é importada.

## Critérios de aceitação

- [ ] Teste de mismatch de nome lança `EmbeddingModelMismatch`.
- [ ] Teste de equivalência openai/azure passa.
- [ ] Teste de tipo diferente lança.
- [ ] IDs iguais para metadata equivalente; diferentes para metadata distinta.
- [ ] Join calcula 2 usos para o mesmo documento em 2 perguntas.
- [ ] Documento sem uso tem lista vazia e contagem 0.
- [ ] `tests/test_rag_evidence_ledger.py` passa.

## Plano de testes

```bash
.venv/bin/python -m pytest tests/test_rag_evidence_ledger.py -q
```

Ciclo TDD: teste escrito antes do módulo; RED por `ModuleNotFoundError`; implementação; GREEN.

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Duplicar responsabilidade do RAG científico | Módulo isolado; nenhuma alteração em `rag/scientific.py` |
| Guarda bloquear coleção legítima | Metadata ausente é no-op; equivalência openai/azure explícita |
| Join O(n·m) em corpora grandes | Documentado; uso previsto para lotes de avaliação, não para produção massiva |
| Confundir contagem de uso com relevância | O campo mede uso observado, não qualidade; documentado no docstring |

## Evidência

- Fonte: `renumics-rag`, commit `c504659d35eab001acbeed1eb17b5dccb0b4fa7a`, MIT.
- Arquivos de origem: `assistant/__init__.py` (guarda), `assistant/exploration.py` (join), `assistant/cli/create_db.py` (hash).
