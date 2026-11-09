# SPEC-935-R1124 — Repetição da leitura com mitigação em dois conjuntos

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1116, R1120

## 1. Contexto

O operador pediu repetir a leitura com mitigação em dois conjuntos e verificar
o gate r1 ≤ 0,05. A leitura tem duas camadas distintas:

- **r1 físico**: probabilidade de medir 0 dado que |1> foi preparado; é uma
  propriedade do hardware.
- **TVD mitigada**: efeito residual após aplicar a matriz de calibração; é uma
  métrica de software.

Mitigação de leitura reduz o efeito, mas não reduz o r1 físico.

## 2. Requisitos

- **R1.** Ler o run original e os dois conjuntos novos.
- **R2.** Comparar baseline vs otimizado em TVD mitigada.
- **R3.** Reportar qubits físicos usados por cada layout.
- **R4.** Verificar estabilidade do sinal entre runs.
- **R5.** Manter a decisão de não comparar layouts quando o sinal não for
  estável ou os qubits forem diferentes.
- **R6.** Declarar que mitigação ≠ correção do r1 físico.
- **R7.** Não executar hardware na análise.
- **R8.** Testes de consistência.

## 3. Resultado

| Run | Baseline TVD | Otimizado TVD | Δ | Qubits baseline | Qubits otimizado |
|---|---:|---:|---:|---|---|
| original | 0,0249 | 0,0277 | +0,0028 | [0,1] | [106,107] |
| set1 | 0,0263 | 0,0153 | −0,0110 | [0,1] | [106,107] |
| set2 | 0,0228 | 0,0079 | −0,0149 | [0,1] | [106,107] |

- Sinal estável: **não**.
- Qubits físicos diferentes: **sim**.
- Decisão: **não comparar layouts agora**.

## 4. Critérios de aceitação

- JSON com 3 runs e resumo;
- decisão `False` com razões;
- relatório com “mitigação ≠ correção do readout”;
- testes R1124 passam;
- nenhum hardware, segredo ou overclaim.
