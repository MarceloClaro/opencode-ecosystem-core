# SPEC-935-R1147 — Correlações, arranjos e contraprovas

**Status:** implementação local; sem hardware
**Data:** 2026-11-10
**Depende de:** R1146, R1114, R1147
**Fontes:** PRA 2025 `10.1103/6p6s-t8b7`; TRIM `10.1109/qsw59989.2023.00025`;
ASPLOS 2019 `10.1145/3297858.3304075`; Quantum 2021
`10.22331/q-2021-09-21-548`; Quantum 2025 `10.22331/q-2025-11-14-1909`;
PRA 2021 `10.1103/physreva.104.052607`; PRA 2021
`10.1103/physreva.103.022607`.

## 1. Objetivo

Mitigar erros e inovar arranjos com base em **correlação de leitura**,
produzindo:

1. uma correlação auditável (`p_ij`, `phi`, cotas) que não assume independência;
2. um otimizador de layout multi-termo (porta, leitura, crosstalk, correlação);
3. contraprovas explícitas de que marginais não bastam, greedy pode falhar e o
   ótimo depende do regime;
4. contraprova formal em Lean 4 + Mathlib.

## 2. Requisitos

- **R1.** `calibration_correlations(counts, qubits)` com marginais,
  co-ocorrências, `phi`, cotas, deltas e IC de Wilson.
- **R2.** `simulate_correlated_readout` com fator latente e `rho` explícito.
- **R3.** `layout_cost` decomposto em porta, leitura, crosstalk e correlação.
- **R4.** `greedy_layout`, `two_opt`, `exhaustive_layout`, `optimize_layout`.
- **R5.** Contraprovas: `find_greedy_counterexample`,
  `find_regime_reversal`, `correlation_blind_counterexample`.
- **R6.** `CorrelationCounterproof.lean` com 10 teoremas kernel-checked.
- **R7.** Gate fail-closed com prova + contraprova e certificado SHA-256.
- **R8.** Nenhum hardware, chave, submissão ou alegação de vantagem.

## 3. Critérios de aceitação

- tabelas A/B têm marginais iguais e juntas diferentes;
- `phi_A > 0,5` e `phi_B ≈ 0`;
- `P(0 erro)_A > P(0 erro)_B` e `P(≥1)_A < P(≥1)_B`;
- cotas contêm o observado;
- layout ciente reduz o custo total no modelo declarado;
- greedy tem gap > 0 em ao menos um caso;
- regime reversal tem gap > 0;
- 10 teoremas reportados e kernel-checked;
- gate aceita 4/4 alegações;
- `hardware_executed=False`.

## 4. Limites

Counts sintéticos; correlação de pares apenas; custo proxy; sem agendamento,
calibração real ou hardware. O pareamento alegação↔contraprova é editorial.
Nenhum resultado prova vantagem quântica ou superioridade em hardware.
