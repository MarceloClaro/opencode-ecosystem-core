# SPEC-919: Scientific RAG — Grounding, Citações, Reranking e Avaliação

**STATUS**: IMPLEMENTADO  
**DATA**: 2026-07-08  
**AUTOR**: marceloclaro  
**VERSÃO**: 1.0

## 1. Objetivo

Adicionar um módulo RAG científico de primeira classe ao ecossistema para que respostas, avaliações e relatórios científicos sejam **ancorados em evidências recuperáveis**, com citações, reranking e métricas de grounding.

## 2. Diagnóstico

O ecossistema possui:

- memória vetorial simplificada em `transformer/memory.py`;
- agentes/documentação GraphRAG;
- pipeline acadêmico MASWOS;
- benchmarks científicos.

Mas não há ainda um módulo canônico, testável e sem dependências pesadas para:

- indexar documentos científicos;
- recuperar trechos relevantes;
- reranquear por evidência;
- gerar citações auditáveis;
- medir groundedness, citation coverage e abstention.

## 3. Escopo

Criar pacote `rag/` com:

```text
rag/
├── __init__.py
└── scientific.py
```

Componentes:

- `ScientificDocument` — documento com `doc_id`, título, ano, autores, fonte e texto.
- `RetrievedEvidence` — trecho recuperado com score lexical, semântico, final e citação.
- `ScientificRAG` — indexação, chunking, busca híbrida e reranking.
- `GroundingEvaluator` — métricas de grounding e cobertura de citações.

## 4. Estratégia RAG

Sem dependências pesadas por padrão:

1. **Chunking determinístico** por frases/janelas.
2. **Lexical score** via overlap TF simplificado.
3. **Semantic-lite score** via normalização, stemming leve e sinônimos científicos mínimos.
4. **Hybrid score** = 0.6 lexical + 0.4 semantic-lite.
5. **Reranking científico** com bônus para:
   - termos de método (`randomização`, `p-valor`, `confounder`, `power`, `replicação`);
   - ano/fonte/autores presentes;
   - evidência direta vs. especulação.
6. **Abstenção** se top score < threshold.

## 5. Critérios de Aceitação

- [x] Indexa documentos científicos com metadados.
- [x] Divide documentos em chunks citáveis.
- [x] Recupera top-k evidências relevantes para consulta.
- [x] Gera citação auditável `Autor (Ano), doc_id:chunk_id`.
- [x] Retorna resposta grounded com lista de evidências.
- [x] Abstem quando não há evidência suficiente.
- [x] Calcula `groundedness`, `citation_coverage`, `abstention` e `evidence_count`.
- [x] Integra com a SPEC-918 como métrica de grounding.
- [x] Testes TDD cobrem recuperação, citação, abstenção e avaliação.

## 6. Política de Segurança Epistêmica

O RAG deve preferir **não responder** a inventar evidências. Qualquer resposta sem evidência suficiente deve retornar `abstained=True` e explicar a ausência de grounding.

## 7. Validação TDD

```bash
pytest tests/test_scientific_rag_superhuman.py -q
# 8 passed
```

O RAG implementado é leve e determinístico: busca híbrida lexical + semantic-lite, reranking científico, citações e abstenção conservadora.
