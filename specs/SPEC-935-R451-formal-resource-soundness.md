---
spec_id: SPEC-935-R451
title: Limites de recurso e exatidão do fragmento formal
component: integrations/deepmind/formal_verifier.py, tests
status: green
round_id: R451
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    power_growth_is_bounded_before_sympy_construction:
      - tests/test_r451_formal_resource_soundness.py::test_power_growth_is_rejected_before_sympy_construction
    inexact_numeric_literals_are_rejected:
      - tests/test_r451_formal_resource_soundness.py::test_float_literals_are_not_silently_rounded_into_formal_identities
    counterexample_search_covers_bound_variables:
      - tests/test_r451_formal_resource_soundness.py::test_counterexample_search_enumerates_all_declared_variables_within_budget
    propositional_input_has_structural_budget:
      - tests/test_r451_formal_resource_soundness.py::test_propositional_parser_rejects_input_before_recursive_depth_is_exhausted
    formal_limits_fail_closed:
      - tests/test_r451_formal_resource_soundness.py::test_power_growth_is_rejected_before_sympy_construction
      - tests/test_r451_formal_resource_soundness.py::test_float_literals_are_not_silently_rounded_into_formal_identities
      - tests/test_r451_formal_resource_soundness.py::test_counterexample_search_enumerates_all_declared_variables_within_budget
      - tests/test_r451_formal_resource_soundness.py::test_propositional_parser_rejects_input_before_recursive_depth_is_exhausted
---

# SPEC-935-R451 — Limites de recurso e exatidão do fragmento formal

## Objetivo

Completar o fechamento fail-closed do verificador formal após a auditoria R450:
o fragmento algébrico não pode materializar potências explosivas ou arredondar
literais textuais, a busca de contraexemplos não pode ocultar variáveis livres
e a gramática proposicional deve recusar entradas além de orçamento estrutural.

## Critérios de Aceitação Executáveis

- `power_growth_is_bounded_before_sympy_construction` — potência aninhada,
  base composta excessiva ou orçamento acumulado de potência são recusados pela
  AST antes de criar objetos SymPy; identidades elementares como `(a+b)**2`
  continuam aceitas.
- `inexact_numeric_literals_are_rejected` — o fragmento formal aceita inteiros
  e racionais expressos por operações, mas recusa `float` e `complex` textuais
  que o parser Python poderia arredondar antes da prova.
- `counterexample_search_covers_bound_variables` — para um domínio pequeno, a
  busca percorre o produto cartesiano das variáveis declaradas dentro de um
  teto explícito e recusa expressões com símbolos livres não declarados.
- `propositional_input_has_structural_budget` — tamanho, quantidade de tokens,
  encadeamento de negações e aninhamento proposicional são limitados antes do
  parser recursivo ou do Z3.
- `formal_limits_fail_closed` — entradas fora dos limites retornam falha ou
  ausência de contraexemplo sem promover uma prova, sem dependência de rede ou
  processo externo.

## Estratégia TDD

1. Criar testes RED para potência cumulativa, precisão numérica, produto de
   variáveis e fórmula proposicional longa.
2. Aplicar limites sintáticos antes de construção/equivalência simbólica.
3. Rodar testes focados, suíte integral e gate SDD com evidência runtime.

## Não objetivos

- Não declarar que limites locais eliminam toda possibilidade de consumo de
  recurso ou substituem sandbox de processo para entradas arbitrárias.
- Não ampliar a gramática SymPy suportada além do fragmento auditável.
