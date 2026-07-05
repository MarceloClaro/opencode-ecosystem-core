# Índice de Rastreabilidade de Especificações

Este diretório consolida a rastreabilidade completa do ecossistema, combinando as especificações nativas do Core (SDD) com o acervo legado portado do OpenCode_Ecosystem original.

## Especificações Nativas do Core (SDD)

| Spec | Componente | Módulo |
|---|---|---|
| SPEC-001 | MetaBus + Memória Global | `mci/metabus.py` |
| SPEC-002 | Blackboard A2A | `mci/blackboard.py` |
| SPEC-003 | Reflexion Middleware | `mci/reflexion.py` |
| SPEC-004 | Camada Transformer | `transformer/` |
| SPEC-005 | Orquestrador MarceloClaro | `marceloclaro/orchestrator.py` |
| SPEC-006 | Protocolo dos Agentes | `agents/` |
| SPEC-007 | Trust Engine | `trust/trust_engine.py` |
| SPEC-008 | Token Economy | `economy/token_economy.py` |
| SPEC-009 | Pipeline de Scanners | `scanners/pipeline.py` |
| SPEC-010 | Pipeline Acadêmico MASWOS | `academic/maswos.py` |
| SPEC-011 | Raciocínio + Quantum | `reasoning/` |
| SPEC-012 | Ciclos Evolutivos | `evolution/cycles.py` |
| SPEC-013 | Integrações CLI | `integrations/` |

## Acervo Legado (`specs/legacy/`)

O diretório `specs/legacy/` preserva o acervo integral de especificações do repositório original **MarceloClaro/OpenCode_Ecosystem**, incluindo os SPECs numerados (SPEC-001 a SPEC-081+ do sistema original, entre eles o SPEC-038 do Trust Engine, os SPEC-022 a SPEC-025 da Token Economy e o SPEC-046 da integração Antigravity), documentos de contexto, e o subdiretório `tdd-sdd/` com os artefatos da metodologia TDD/SDD original. Este acervo garante rastreabilidade histórica completa das decisões de design que originaram cada componente portado para o Core.

A correspondência entre componentes portados e suas especificações de origem é direta: o `trust/trust_engine.py` implementa o SPEC-038 (BehavioralGate, NaturalForgetting, OutcomeTracker); o `economy/token_economy.py` implementa os SPEC-022~025 (staking, slashing, fee market); o `integrations/antigravity/` implementa o SPEC-046; e os ciclos evolutivos R1–R46 documentados em `evolution/evo-*.md` fundamentam o `EvolutionRegistry`, que continua a numeração a partir de R47.
