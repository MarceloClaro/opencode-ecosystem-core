# SPEC-935-R1116 — Scorecard híbrido de resiliência quântica

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1114 (QEM/QEC), R1115 (protocolos de hardware)

## 1. Contexto

As técnicas de mitigação não são intercambiáveis: readout 4×4, tomografia SPAM,
ZNE, PEC, superfície e DD pulse-level têm pré-requisitos e limites diferentes.
O operador pediu resiliência híbrida/multitécnica capaz de apontar o próximo
passo efetivo, em vez de somar técnicas como se fossem equivalentes.

Esta spec cria um **scorecard heurístico** que lê evidências reais e recomenda
prioridades, bloqueios e limites.

## 2. Requisitos

- **R1.** Combinar evidências de readout 4×4, tomografia q0/q1, ZNE, PEC e
  incerteza bootstrap.
- **R2.** Produzir `status`, `findings`, `recommendations`, `blocked` e
  `limits`.
- **R3.** Bloquear ZNE quando a curva não for monotônica.
- **R4.** Bloquear PEC 2q quando o orçamento de amostragem for proibitivo.
- **R5.** Recomendar state preparation/leitura quando q1 for pior que q0.
- **R6.** Recomendar mais repetições quando a largura do IC exceder 0,01.
- **R7.** Expor o comando `resilience` no harness e no wrapper do agente.
- **R8.** Não executar hardware e não declarar vantagem quântica.
- **R9.** Testes com artefatos reais e sintéticos.
- **R10.** Documentar que o scorecard é heurístico, não um certificado.

## 3. Entradas

| Evidência | Formato |
|---|---|
| readout 4×4 | `comparacao.json` com `baseline`/`optimized` mitigados |
| ZNE | `zne.json` com `applicability` |
| tomografia q0 | `tomography.json` com `prep_fidelity` e readout |
| tomografia q1 | `comparison.json` com `q1.fit_combined` e bootstrap |
| PEC | `resultado.json` com `gamma_total` e `samples_required` |
| incerteza | bootstrap com ICs |
| superfície/pulse DD | flags de planejamento |

## 4. Critérios de aceitação

- scorecard identifica ZNE bloqueado no run atual;
- identifica q1 com menor fidelidade e maior r1;
- recomenda não comparar layouts antes de melhorar state preparation;
- bloqueia superfície e DD pulse-level;
- comando `resilience` gera JSON/Markdown;
- agente tem permissão para `resilience*`;
- testes R1116 passam;
- nenhuma chave ou overclaim.

## 5. Revisão 2026-11-09 (R1117)

O run simétrico com dois conjuntos de q0 mostrou que:

- o Δ q1−q0 em `prep |1>` é −0,0072 e em `r1` é +0,0072;
- os ICs bootstrap se sobrepõem e o Δ é menor que o spread entre conjuntos;
- portanto a diferença **não é conclusiva**;
- `prep |0>` = 1 − r0 e `prep |1>` = 1 − r1 neste desenho: o scorecard não
  deve tratar preparação e leitura como duas evidências independentes.

O scorecard v2 (R1117) usa `prep coerente` (|+>, |+i>) para preparação
independente de readout e declara explicitamente a redundância. O critério de
aceitação original "identifica q1 com menor fidelidade e maior r1" passa a ser
"identifica a direção, sem declarar diferença conclusiva".

## 6. Não objetivos

- Certificar qualidade quântica.
- Somar técnicas como se fossem independentes.
- Executar hardware.
- Declarar vantagem, threshold ou fidelidade.
