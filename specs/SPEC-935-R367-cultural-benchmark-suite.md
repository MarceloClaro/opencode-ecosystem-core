---
spec_id: SPEC-935-R367
title: Suíte de benchmark cultural medido (corpus interno rotulado)
component: scripts/benchmark_r367_cultural.py + validacao_externa/cultural_episteme/benchmark_corpus_r367.json
status: verified
test_file: tests/test_r367_cultural_benchmark.py
---

# SPEC-935-R367 — Benchmark Cultural Medido

**Data:** 2026-08-02
**Motivação:** o plano de negócios OpenCode Books Global anuncia
"consistência simbólica ≥ 98%" sem medição. A política do CORRIGENDUM proíbe
anunciar métrica não medida. Este ciclo cria a primeira medição real — em
corpus interno rotulado — dos três guardas de tradução (R364/R365/R366),
para que qualquer número usado comercialmente seja **descritivo e datado**,
nunca meta inventada.

## 1. Objetivo

1. Corpus rotulado (`benchmark_corpus_r367.json`): casos com códigos
   esperados por módulo (`terminology`, `voice`, `backtranslation`),
   incluindo **casos difíceis que as regras atuais sabidamente não detectam**
   — o benchmark deve poder mostrar recall < 100%.
2. Runner determinístico (`scripts/benchmark_r367_cultural.py`):
   `run_benchmark(corpus_path)` executa os módulos reais, calcula
   precisão/recall/F1 por código e totais, e grava
   `validacao_externa/cultural_episteme/benchmark_r367_report.{json,md}`.
3. Enquadramento honesto obrigatório no relatório: `measured: true`,
   `claim: internal-fixture-benchmark`, tamanho do corpus, data, e
   disclaimer de que números em corpus interno pequeno **não** constituem
   validação externa nem promessa de desempenho.

## 2. Contratos

- Corpus: `schema_version`, `claim`, `cases[]` com `case_id` único,
  `module`, `input`, `expected_codes` (lista possivelmente vazia) e
  `note` opcional. Corpus mínimo: 18 casos, ≥ 4 por módulo, ≥ 3 casos
  negativos (sem código esperado) e ≥ 2 casos de limitação conhecida.
- Fixtures de apoio (grafo aprovado e perfil de voz) vivem no runner e são
  determinísticos.
- Métricas: TP/FP/FN por código; precisão/recall/F1 com `None` quando
  denominador zero; agregado micro.
- Proibição textual: o relatório não pode conter promessa de meta
  ("98%", "garantimos", "superhuman").

## 3. Critérios de aceitação

1. Corpus válido pelo schema acima; case_ids únicos.
2. `run_benchmark` é determinístico (duas execuções, mesmo resultado).
3. Relatório contém enquadramento honesto (§1.3) e métricas em [0,1].
4. O recall global é < 1.0 no corpus atual (prova de que o benchmark
   captura limitações reais, não é vitrine).
5. Relatório `.json` e `.md` gerados e versionados; teste garante que o
   relatório versionado corresponde à execução atual do código.
6. Nenhuma string de meta proibida no relatório.
