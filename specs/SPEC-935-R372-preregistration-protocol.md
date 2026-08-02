---
spec_id: SPEC-935-R372
title: Protocolo de Pré-registro — declaração prévia + verificação de desvio
component: mci/preregistration_protocol.py + mci/experiment_designer.py + agentic_science_v2/review_agent.py
status: verified
test_file: tests/test_r372_preregistration_protocol.py
---

# SPEC-935-R372 — Protocolo de Pré-registro

**Data:** 2026-08-02
**Motivação dupla:**

1. **Correção de bug real (overclaim):** `mci/experiment_designer.py::design_experiment()`
   linha `"pre_registered": context.get("pre_registered", True)` assume
   `True` por padrão sem verificação alguma — qualquer chamador que não
   declare nada ganha o selo "pré-registrado" de graça. Exatamente o tipo
   de alegação sem sustentação que o `CORRIGENDUM.md` existe para evitar.
2. **Fecha o item descartado no brainstorming do R370**: pré-registro de
   protocolo (hipótese, método, critério de falsificação e alpha
   declarados **antes** de rodar a análise) reduz p-hacking e HARKing
   (Hypothesizing After Results are Known).

**Limite epistêmico:** o módulo não impede que alguém minta ao registrar
o protocolo (não há como impedir isso sem uma autoridade externa de
timestamp) — ele impede a forma mais comum de p-hacking: **mudar
silenciosamente** hipótese/método/alpha depois de ver os dados. A
comparação é textual exata (normalizada por case/espaços), porque
reformulação "só de forma" é justamente como HARKing se disfarça.

## 1. `register_protocol(hypothesis, method, falsification_criterion, alpha=0.05) -> dict`

- Valida os 4 campos (strings não vazias; `alpha` em `(0, 1)`) —
  `ContractError` fail-closed.
- `protocol_id` determinístico: hash SHA-256 (24 hex, mesmo padrão de
  `translation.cultural_episteme.build_terminology_delta`) do conteúdo
  canônico `{hypothesis, method, falsification_criterion, alpha}`
  normalizado (casefold + strip).
- `registered_at`: timestamp real (`time.time()`), não determinístico —
  segue a convenção já usada em `Evidence.timestamp` (R102); testes não
  comparam esse campo por igualdade exata.
- Retorna o protocolo completo (campos originais + `protocol_id` +
  `registered_at`), destinado a ser guardado pelo chamador e apresentado
  de volta em `verify_protocol`.

## 2. `verify_protocol(protocol, actual_hypothesis, actual_method, actual_alpha) -> dict`

- Compara cada campo declarado contra o valor **efetivamente usado** na
  análise, normalizado (casefold + strip para texto; `abs(diff) < 1e-9`
  para `alpha`).
- `honored = True` **somente se os 3 campos comparáveis coincidem**
  (hipótese, método, alpha — `falsification_criterion` é declarado mas
  não comparável contra "uso real", pois não há um valor efetivo
  equivalente a comparar; ele figura no relatório como contexto).
- Cada divergência gera achado `PROTOCOL_DEVIATION` (severity `high`)
  nomeando o campo, o valor declarado e o valor efetivo.
- Retorna envelope: `schema_version`, `protocol_id`, `honored`,
  `findings[]`, `human_gate` (`required` se houver desvio),
  `disclaimer`.
- `protocol` inválido (sem `protocol_id`) → `ContractError`.

## 3. Correção do bug em `mci/experiment_designer.py`

- `design_experiment()`: `pre_registered` deixa de ter default `True`.
  Novo comportamento:
  - se `context` traz `registered_protocol` (dict de `register_protocol`)
    **e** `actual_hypothesis`/`actual_method`/`actual_alpha`: chama
    `verify_protocol` e usa `honored` como `pre_registered`, anexando
    `protocol_verification` ao `design`;
  - caso contrário: `pre_registered = False` (correção do bug — não é
    mais um freebie) com nota explícita em `limitations`: "Pré-registro
    não declarado; nenhum protocolo formal foi verificado antes da
    análise."
- Teste de regressão prova que o comportamento antigo (default `True`
  sem verificação) não existe mais.

## 4. Integração no R103

`OrchestratorReviewer.verify_preregistered_claim(claim_id, protocol,
actual_hypothesis, actual_method, actual_alpha, ledger) -> dict` — mesmo
padrão de `verify_statistical_claim`/`verify_multidisciplinary_claim`
(R370/R371): só verifica a claim no ledger quando `honored=True`.

## 5. Critérios de aceitação

1. `register_protocol`: campos vazios ou `alpha` fora de `(0,1)` →
   `ContractError`; `protocol_id` determinístico para o mesmo conteúdo
   normalizado.
2. `verify_protocol`: todos os campos coincidem → `honored=True`, zero
   achados; qualquer campo divergente → `honored=False` +
   `PROTOCOL_DEVIATION` nomeando o campo.
3. Normalização: diferença de caixa/espaços não conta como desvio;
   diferença de conteúdo real conta.
4. `design_experiment()`: sem protocolo registrado → `pre_registered=False`
   (bug corrigido, testado explicitamente contra o comportamento antigo);
   com protocolo honrado → `pre_registered=True`; com protocolo violado →
   `pre_registered=False` e motivo anexado.
5. `verify_preregistered_claim`: claim só verificada quando `honored=True`.
6. Suíte do ciclo verde; zero regressão em `mci.statistical_validator`,
   R101-R105, R370, R371.
