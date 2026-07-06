# SPEC-025 — Hardening TDD do Scientific Governance Pipeline

```yaml
spec_id: SPEC-025
title: Fixtures e contract tests do Scientific Governance Pipeline
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-021, SPEC-023]
origin: Fechamento do item parcial `scientific_governance_tdd_plan` na auditoria de inspirações
```

## 1. Objetivo

Completar a lacuna do plano TDD do pipeline científico com governança, adicionando:

- diretórios de fixtures previstos no plano
- payloads determinísticos mínimos
- contract tests para os 3 schemas centrais

## 2. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| REQ-025.1 | O repositório DEVE conter `tests/fixtures/problems/` | diretório existe com pelo menos 1 JSON |
| REQ-025.2 | O repositório DEVE conter `tests/fixtures/oqs_candidates/` | diretório existe com payload válido |
| REQ-025.3 | O repositório DEVE conter `tests/fixtures/vsee_routes/` | diretório existe com payload válido |
| REQ-025.4 | O repositório DEVE conter `tests/fixtures/egs_cases/` | diretório existe com payload válido |
| REQ-025.5 | O repositório DEVE conter `tests/fixtures/pipeline/` | diretório existe com payload válido |
| REQ-025.6 | O sistema DEVE possuir contract tests para os schemas `optimal_question`, `vector_execution_decision` e `ethical_assessment` | `tests/test_scientific_governance_contracts.py` verde |
| REQ-025.7 | A auditoria de inspirações DEVE classificar `scientific_governance_tdd_plan` como `implemented` | teste de auditoria verde |

## 3. Invariantes

- INV-025.1: Fixtures são determinísticos e legíveis em UTF-8.
- INV-025.2: Todos os payloads de contrato respeitam campos obrigatórios e enums dos schemas.
- INV-025.3: Nenhum fixture depende de rede ou estado externo.

## 4. Critérios de Aceitação

- [x] `tests/test_scientific_governance_contracts.py` passa
- [x] os 5 diretórios de fixtures existem
- [x] `scientific_governance_tdd_plan` passa de `partial` para `implemented`

## 5. TDD

- RED: criar testes de contrato + auditoria
- GREEN: criar fixtures e payloads
- REFACTOR: consolidar utilitários sem alterar os contratos
