# SPEC-935-R1117 — Comparação simétrica q0/q1 e correção de dupla contagem

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1115 (tomografia), R1116 (scorecard)

## 1. Contexto

O run inicial de q1 comparou dois conjuntos de q1 contra **um** conjunto de q0.
Isso era assimétrico. O operador autorizou repetir q0 em dois conjuntos para
que a comparação fosse simétrica.

Além disso, a análise revelou que, neste desenho de tomografia:

- `prep |0>` = 1 − r0;
- `prep |1>` = 1 − r1.

Ou seja, fidelidade de preparação de |0>/|1> e erro de leitura são a **mesma
contagem Z**, não duas evidências independentes. O scorecard R1116 somava essas
duas linhas como se fossem achados distintos. Esta spec corrige isso.

## 2. Requisitos

- **R1.** Combinar dois conjuntos de q0 e dois de q1, com bootstrap de 2000
  amostras por qubit.
- **R2.** Produzir `comparison.json` por qubit e `comparison_q0_q1.json` com
  Δ = q1 − q0, ICs e spread entre conjuntos.
- **R3.** Detectar e declarar a redundância `prep |0>/|1>` ↔ `r0/r1`.
- **R4.** Medir preparação coerente independente de readout por `|+>` e `|+i>`.
- **R5.** Não declarar diferença q0/q1 quando o Δ estiver dentro do spread
  entre conjuntos e os ICs se sobrepuserem.
- **R6.** Gate de layout: não comparar layouts antes de preparação coerente
  ≥ 0,99 em ambos os qubits.
- **R7.** Gate de leitura: recomendar mitigação de leitura quando r1 > 0,05.
- **R8.** Generalizar o script de tomografia para `--qubit` e `--out-dir`,
  mantendo o nome histórico do arquivo.
- **R9.** Testes dos artefatos q0, da simulação e da análise.
- **R10.** Nenhuma chave, nenhum hardware novo nesta etapa de análise.

## 3. Resultado com os dados atuais

| Métrica | q0 (2 sets) | q1 (2 sets) | Δ (q1−q0) | ICs se sobrepõem? |
|---|---:|---:|---:|---|
| prep \|0> | 0,9839 | 0,9841 | +0,0002 | sim |
| prep \|1> | 0,9235 | 0,9163 | −0,0072 | sim |
| prep \|+> | 0,9850 | 0,9823 | −0,0027 | sim |
| prep \|+i> | 0,9854 | 0,9849 | −0,0005 | sim |
| r0 | 0,0161 | 0,0159 | −0,0002 | sim |
| r1 | 0,0765 | 0,0837 | +0,0072 | sim |

Leitura: q1 é **direcionalmente** pior em |1>/r1, mas o Δ é menor que o spread
entre conjuntos (q0: 0,0115; q1: 0,0127) e os ICs se sobrepõem. Não é conclusivo.

## 4. Critérios de aceitação

- q0 e q1 têm `n_sets = 2` nos artefatos combinados;
- `comparison_q0_q1.json` contém Δ, ICs, spread e `ci_overlap`;
- `RELATORIO_Q0_Q1.md` declara a redundância e a não conclusividade;
- scorecard não recomenda “state preparation” e “readout” como se fossem
  duas evidências independentes;
- scorecard mantém os bloqueios de ZNE, superfície e DD pulse-level;
- script `--analyze` reproduz os artefatos sem hardware;
- testes R1117 passam;
- nenhuma chave ou overclaim.

## 5. Não objetivos

- Declarar q1 definitivamente pior que q0.
- Comparar layouts.
- Substituir GST completa.
- Executar hardware nesta etapa.
