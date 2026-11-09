# SPEC-935-R1122 — Plano de cycle benchmarking das 15 taxas Pauli-Lindblad

**Status:** planejamento local
**Data:** 2026-11-09
**Depende de:** R1119 (Pauli-frame), R1121 (literatura)

## 1. Contexto

PEC 2q exige as 15 taxas Pauli-Lindblad. Elas não podem ser inventadas a partir
de um erro escalar. O protocolo publicado é cycle benchmarking (Erhard et al.
2019; Harper et al. 2020; Flammia & Wallman 2020).

Esta spec entrega o **plano de jobs e o orçamento**, não as taxas. A execução e
o ajuste ficam para um run dedicado.

## 2. Requisitos

- **R1.** Listar os 15 Paulis não identidade de 2 qubits.
- **R2.** Definir profundidades de ciclo (1, 2, 4, 8, 16).
- **R3.** Calcular jobs: 15 × 5 × 2 conjuntos = 150.
- **R4.** Respeitar o limite de 20 submissões por processo: 8 processos.
- **R5.** Declarar pré-requisitos: RC, mitigação de leitura, `n` pré-registrado.
- **R6.** Declarar que nenhuma taxa foi medida.
- **R7.** Não executar hardware.
- **R8.** Testes de contagem, unicidade e ausência de overclaim.

## 3. Critérios de aceitação

- JSON com 15 Paulis únicos, 5 profundidades, 150 jobs, 8 processos;
- relatório com “nenhuma taxa foi medida”;
- `hardware_executed = false`;
- testes R1122 passam.
