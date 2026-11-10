# SPEC-935-R1133 — Desenho pareado randomizado para layouts

**Status:** implementação local, sem hardware
**Depende de:** R1120, R1124

## 1. Contexto

A comparação anterior usou pares físicos diferentes (0/1 vs 106/107) sem
randomização, confundindo layout com qualidade do qubit. Não se deve comparar
layouts com um único par por braço nem tratar a diferença como causal.

## 2. Método

- unidade experimental: par físico + instância de circuito;
- dois desenhos:
  - `within_pair`: mesmo par físico, compiladores/estratégias diferentes;
  - `layout_randomized`: pares diferentes, atribuição AB/BA randomizada;
- métrica primária: diferença pareada de TVD mitigada;
- covariável: r1 do par;
- `n` por aproximação normal pareada;
- regra de decisão: só comparar com `enough_pairs` e `confound.allowed`.

## 3. Requisitos

- **R1.** `paired_sample_size`, `randomized_assignment`, `confound_audit`.
- **R2.** Pré-registro com n, seed, atribuição, covariável e regra.
- **R3.** Bloquear pares diferentes sem randomização.
- **R4.** Nenhum hardware, submissão ou credencial.
- **R5.** Não declarar layout superior sem dados.

## 4. Critérios

- n cresce quando o efeito diminui;
- atribuição balanceada e determinística;
- confound bloqueia 0/1 vs 106/107 sem randomização;
- pré-registro com `hardware_submission_allowed=False`;
- testes e relatório.

## 5. Limites

A fórmula normal não cobre drift/caudas; r1 continua gate físico. Se o r1 não
puder ser reduzido, ele deve ser reportado como limitação ou usado como
covariável, não apagado por mitigação.
