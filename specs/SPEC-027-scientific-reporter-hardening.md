# SPEC-027 — Hardening do ScientificReporter

```yaml
spec_id: SPEC-027
title: Remoção de SyntaxWarning e preservação dos contratos LaTeX do ScientificReporter
version: 1.0.0
status: active
owner: marceloclaro
depends_on: [SPEC-021]
origin: refinamento pós-auditoria para eliminar invalid escape sequences em mci/scientific_reporter.py
```

## 1. Objetivo

Eliminar os `SyntaxWarning` gerados por *invalid escape sequences* em `mci/scientific_reporter.py`, preservando o conteúdo LaTeX e sem regressão funcional no `ScientificReporter`.

## 2. Requisitos

| ID | Requisito | Critério de aceitação |
|---|---|---|
| REQ-027.1 | O fonte `mci/scientific_reporter.py` DEVE compilar sem `SyntaxWarning` | `compile()` sob `warnings.simplefilter("error", SyntaxWarning)` não falha |
| REQ-027.2 | `build_report()` DEVE preservar as seções científicas atuais | testes continuam encontrando Hipóteses, Resultados, Limitações, Veredito, Metadados |
| REQ-027.3 | `build_executive_summary()` e `build_reproducibility_checklist()` NÃO DEVEM regredir | testes existentes continuam verdes |

## 3. Invariantes

- INV-027.1: O output LaTeX continua sendo string válida para o pipeline atual.
- INV-027.2: Nenhum símbolo LaTeX intencional (`\section`, `\textbf`, `\c{c}`, `\~`) pode ser perdido.

## 4. Critérios de Aceitação

- [x] `tests/test_scientific_reporter_hardening.py` passa
- [x] `tests/test_scientific_superhuman.py::TestScientificReporter` continua verde

## 5. TDD

- RED: adicionar teste de compilação sem `SyntaxWarning`
- GREEN: corrigir literais com escapes inválidos
- REFACTOR: consolidar strings LaTeX sem alterar o comportamento
