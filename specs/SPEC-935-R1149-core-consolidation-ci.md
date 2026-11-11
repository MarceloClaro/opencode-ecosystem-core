# SPEC-935-R1149 — Consolidação do runtime, CI e claims graph

**Status:** implementação local; sem hardware
**Data:** 2026-11-10
**Depende de:** R1132, R1148
**Objetivo:** eliminar duplicações entre `core_cognition` e `mci`, fazer o CI
cobrir a branch de trabalho e os proofs Lean, e persistir o grafo de claims.

## 1. Requisitos

- **R1.** `mci.runtime_contract` é adaptador de execução sobre
  `core_cognition.runtime_contract`; não redefine política de ação.
- **R2.** A decisão canônica (`allow`, `ask`, `defer`, `block`) é consultada
  antes de executar; `ask` escala, `defer`/`block` bloqueiam.
- **R3.** Hooks `before`/`after`, circuit breaker e auditoria JSONL continuam
  disponíveis no adaptador.
- **R4.** `mci.claims_graph` persiste (`save`/`load`), audita (`audit`) e faz
  ponte com `core_cognition.claims_ledger` (`from_ledger`/`to_ledger`).
- **R5.** O CI principal dispara em `codex/**` e `feat/**` e possui job
  dedicado de Lean 4 + Mathlib.
- **R6.** `whoosh3` é dependência declarada de desenvolvimento/CI.

## 2. Critérios de aceitação

- testes R1148 de runtime continuam passando;
- novo teste prova que `core_state.allowed` incrementa e que `stop` bloqueia;
- `ask` de ação irreversível escala com `core_decision.rule`;
- grafo salva/carrega com o mesmo número de nós/arestas e mantém warrant;
- ledger → grafo → ledger preserva `claim_id`, `status` e `falsifier`;
- carregar grafo com aresta órfã falha fechado;
- YAML dos workflows é válido;
- job Lean compila `ComplexProofs.lean`, `CorrelationCounterproof.lean` e
  `MathlibCounterproof.lean` (execução real no CI, com cache do Mathlib).

## 3. Limites

O patch de workflow exige credencial com escopo `workflow`; enquanto não for
aplicado, os gatilhos e o job Lean não estão ativos no GitHub. O job Lean pode
consumir 10–30 minutos e depende de rede para o cache do Mathlib. A integração de claims é uma ponte lossy: evidência do ledger vira
nó de evidência/teste com peso 0,5 e o pareamento continua editorial. Nada
aqui executa hardware, promove confiança ou valida eficácia clínica.
