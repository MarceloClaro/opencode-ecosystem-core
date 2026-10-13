---
spec_id: SPEC-935-R832
title: Realidade para os 36 restantes — agentes, mci, evolução, protocolos, integrações, infra e governança
status: proposed
component: agents/ + mci/ + evolution/ + protocolos/ + integrations/ + infra_dados/ + governanca/
test_file: tests/test_r832_restantes_36.py
---

# R832 — Inventário, contratos de entrada e comportamentos delimitados

Origem histórica: R830 elevou a autodescoberta lexical do próprio repositório
a 100% via correção do instrumento e inclusão de fachadas. Isso não demonstra
cobertura funcional, qualidade epistêmica ou completude.
Auditoria honesta: 12/48 com implementação nova real; 36/48 cobertos porque
o conteúdo já existia mas não era contado. Este ciclo dá realidade aos 36.

## Mapa exato dos 36 (dimensão → ausentes → destino)

- `agentes (5)` → `agents/`: `bernstein_orchestrator, antigravity_orchestrator, reversa_agents, ws_agents, agent_catalog`. Existentes cobertos: orchestrator, coder, researcher, auditor, academic_writer.
- `mci_core (3)` → `mci/`: `context_manager, memory_updater, orchestration_pipeline`. Cobertos: metabus, blackboard, reflexion, transformer, graph_builder, mcp_server.
- `evolucao (4)` → `evolution/`: `cycles_manager, reflection_ledger, autoevolve_pipeline, evolutionary_roadmap`. Cobertos: evolution_registry, trajectory_mapper, successor_generator.
- `protocolos (8)` → `protocolos/` (novo, entra em `core_dirs`): `sdd_spec_first, tdd_red_green_refactor, a2a_blackboard, mcp_interconnect, bernstein_orchestration, sdd_gate, behavioral_gate, reflexion_middleware`. Hoje 8/8 por keyword genérico; este ciclo cria protocolo executável por categoria.
- `integracoes (6)` → `integrations/`: `antigravity_bridge, cli_integrations, pypi_searcher, web_search, mcp_servers, git_manager`. Coberto: webfetch.
- `infra_dados (5)` → `infra_dados/` (novo, entra em `core_dirs`): `schemas_validator, data_pipeline, batch_executor, assets_media, gametheory_models`. Cobertos: benchmarks, notebooks, installer.
- `governanca (5)` → `governanca/` (novo, entra em `core_dirs`): `cooperative_governance, game_theory_analysis, trust_scoring, slashing_rules, tokenomics`. Cobertos: debate_strategies, phd_auditor, scientific_governance.

Total: 5+3+4+8+6+5+5=36.

## Padrão de realidade por arquivo (fail-closed, stdlib, sem rede)

Cada arquivo `<categoria>.py` deve:
1. Expor nomes e documentação coerentes com sua API; esses sinais só contam
   como inventário lexical, sem meta de inserir keywords para aprovar o scanner.
2. Expor 1-2 funções reais com comportamento testável (não stub `pass`):
   - `agents/*`: `describe()` + `delegate(task)` que valida e roteia sem executar (retorna plano).
   - `mci/*`: `context_manager` (janela com orçamento), `memory_updater` (append com hash), `orchestration_pipeline` (ordena etapas por dependência).
   - `evolution/*`: `cycles_manager` (lista/próximo id), `reflection_ledger` (append com timestamp), `autoevolve_pipeline` (estágios SENSE→LEARN como dados), `evolutionary_roadmap` (quick_wins/foundations).
   - `protocolos/*`: cada protocolo como `check(payload) → {approved, reason}` fail-closed (ex.: `sdd_spec_first` exige spec_id; `tdd_red_green_refactor` exige red_hash + green; `a2a_blackboard` valida anúncio; `mcp_interconnect` valida tool/arguments; `bernstein_orchestration` ordena; `sdd_gate` barra sem spec; `behavioral_gate` delega a `trust/behavioral_gate`; `reflexion_middleware` registra lição).
   - `integrations/*`: facades que verificam instalação (`shutil.which`) e montam argv sem executar (retorna plano + `available`).
   - `infra_dados/*`: `schemas_validator` (valida dict contra required), `data_pipeline` (normaliza CSV-like), `batch_executor` (ordena jobs), `assets_media` (manifesto com hash), `gametheory_models` (payoff/nash 2x2).
   - `governanca/*`: `cooperative_governance` (quórum), `game_theory_analysis` (nash 2x2), `trust_scoring` (média ponderada com supervisão <0.3), `slashing_rules` (tabela de faixas), `tokenomics` (emissão/gasto conservador).
3. Nunca alegar prova, desempenho, Qualis ou valor econômico. Fallback explícito.

Corpus: `protocolos/`, `infra_dados/`, `governanca/` entram em `core_dirs`; os 36 arquivos entram em `TRACKED_FILES` e `py_content_files`.

## Inspirações (referência)

Reuso dos padrões R830 (z3, kanren, vouch tiers, staking-mcp, TrustGate, prstake, mathkernel trail/trust) + padrões internos (SpecVerifier, TDDRunner, TrustEngine, TokenLedger, DebateStrategies, Moderator). Nenhum código de terceiro copiado ou executado.

## Aceite

- `tests/test_r832_restantes_36.py`: existência separada de operações,
  resultados booleanos estritos e negativos no nível `protocolos.*`, ordens
  topológicas exatas e resultados matemáticos corretos. Descrições/planos não
  contam como execução de agentes, CLIs ou MCP.
- Ledger e fachada comportamental: testes R836 e recibo com ledger preservado.
- Scanner: testes R835 sobre corpus retido independente, vazio e negativo,
  com hash e categorias únicas. Não se exige nem se declara 100% funcional.
- Os validadores esquemáticos SDD/TDD dos protocolos não são gates de entrega.
  O gate efetivo usa o primário, SpecVerifier e evidência emitida pelo runner.
  Remoção dos atalhos sem consumidores e limites dos contratos constam de R828.

## Limites

Operação local. Integrações verificam presença sem autenticar nem inferir. Governança/tokenomics são simulação local, não criptoativo. Revisão humana obrigatória.
