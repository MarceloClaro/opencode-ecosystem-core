---
spec_id: SPEC-935-R454
title: Evidência runtime granular e fechamento rastreável de release
component: sdd, marceloclaro, specs, tests, validation
status: green
round_id: R454
test_file: tests/test_r454_criterion_runtime_evidence.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    strict_contract_requires_complete_bindings:
      - tests/test_r454_criterion_runtime_evidence.py::test_v1_contract_requires_every_markdown_criterion
    global_suite_success_is_insufficient:
      - tests/test_r454_criterion_runtime_evidence.py::test_v1_rejects_global_evidence_without_criterion_records
    criterion_records_are_runtime_bound:
      - tests/test_r454_criterion_runtime_evidence.py::test_v1_requires_matching_runtime_bound_records
    invalid_or_nonpassing_targets_fail_closed:
      - tests/test_r454_criterion_runtime_evidence.py::test_v1_rejects_invalid_targets_and_nonpassing_outcomes
    strict_specs_start_red_until_runtime_evidence:
      - tests/test_r454_criterion_runtime_evidence.py::test_v1_loaded_green_frontmatter_starts_red
    legacy_contracts_remain_compatible:
      - tests/test_r454_criterion_runtime_evidence.py::test_legacy_markdown_contracts_remain_compatible
    r447_audit_is_traceable_and_closed:
      - tests/test_r454_criterion_runtime_evidence.py::test_r447_receipt_and_criteria_are_traceable
    release_specs_use_granular_contracts:
      - tests/test_r454_criterion_runtime_evidence.py::test_release_specs_use_criterion_runtime_v1
    runtime_evidence_scope_remains_local:
      - tests/test_r454_criterion_runtime_evidence.py::test_runtime_evidence_is_locally_scoped
---

# SPEC-935-R454 — Evidência Runtime Granular e Fechamento Rastreável de Release

## Objetivo

Eliminar a promoção coletiva de critérios Markdown por uma única execução verde
e fechar a auditoria R447 com um recibo local rastreável. A evidência deve ser
emitida pelo runtime para cada critério associado a alvos de teste explícitos,
sem transformar testes locais em validação ou certificação externa.

## Critérios de Aceitação Executáveis

- `strict_contract_requires_complete_bindings` — uma spec no modo
  `criterion-runtime-v1` só é carregada como contrato estrito quando cada ID
  Markdown possui associação não ambígua, canônica e contida no `test_file`.
- `global_suite_success_is_insufficient` — uma evidência global verde, sem
  registros individuais para todos os critérios declarados, não promove a spec
  nem os critérios ausentes.
- `criterion_records_are_runtime_bound` — cada aprovação estrita requer objeto
  selado pelo runtime com `spec_id`, ID do critério, alvo executado e impressão
  digital do contrato correspondentes; payload ou serialização controlados pelo
  agente não substituem essa prova.
- `invalid_or_nonpassing_targets_fail_closed` — alvo ausente, fora do checkout,
  não coletado, skipped, xfailed, com timeout, erro ou falha deixa apenas o
  critério correspondente vermelho.
- `strict_specs_start_red_until_runtime_evidence` — `status: green` declarado
  no frontmatter de uma spec estrita não substitui evidência runtime fresca e
  local para a execução atual.
- `legacy_contracts_remain_compatible` — specs e critérios programáticos
  legados preservam o comportamento documentado, mas não são apresentados como
  cobertura granular `criterion-runtime-v1`.
- `r447_audit_is_traceable_and_closed` — R447 possui critérios executáveis,
  recibo local com ambiente, comandos, resultados, achados, limites e escopo
  somente leitura, além de ciclo de evolução que referencia tal evidência.
- `release_specs_use_granular_contracts` — as specs R447–R453 que sustentam o
  lote de release usam associações explícitas por critério e não declaram uma
  contagem granular baseada apenas em uma suíte global.
- `runtime_evidence_scope_remains_local` — resultados expõem escopo local e
  `external_validation: false`; documentação não usa esses gates como prova de
  certificação externa, segurança absoluta ou validação independente.

## Estratégia TDD

1. Criar regressões RED para evidência global sem vínculos, registros parciais,
   fingerprint divergente, alvos inválidos e frontmatter verde autoafirmado.
2. Implementar o contrato versionado e a emissão selada de registros por
   critério, mantendo compatibilidade explícita para specs legadas.
3. Migrar R447–R453 para associações de testes auditáveis e produzir o recibo
   factual da auditoria R447.
4. Executar testes focados, gates SDD locais, suíte integral e revisão do índice
   antes de retomar o commit.

## Não objetivos

- Não afirmar que a associação teste→critério substitui revisão humana de
  suficiência semântica.
- Não tratar objetos selados no mesmo processo como sandbox contra código
  arbitrário.
- Não converter execução local, recibos ou resultados de pytest em certificação
  externa, auditoria independente ou garantia absoluta.
