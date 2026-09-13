---
spec_id: SPEC-935-R478
title: Fase 2 da R471 — sandbox científico declarativo (M2) e roteador local de inferência PAIR (M3)
component: sandbox (declarative_policy), research_factory (pair_router), doctor
test_file: tests/test_r478_sandbox_pair.py
status: green
estoque: rc
data: 2026-09-13
---

# SPEC-935-R478 — Fase 2: sandbox científico declarativo e roteador PAIR

## Objetivo
Executar a Fase 2 do roadmap da SPEC-935-R471:

1. **M2 — Sandbox científico declarativo (OpenShell + NemoClaw)**: template de política YAML adaptado ao modelo de 4 camadas do OpenShell (filesystem, network, process, providers) para tarefas de pesquisa — coleta de dados, scraping bibliográfico e execução de código estatístico — com allowlist de endpoints bibliográficos, negação padrão de egresso e credenciais endpoint-bound.
2. **M3 — Roteador local de inferência (PAIR)**: conector que expõe endpoints PAIR (Personal-AI-Router, NVIDIA; Ollama-compatible/OpenAI-compatible) como provedor adicional do doctor e do roteamento de inferência; prioridade local → PAIR → Ollama → OpenAI, com fallback transparente.

## Não-objetivos
- Não fazer chamadas de rede reais, download ou scraping em testes (hermético; readiness injetável, CA8 da R471).
- Não expor ou persistir credenciais: status PAIR reporta apenas definido/ausente (padrão R128); recibos jamais contêm valor de chave (invariante 5).
- Não alterar `open_science_only`, `DEFAULT_SOURCES` nem a política fail-closed do resolvedor restrito (invariantes 1/3).
- Não aprovar despacho com `shell=True` ou interpolação de shell (invariante 4).
- Não declarar "superação"/"verificado"/"Qualis A1" sem validação externa (invariante 8).

## Invariantes
1. Egresso padrão de rede é `deny`; apenas endpoints bibliográficos da allowlist (`openalex.org`, `api.crossref.org`, `europepmc.org`, `export.arxiv.org`, etc.) passam.
2. Ausência de política ou de match ⇒ negação com recibo (fail-closed), em todas as 4 camadas.
3. Shell interativo (`sh/bash/zsh/...` com `-c`), metacaracteres (`;`, `&&`, `||`, `|`) e interpolação (`$(`/`${`) são negados em `check_process`.
4. Providers fora da allowlist são negados; credencial/hint nunca aparece em recibo.
5. PAIR é opt-in: sem `PAIR_BASE_URL`/`PAIR_ENDPOINTS` o provedor está inativo e o roteamento degrada para local → Ollama → OpenAI sem exceção.
6. `pair_provider_status()` jamais expõe host, porta ou valor de credencial; doctor reporta "definido/ausente" apenas.
7. Nenhuma chamada de rede parte do módulo PAIR; readiness é injetada por funções (`local_ready`, `pair_ready`, `ollama_ready`, `openai_ready`).

## Critérios de aceitação
- CA3': egresso bibliográfico autorizado produz `PolicyDecision(allowed=True, layer="network")`; egresso não autorizado produz recibo de negação com `allowed=False` e motivo.
- CA4': sem PAIR configurado, `PairRouter.resolve()` seleciona local/ollama/openai com `fallback_used=True`; com PAIR configurado e pronto, seleciona `pair` após `local`; `DEFAULT_ROUTE_PRIORITY == ("local","pair","ollama","openai")`.
- CA8': 25 testes herméticos sem rede/credenciais reais.
- CA9': doctor permanece pass/warn apenas (novo branch "PAIR definido" sem expor valor).
- CA10: nenhum relatório deste ciclo contém "superhuman"/"verificado"/"Qualis A1"/"superação".
- CA11: ciclo R478 registrado no EvolutionRegistry com score e lições; reflexão no MetaBus.

## Plano TDD
RED: 25 testes em `tests/test_r478_sandbox_pair.py` antes da implementação — falharam na coleta (`ModuleNotFoundError: No module named 'sandbox'`); PAIR sem readiness fora da allowlist também falhou (1 teste ajustado para o vocabulário correto "definido"). GREEN: `sandbox/declarative_policy.py` (M2: template YAML 4 camadas + receitas de decisão), `research_factory/pair_router.py` (M3: `PairRouter`, `pair_configured`, `pair_provider_status`), integração `doctor.py::_check_llm_providers` (branch PAIR). VERIFY: 25/25 verdes; suíte completa; doctor; ciclo registrado.