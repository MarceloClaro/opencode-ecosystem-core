---
spec_id: SPEC-935-R452
title: Soundness de domínio algébrico e orçamentos globais formais
component: integrations/deepmind/formal_verifier.py, tests
status: green
round_id: R452
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    symbolic_denominators_are_not_universal_identities:
      - tests/test_r452_domain_soundness_budgets.py::test_symbolic_denominators_are_rejected_before_universal_identity_check
    logical_input_has_global_budget:
      - tests/test_r452_domain_soundness_budgets.py::test_logical_implication_rejects_excessive_aggregate_input_before_z3
      - tests/test_r452_domain_soundness_budgets.py::test_logical_implication_sets_a_runtime_z3_timeout
      - tests/test_r452_domain_soundness_budgets.py::test_logical_implication_uses_a_snapshot_after_preflight
    proof_step_input_has_global_budget:
      - tests/test_r452_domain_soundness_budgets.py::test_proof_steps_reject_excessive_batch_before_full_processing
      - tests/test_r452_domain_soundness_budgets.py::test_proof_step_snapshot_rejects_subclasses_and_oversized_text
    proof_claim_has_canonical_restricted_syntax:
      - tests/test_r452_domain_soundness_budgets.py::test_proof_claim_is_parsed_before_matching_a_verified_step
    raw_algebraic_syntax_is_ascii_and_comment_free:
      - tests/test_r452_domain_soundness_budgets.py::test_raw_algebraic_input_rejects_unicode_normalization_and_comments
    global_limits_fail_closed:
      - tests/test_r452_domain_soundness_budgets.py::test_logical_implication_rejects_excessive_aggregate_input_before_z3
      - tests/test_r452_domain_soundness_budgets.py::test_proof_steps_reject_excessive_batch_before_full_processing
      - tests/test_r452_domain_soundness_budgets.py::test_proof_step_snapshot_rejects_subclasses_and_oversized_text
---

# SPEC-935-R452 — Soundness de domínio algébrico e orçamentos globais formais

## Objetivo

Remover as últimas promoções indevidas e vetores de consumo agregado do
verificador formal: uma identidade não deve ignorar denominadores simbólicos,
e entradas compostas por muitas premissas ou passos devem respeitar limites
globais antes de SymPy, Z3 ou acumulação de resultados.

## Critérios de Aceitação Executáveis

- `symbolic_denominators_are_not_universal_identities` — divisão e potência
  não positiva só aceitam denominador/base literal inteiro não nulo; `x/x = 1`,
  inversos simbólicos e formas indefinidas como `0**0` são recusados, enquanto
  coeficientes racionais literais continuam verificáveis.
- `logical_input_has_global_budget` — implicação exige lista finita, tem teto
  de premissas e de tamanho agregado, limita átomos distintos e configura
  timeout explícito no solver Z3; premissas validadas são copiadas para
  snapshot imutável antes de qualquer análise ou construção Z3.
- `proof_step_input_has_global_budget` — sequência de passos e texto agregado
  possuem teto e ultrapassá-lo retorna resultado não válido sem processar todos
  os passos; a prova usa snapshot de `dict` e `str` nativos, sem subclasses ou
  leitura variável entre validação e consumo.
- `proof_claim_has_canonical_restricted_syntax` — a alegação principal é uma
  igualdade do fragmento algébrico restrito e é comparada estruturalmente a um
  passo validado, sem normalização textual que crie outra fórmula.
- `raw_algebraic_syntax_is_ascii_and_comment_free` — o texto bruto rejeita
  identificadores Unicode normalizáveis e comentários antes de `ast.parse`.
- `global_limits_fail_closed` — entradas além de qualquer orçamento retornam
  falha, sem promover prova, sem chamadas de rede ou processos externos.

## Estratégia TDD

1. Adicionar testes RED para domínio de divisão, lista de premissas e lote de
   passos excessivo.
2. Impor as guardas antes de construir expressões ou chamar o solver.
3. Executar testes focados, suíte integral e gate SDD runtime antes de promoção.

## Não objetivos

- Não provar validade universal para funções com domínio parcial fora do
  fragmento estrito.
- Não alegar sandbox completo de CPU ou memória para bibliotecas simbólicas.
