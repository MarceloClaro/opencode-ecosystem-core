---
spec_id: SPEC-935-R368
title: Cobertura epistêmica do catálogo — léxico pt ampliado + check no doctor
component: transformer/episteme.py + marceloclaro/doctor.py
status: verified
test_file: tests/test_r368_episteme_coverage.py
---

# SPEC-935-R368 — Cobertura Epistêmica do Catálogo

**Data:** 2026-08-02
**Motivação:** medição da reavaliação de gaps: 139/205 agentes (68%) ficam
sem episteme porque o léxico do R363 não cobre os nomes em português do
catálogo legado (`resultados`, `revisao`, `consistencia`, `resumo`...). A
camada epistêmica só roteia o que consegue classificar; cobertura baixa
significa peso brando inerte para 2/3 do catálogo.

## 1. Objetivo

1. **Ampliar o léxico** dos 6 regimes com sinais pt/en presentes no catálogo
   real, mantendo a disciplina "nunca chutar" (só palavras com regime claro;
   termos ambíguos como `escopo`, `busca`, `diagnostico` ficam de fora).
2. **Invariante estrutural nova:** sinais disjuntos entre regimes (nenhuma
   palavra em dois léxicos) — verificada por teste.
3. **Check `episteme_coverage` no doctor:** mede a cobertura real do catálogo
   (explícita + inferida) e reporta números medidos; `warn` abaixo de 50%,
   `pass` acima, `fail` em erro de carga. O detalhe cita contagens, nunca
   metas fabricadas.
4. `transformer/episteme.py` ganha `catalog_episteme_coverage(definitions)`
   — função pura sobre definições já carregadas (testável sem I/O).

## 2. Sinais adicionados (curadoria)

- `empirico_analitico`: resultados, evidencia(s), visualizacao, datamining,
  mining, learning, ml, dl.
- `hermeneutico_interpretativo`: resumo, abstract, escrita, redacao, textual.
- `critico_reflexivo`: editor, editorial, revisao, consistencia, coerencia,
  qualidade, argumentativa, argumentacao.
- `pragmatico_tecnico`: docx, latex, framework, ambientes, workflow.
- `regulatorio_normativo`: normalizacao, padronizacao, diretrizes.

**Segunda rodada (após medição de 41%):** domínios inteiros do catálogo sem
sinais — medicina clínica, bioinformática/ômicas, visão computacional, GIS,
engenharia/dev (cloud, git, debug, codebase...), KDP/preflight, jurídico
(auxjuris) e sumarização/copywriting — receberam sinais curados nos regimes
correspondentes. Termos ambíguos (`escopo`, `busca`, `diagnostico`,
`apresentacao`, `montagem`) permanecem deliberadamente fora.

**Cobertura medida após as duas rodadas (2026-08-02):** 133/205 agentes
(65%): 3 explícitas, 130 inferidas, 72 sem sinais. Número descritivo do
catálogo desta data, reportado pelo doctor — não é meta nem promessa.

## 3. Critérios de aceitação

1. Agentes legados representativos passam a ser classificados:
   `09_agente_resultados` → empírico; `14_agente_consistencia_interna` →
   crítico; `15_agente_resumo_abstract_palavras_chave` → hermenêutico;
   `16_agente_integracao_editorial_docx` → pragmático;
   `22_agente_ml_dl_datamining` → empírico.
2. Sinais disjuntos entre regimes (invariante testada).
3. Cobertura medida no catálogo real ≥ 50% (piso conservador; o valor real
   observado é reportado pelo doctor, não anunciado como meta).
4. "Nunca chuta" preservado: texto sem sinais → `None` (regressão R363 verde).
5. Doctor inclui `episteme_coverage` com contagens medidas no detail.
6. Suíte dos ciclos R363–R368 verde.
