# SPEC-935-R1136 — Contraprova Mathlib dedicada

**Status:** compilada com Mathlib, retorno 0
**Data:** 2026-11-10
**Depende de:** R1131
**Arquivo:** `lean/quantum-cb/MathlibCounterproof.lean`

## 1. Objetivo

Repetir a contraprova finita do CB com Mathlib, incluindo o posto via API
`Matrix.rank`, e registrar os axiomas usados.

## 2. Resultado

- `D_mul_R`: `D` 13×15 tem inversa à direita `R` 15×13;
- `rank_D`: `D.rank = 13` via `Matrix.rank_le_height` e
  `Matrix.rank_mul_le_left`;
- `B_mul_D_transpose = 0`;
- `C_mul_D_transpose = 0`;
- `C_independent`: menor 2×2 não nulo;
- contagens 13/2.

Compilação:

```bash
cd livro-core/lean
lake env lean ../../lean/quantum-cb/MathlibCounterproof.lean
```

Retorno 0. Log: `lean/quantum-cb/mathlib_compile.log`.

## 3. Axiomas

As identidades matriciais usam `native_decide`; `D_mul_R` tem 338 axiomas
nativos associados e `C_independent` tem um. `rank_D` usa Mathlib, mas depende
de `D_mul_R`. As contagens são livres de axiomas adicionais. Portanto, é uma
prova assistida por Mathlib, **não kernel-only** para as identidades.

## 4. O que não é provado

- Canal quântico, matriz densidade, exponencial e recuperação numérica.
- Twirl/frame, ruído das correções, compilação ou Baihua.
- Identificação das 2 funções de corte sem hipótese.
- Validade experimental do protocolo.

## 5. Critérios

- arquivo compila com retorno 0;
- `rank_D` presente e dependente de `D_mul_R`;
- log de axiomas presente;
- sem `sorry`/`admit`;
- README declara escopo e limites;
- teste Python padrão não recompila; job dedicado via
  `RUN_MATHLIB_PROOF=1`.
