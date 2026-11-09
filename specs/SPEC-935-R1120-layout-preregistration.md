# SPEC-935-R1120 — Pré-registro de n e gates para comparação de layouts

**Status:** implementação local
**Data:** 2026-11-09
**Depende de:** R1116/R1117 (scorecard e comparação simétrica)

## 1. Contexto

O operador pediu pré-registrar `n` e repetir antes de qualquer comparação de
layouts. Os dados atuais mostram:

- readout 4×4: baseline 0,0249 vs otimizado 0,0277 (TVD mitigada);
- q0/q1: prep coerente 0,9850/0,9823; r1 0,0765/0,0837;
- Δ r1 q1−q0 = +0,0072, dentro do spread entre conjuntos.

A diferença observada entre layouts (0,0028) é menor que a resolução atual.
Comparar layouts agora seria overclaim.

## 2. Requisitos

- **R1.** Calcular `n` para meia-largura 0,005, 0,01 e 0,015 com p=0,5 e 95%.
- **R2.** Definir gates de elegibilidade:
  - prep coerente ≥ 0,99 em ambos os qubits;
  - r1 ≤ 0,05 ou leitura mitigada abaixo de 0,05;
  - Δ r1 dentro do spread entre conjuntos;
  - efeito de layout pré-registrado ≥ 0,01.
- **R3.** Emitir decisão `compare_layouts_now` com razões.
- **R4.** Orçamento de jobs: 2 layouts × 4 circuitos × 2 conjuntos.
- **R5.** Incluir hash SHA-256 do conteúdo pré-registrado.
- **R6.** Não executar hardware.
- **R7.** Relatório em Markdown com a decisão e os limites.
- **R8.** Testes dos cálculos, gates, hash e ausência de overclaim.

## 3. Cálculo

Para p=0,5 e 95%:

| Meia-largura | n por circuito/layout |
|---:|---:|
| 0,005 | 38.411 |
| 0,010 | 9.600 |
| 0,015 | 4.265 |

Para comparar dois layouts, a meia-largura da diferença é aproximadamente
`√2 × meia-largura`. Com n=38.411, a diferença detectável é ~1,4%; com n=9.600,
~2,8%. O efeito de interesse pré-registrado é 1%, então o orçamento conservador
é 38.411 shots por circuito/layout.

## 4. Decisão atual

**Não comparar layouts agora.** Razões:

1. prep coerente de q0/q1 abaixo de 0,99;
2. r1 de q0/q1 acima de 0,05;
3. diferença de layout observada (0,0028) abaixo do efeito pré-registrado (0,01);
4. drift entre conjuntos não resolvido.

## 5. Critérios de aceitação

- JSON com n, gates, decisão, orçamento e hash;
- decisão `False` com razões explícitas;
- hash reproduzível;
- testes R1120 passam;
- nenhum hardware, segredo ou overclaim.
