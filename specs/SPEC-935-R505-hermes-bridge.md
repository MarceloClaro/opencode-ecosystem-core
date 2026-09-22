---
spec_id: SPEC-935-R505
component: hermes_bridge.*
title: Hermes Bridge — contratos opcionais de interoperabilidade (sem runtime)
version: 1.0.0
status: green
test_file: tests/test_r505_hermes_bridge.py
---

# SPEC-935-R505 — Hermes Bridge no OpenCode Ecosystem Core

## Meta
- **Ciclo**: R505
- **Origem**: `MarceloClaro/hermes-agent` (fork de `NousResearch/hermes-agent`, Nous Research — autoria externa preservada) e contratos Hermes Bridge v1 do ReversaFeynman.
- **Escopo**: definir a *fronteira* de interoperabilidade com o runtime Hermes como **contratos opcionais**, sem adicionar runtime Hermes/Nous/Python ao core. A bridge fica **inerte** sem transporte configurado. Não transfere autoridade epistemológica ao runtime.
- **Motivação**: o ecossistema já cobre memória (MetaBus), aprendizado (autoevolve/EvolutionRegistry) e subagentes (Task/Blackboard). O Hermes runtime agregaria apenas operação (gateway Telegram/Discord/Slack, cron, backends remotos) — ganho operacional, não científico. A bridge habilita futura conexão opcional com firewall epistemológico.

## Arquitetura

```
hermes_bridge/
├── __init__.py
├── contracts.py        # schemas v1: hermes.memory, hermes.skill.proposal,
│                       #   hermes.trajectory, hermes.execution.result
├── memory_firewall.py  # memória aceita INFERRED/UNVERIFIED/BLOCKED; nunca OBSERVED
├── skill_governance.py # proposal nasce shadow; gates; executable=False; mutation nunca automática
├── trajectory.py       # sinais operacionais conservadores (steps/failures/tool_calls/duration/retry/terminal)
├── evidence_adapter.py # execution result → evidência direta → claim_id → EvidenceGuard (R504)
└── bridge.py           # dispatch inerte sem transport; sem dependência Hermes
```

## Critérios de aceitação

1. **MemoryFirewall** — eventos `hermes.memory/v1` só aceitam `INFERRED | UNVERIFIED | BLOCKED`; `scope=personalization` isolado; nunca `OBSERVED`.
2. **SkillGovernance** — toda proposal nasce `mode=shadow, requires_review=True, requires_tests=True, evidence_authority=False`; elegibilidade exige review AND tests AND feynman AND no-drift; mesmo elegível `executable=False, file_mutation_performed=False`.
3. **Trajectory** — extrai apenas sinais conhecidos; falha de provisionamento de runner não conta como aprovação nem como falha de step.
4. **EvidenceAdapter** — `execution.result/v1` com `direct_evidence[]` e `claim_id` explícito propõe evidência ao EvidenceGuard (R504); sem claim_id mapeado, **nunca** promove claim.
5. **Bridge** — sem transporte configurado, `dispatch()` é no-op (inerte); módulo não importa Hermes.
6. Integra com `reversa_feynman.evidence_guard` (dependência local, não externa).

## Não-escopo
- Não instala/gera runtime Hermes; Não duplica MetaBus/autoevolve; não promete ganho de acurácia.