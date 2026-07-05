# SPEC-TOP-002: Cora-Debate
Version: 1.0.0 | Domain: verification

## Objective
Arquitetura de debate multiagente com verificacao simbolica formal. 7 verificadores V1-V7, Q-Score UCB1 para selecao adaptativa de arguedores, self-consistency K=7, temperatura adaptativa, calibracao Platt.

## Acceptance Criteria
- [x] CT-1: MCPHandler health check returns running
- [x] CT-2: V1 dimensional analysis (F=ma passes, F=m fails)
- [x] CT-3: List verifiers returns >=7 available
- [x] CT-4: validate_cora.py and SKILL.md exist and well-formed

## Assets
- validate_cora.py
- servers/cora_verifier.py
- servers/context_weight_engine.py
- tests/test_cora_debate.py
