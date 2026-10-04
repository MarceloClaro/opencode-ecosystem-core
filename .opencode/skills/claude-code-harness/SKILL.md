---
name: claude-code-harness
description: >-
  Curadoria do Claude Code Harness (Chachamaru127, MIT) — loop disciplinado
  Plan→Work→Review→Release com 5 verb skills e rota OpenCode
  (scripts/setup-opencode.sh, tier internal-compatible). Use para referenciar
  o contrato spec.md/Plans.md, gates de aprovação e o diagnóstico
  bin/harness doctor --migration-report. Metodologia espelha o SDD/TDD do Core;
  NÃO clona nem executa o harness.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R647
spec: SPEC-935-R647-ecossistema-claude.md
---

# Skill: Claude Code Harness (curadoria, SPEC-935-R647)

Referência metodológica, não execução. O orquestrador lê este SKILL.md e
aplica o loop no contexto atual do Core.

## O loop (espelho do nosso SDD/TDD)

| Harness | Core |
|---|---|
| `/harness-plan` → `spec.md` + `Plans.md` (escopo, critérios, unknowns, stop) | SPEC formal antes de implementar |
| Aprovação do contrato pelo operador | Gate SDD |
| `/harness-work` (fatia aprovada, TDD) | RED→GREEN→REFACTOR |
| `/harness-review` (achados major = blockers) | BehavioralGate / QA |
| `/harness-release` (só evidência verificada) | EvolutionRegistry + release |

## Comandos do harness (no repo do operador, opt-in)

- `/harness-setup` — baseline (guidance, hooks, checks).
- `/harness-plan`, `/harness-work [all]`, `/harness-review`, `/harness-release`.
- `bin/harness doctor --migration-report` — inventário sem deletar (caches,
  skills duplicadas, symlinks, OpenCode backups, harness-mem).
- OpenCode: `scripts/setup-opencode.sh` (paridade real NÃO alegada).

## Regras

- Dados não observados ficam `unknown` — nunca inventar.
- `not_observed != absent`: sem prova local, "não provado aqui".
- Suporte por host: Claude supported; Codex/OpenCode internal-compatible;
  Copilot candidate; Antigravity future/unsupported.
