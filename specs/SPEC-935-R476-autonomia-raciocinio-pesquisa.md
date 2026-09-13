---
spec_id: SPEC-935-R476
title: Autonomia, raciocínio e pesquisa open science na fábrica de pesquisa (extensão do M1/R471)
component: research_factory (autonomy, reasoning, search)
test_file: tests/test_r476_autonomy_reasoning_search.py
status: green
estoque: rc
data: 2026-09-12
---

# SPEC-935-R476 — Autonomia, raciocínio e pesquisa open science na fábrica

## Objetivo
Estender a Research Factory (SPEC-935-R471, M1) com três capacidades que elevam score, autonomia, raciocínio e pesquisa do ecossistema:

1. **Autonomia (Reflexion)**: `AutonomyCore.self_supervise()` consulta lições do MetaBus (memória injetável) após uma execução, deriva plano de próximas ações e pontua acionabilidade; `rank_agents()` ordena despachos por trust score (Trust Engine) com `default_trust` para agentes sem histórico, ou ordem neutra.
2. **Raciocínio**: `PlanConsistencyChecker` valida planos (grafos acíclicos via DFS), estatísticas descritivas (n>=1, std>=0, média dentro de [min,max]) e prazos (monotonicidade não-decrescente); Z3/SymPy opcionais detectados em runtime, nunca obrigatórios (fallback determinístico).
3. **Pesquisa open science**: `OpenScienceSearchOrchestrator` com failover multi-provedor na ordem canônica OpenAlex → Crossref → EuropePMC → arXiv, recibo auditável por tentativa e bloqueio fail-closed de fontes fora da política (`open_science_only`).

## Não-objetivos
- Não usar rede, credenciais ou LLM real em testes; tudo é hermético e injetável.
- Não alterar `DEFAULT_SOURCES` nem a política open_science_only (invariante 1 da R471).
- Não depender de z3/sympy (opcionais; capacidades reportadas honestamente).
- Não promover mérito de topo ("superhuman", "verificado", "Qualis A1", "superação") em recibos/relatórios.

## Invariantes
1. `OPEN_SCIENCE_SOURCES` = {openalex, crossref, europepmc, arxiv}; nenhuma fonte restrita pertence ao conjunto; ordem canônica estável via lista.
2. Fonte fora da allowlist é bloqueada e **nunca executada** (fail-closed); allowlist nunca contém resolvedores restritos por padrão.
3. `self_supervise` sem lições retorna `actionable=0.0` e plano vazio; com lições, plano derivado automaticamente (max. 3 ações) e acionabilidade em [0,1].
4. `rank_agents(prefer_trust=False)` preserva ordem; com preferência, ordena por trust desc (default 0.5).
5. Verificadores de raciocínio são determinísticos; `reasoner` no relatório reflete o motor realmente usado ("dfs", "z3_hybrid", "sympy", "deterministic").
6. Recibo de busca registra `policy`, `permitted_sources`, `attempted`, `succeeded`, `failed`, `blocked`, `succeeded_source` e `records_count`; orquestrador sempre `marceloclaro`.
7. Nenhum componente toca rede, arquivos fora do controle da fábrica ou credenciais; fábrica novos atributos `autonomy`, `reasoning`, `search` e método `self_supervise` — sem quebrar os entrypoints R471.

## Critérios de aceitação
- CA1: `self_supervise` com lições ≥ 1 produz plano ≥ 1 ação e actionable ≥ 0.5; sem lições, actionable == 0.0 e plano vazio.
- CA2: `rank_agents` ordena por trust desc; desconhecidos usam default_trust; `prefer_trust=False` preserva ordem.
- CA3: Grafo acíclico validado; auto-ciclo e ciclos reais detectados (valid=False, cycles ≥ 1).
- CA4: Estatísticas válidas aprovadas; n≤0, std<0 e média fora de [min,max] rejeitadas.
- CA5: Prazos monotônicos aprovados; deadline regressiva rejeitada.
- CA6: Busca com failover registra tentativa falha, sucede na próxima fonte e retorna `succeeded_source` correto; registros agregados de múltiplas fontes.
- CA7: Busca com fonte fora da política bloqueia sem executar; `policy == "open_science_only"`.
- CA8: Fábrica expõe `autonomy`, `reasoning`, `search` e `self_supervise`; suíte R471 continua verde (sem regressão).
- CA9: Anti-overclaim em todos os recibos/relatórios (palavras banidas ausentes).
- CA10: Ciclo R476 registrado no EvolutionRegistry com score e lições; reflexão no MetaBus.

## Plano TDD
RED: `tests/test_r476_autonomy_reasoning_search.py` (23 testes) antes da implementação — falhou na coleta (módulos inexistentes). GREEN: `research_factory/autonomy.py`, `reasoning.py`, `search.py` + extensão de `research_factory/graph.py`; 23/23 verdes. VERIFY: regressões R471/R473/R475 e suíte crítica verdes; ciclo registrado.