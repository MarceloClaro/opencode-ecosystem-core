---
spec_id: SPEC-935-R830
title: Cobertura por categoria — raciocinio_conhecimento (6) e trust_economy (6)
status: proposed
component: scanners/noological_scanner + trust/ + reasoning/ + economy/
test_file: tests/test_r830_categorias_razao_trust.py
---

# R830 — Resolver 12 ausências nome a nome (6 razão + 6 trust)

Retificação após revisão cega: o inventário histórico abaixo usa 83 projeções;
R835 distingue 81 categorias canônicas, sem dupla contagem. R838 substitui a
tradução SMT demonstrativa e o reparsing externo do SymPy pela gramática
restrita canônica. Presença no corpus não é cobertura funcional. Alegações de
ganho ou licença de referências externas abaixo pertencem ao despacho original;
não são resultados obtidos pelo Core nesta rodada.

Origem: varredura real do corpus (`_build_ecosystem_corpus`, 635801 chars) +
`NoologicalScanner.scan(research_domain=ecosystem)`:

- Total 83 (35 cobertas, 48 ausentes). Soma por camada: 16+4+11+6+11=48.
- Foco deste ciclo (12):
  - `raciocinio_conhecimento` 2/8: ausentes `z3_solver, critical_reasoner, quantum_reasoning, bayesian_inference, dialectical_engine, reasoning_engines`. Cobertas: `sympy, kanren`.
  - `trust_economy` 2/8: ausentes `staking_mechanism, slashing_mechanism, fee_market, behavioral_gate, outcome_tracker, stake_pool`. Cobertas: `trust_engine, token_economy`.
- Restantes 36 (agentes 5, mci 3, evolucao 4, protocolos 8, integracoes 6, infra 5, governanca 5) fora deste ciclo.

## Causa-raiz (instrumento + corpus)

1. `_compile_dimension_patterns` definida mas nunca chamada: `ECOSYSTEM_KEYWORDS` (desenhado para `z3, staking, sdd, tdd...`) jamais compilado. `_compiled_ecosystem` permanece `{}`.
2. `keyword_map_builtin` e `ENRICHED_KW` só têm dimensões acadêmicas, não ecossistema.
3. Fallback divide categoria por espaços (`split()`), mas categorias usam underscore (`z3_solver` vira token único). Só passa se corpus contiver literal `z3_solver`.
4. Corpus só contém literal snake_case via nomes de arquivo em `core_dirs`, termos de specs e conteúdo dos 40 `py_content_files`. Conceitos reais em CamelCase (`BehavioralGate`, `OutcomeTracker`, `Z3Engine`) não geram literal com underscore.
5. Resultado: presença real não é detectada; ausência é de sinal, nem sempre de capacidade.

## Inspirações externas (referência, sem copiar código nem executar terceiros)

Raciocínio (licenças verificadas na busca):
- `z3prover/z3` (MIT): prover SMT, bindings Python via `z3-solver`, API `Solver/add/check`, `push/pop`.
- `namin/holey` (MIT): síntese + execução simbólica combinando Z3/CVC5 com LLM, heurísticas externas.
- `ajinkya-awari/llm-reasoning-orchestrator`: pipeline neuro-simbólico — decompor, classificar por keyword, rotear SymPy vs LLM, validar passo, sintetizar. Ganho 0%→40% em matemática exata por delegação.
- `pythological/kanren`, `jknohr/kanren` (fork logpy): relacional/miniKanren, `eq/lall/lany/membero`, unificação.
- `mathkernel` (PyPI): kernel multi-engine com `trust level + engine tag + derivation trail`, separação exact/numeric/formal, `justified_trust` como teto.
- `basisresearch/lean.py` (Knuckledragger): tática Lean com oráculo Z3, conversor `Lean.Expr→Z3`, `ForAll` além do SymPy.
- arXiv: ReAct (Yao 2023), Toolformer (Schick 2023) — roteamento a ferramentas externas.

Trust/g Alta (padrões, sem blockchain neste ciclo):
- `vouch-protocol/vouch reputation.py`: `ReputationEngine` base 50, `+1 success / -2 failure / slash configurável`, decaimento 10% ao dia após 7 dias, tiers.
- `AiAgentKarl/agent-staking-mcp-server`: staking como colateral, tiers `bronze/silver/gold/platinum`, dispute com auto-slash do perdedor, leaderboard.
- `Rishikpulhani/TrustMyGit`: staking em issues, recompensa ETH+reputação, slashing por deadline/disputa, bonding curves.
- `agentcred/agentcred`: verificação TEE + slashing on-chain por faixa (5%/15%/30%), `TrustScoreRegistry` só por auditor.
- `TrustInfra/TrustGate`: trust comportamental (não identidade), sinal para roteamento/gating, decisão no aplicativo.
- `kpj2006/prstake`: staking sem slashing como rate-limit (sinal + limitador).
- arXiv 2511.03434 (Hu/Rong): `Brief/Claim/Proof/Stake/Reputation/Constraint` em A2A/AP2/ERC-8004; 2410.16529 DOL3 aprendizado vitalício distribuído.

