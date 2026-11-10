# SPEC-935-R1131 — Contraprova Lean 4 dos invariantes do CB

**Status:** implementação local, sem hardware
**Data:** 2026-11-10
**Depende de:** R1128, R1129, R1130
**Arquivo:** `lean/quantum-cb/QuantumCB.lean`

## 1. Objetivo

Formalizar em Lean 4 core, sem Mathlib, os invariantes **finitos** que
sustentam a correção do posto 9 e o desenho de 13 funções:

- `D` (13×15) tem inversa à direita `R` (15×13) com entradas inteiras;
- `B` (4×15) anula as 13 linhas de `D`;
- `C` (2×15) anula as 13 linhas de `D` e tem posto 2 por menor não nulo;
- `7+6=13`, `15−4+2=13`, `4−2=2`.

## 2. O que não é formalizado

- Canal quântico, matriz densidade, exponencial e recuperação numérica.
- Twirl/frame, ruído das correções, compilação ou Baihua.
- Identificação das 2 funções de corte sem hipótese adicional.
- Validade experimental do protocolo.

## 3. Requisitos

- **R1.** Arquivo Lean 4 core compilável com `lean QuantumCB.lean`.
- **R2.** Matrizes `D`, `R`, `B`, `C` explícitas sobre `Rat`.
- **R3.** Teoremas `D_mul_R`, `B_mul_D_transpose`, `C_mul_D_transpose`,
  `C_independent`, `design_rows`, `cycle_rank`, `cut_rank`.
- **R4.** Sem `sorry`, `admit` ou `axiom` declarado pelo autor.
- **R5.** Registrar que `native_decide` usa o axioma de avaliação nativa;
  as contagens são livres de axiomas adicionais.
- **R6.** README com escopo, comando e limites.
- **R7.** Teste Python que verifica o arquivo e, se `lean` existir, compila.

## 4. Critérios de aceitação

- `lean QuantumCB.lean` retorna 0;
- os sete teoremas existem;
- nenhum `sorry`/`admit`;
- `compile.log` registra os axiomas;
- teste Python passa ou é pulado se `lean` não estiver instalado;
- nenhuma alegação de prova física ou de hardware.