## Escopo fechado (12 arquivos + 1 fix)

Fix do instrumento (1):
- `scanners/noological_scanner.py`: chamar `_compile_dimension_patterns(dim_key)` no `scan()` para dimensões ecossistema antes do loop. Sem mudar keywords. Teste prova que `ECOSYSTEM_KEYWORDS` passa a ser usado.

Facades reais com nomes exatos (12 arquivos, 100% stdlib, sem rede/inferência):
- `trust/staking_mechanism.py` — stake como compromisso + rate-limit (inspirado prstake + staking-mcp): `deposit/lock/release`, slots por agente, `stake_position`.
- `trust/slashing_mechanism.py` — penalidade proporcional fail-closed (inspirado vouch + agentcred faixas): `slash(amount, reason)`, `slash_rules`, nunca remove além do travado.
- `trust/fee_market.py` — mercado de taxas por prioridade (inspirado TokenEconomy `FeeQuote`): `quote(priority, congestion)`, `BASE_FEE`, multiplicadores.
- `trust/behavioral_gate.py` — pré-execução por trust (inspirado TrustGate + BehavioralGate): `allow(action, trust, threshold) → GateDecision`, tiers.
- `trust/outcome_tracker.py` — registro de outcomes com decaimento (inspirado vouch decay): `record(success)`, `score` com meia-vida, `success_rate`.
- `trust/stake_pool.py` — pool de stakes (inspirado StakingPool + bonding): `lock/release/slashed`, `total_locked`.
- `reasoning/z3_solver.py` — wrapper SMT fail-closed (inspirado z3 + holey): usa `z3-solver` se instalado, senão fallback explícito determinístico; nunca alega prova sem solver; `push/pop/check`.
- `reasoning/critical_reasoner.py` — crítica dialética (inspirado CriticalEngine): tese/antítese/síntese, checklist de falácias, veredito `sustentada/contestada`.
- `reasoning/quantum_reasoning.py` — facade sobre `reasoning/quantum.py` + Qiskit opcional: experimentos declarativos, fallback clássico explícito.
- `reasoning/bayesian_inference.py` — atualização conjugada Beta-Binomial/Normais (inspirado mathkernel trust): prior explícito, posterior, intervalo crível; sem prior oculto.
- `reasoning/dialectical_engine.py` — motor tese-antítese-síntese com trilha (inspirado lean tactic + critical): `run(thesis) → synthesis + trail`.
- `reasoning/reasoning_engines.py` — compositor multi-motor (inspirado llm-reasoning-orchestrator + mathkernel): `route(query) → SymPy/Z3/Kanren/fallback`, `engine tag + derivation trail + trust`, `justified_trust` como teto.

Nomes e termos reais das APIs podem compor o inventário de autodescoberta.
Não se acrescentam palavras ao código para atingir uma meta de cobertura.
A função é testada por resultado tipado independente da presença desses termos.

Também atualizar `DiagnosticPipeline.TRACKED_FILES` e `py_content_files` para incluir os 12 novos arquivos (transparência do corpus).

Exclui: 36 ausentes restantes, blockchain on-chain, TEE, Lean kernel, re-treino, mudança de keywords do scanner.

## Aceite fail-closed

- `tests/test_r830_categorias_razao_trust.py`: 12 testes de presença no corpus (`_build_ecosystem_corpus` contém literal) + 12 testes funcionais (comportamento real com fixtures, sem rede) + 1 teste do fix (`_compiled_ecosystem` não vazio após `scan`) + regressão R828 7/7.
- Novo `scan` local deve mostrar `raciocinio_conhecimento` 2→≥6/8 e `trust_economy` 2→≥6/8; total 35→≥47/83. Teleológico pode permanecer (prática histórica), sem alegar cura.
- Evidências em `outputs/core-r830/release-summary.json` com diff de `covered/absent` por dimensão.

## Limites

Operação local, sem validação externa. Z3/SymPy/Qiskit opcionais; ausência retorna `fallback` explícito com `available=False`, nunca sucesso presumido. Staking/slashing são colateral local em memória/JSON, não criptoativo. Revisão humana obrigatória. Nada de terceiro é clonado, instalado ou executado.
