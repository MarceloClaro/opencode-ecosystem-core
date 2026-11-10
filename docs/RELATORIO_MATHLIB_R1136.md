# R1136 — Contraprova Mathlib dedicada

**Status:** compilação verificada; retorno 0.
**Arquivo:** `lean/quantum-cb/MathlibCounterproof.lean`.
**Log:** `lean/quantum-cb/mathlib_compile.log`.

## O que foi provado

| Teorema | Conteúdo |
|---|---|
| `D_mul_R` | `D` 13×15 tem inversa à direita `R` 15×13 |
| `rank_D` | `D.rank = 13` via `Matrix.rank_le_height` e `Matrix.rank_mul_le_left` |
| `B_mul_D_transpose` | `B` anula `D` |
| `C_mul_D_transpose` | `C` anula `D` |
| `C_independent` | menor 2×2 não nulo |
| `design_rows` | `7 + 6 = 13` |
| `cycle_rank` | `15 − 4 + 2 = 13` |
| `cut_rank` | `4 − 2 = 2` |

O job dedicado compilou com `lake env lean` e retorno 0. O `import Mathlib`
foi o gargalo; o cache de 6,7 GB/8.908 arquivos foi usado.

## Axiomas

As identidades matriciais usam `native_decide`:

- `D_mul_R` tem 338 axiomas nativos associados;
- `C_independent` tem um;
- `rank_D` usa Mathlib, mas depende de `D_mul_R`;
- as contagens são livres de axiomas adicionais.

Portanto, é uma prova **assistida por Mathlib**, não kernel-only para as
identidades. O Lean 4 core (`QuantumCB.lean`) continua sendo a contraprova
leve e reprodutível.

## O que não é provado

- Canal quântico, simulação por matriz densidade, exponencial e recuperação
  numérica.
- Twirl/frame, ruído das correções, compilação ou Baihua.
- Identificação das 2 funções de corte sem hipótese.
- Validade experimental do protocolo.

## Reprodução

```bash
cd livro-core/lean
lake env lean ../../lean/quantum-cb/MathlibCounterproof.lean
```

Teste padrão: `pytest tests/test_r1136_mathlib_counterproof.py -q`
(compilação pesada só com `RUN_MATHLIB_PROOF=1`).

## Limites

Mathlib não transforma a simulação em prova física. A prova vale para as
matrizes finitas; os gates PEC/ZNE/layout continuam dependentes de dados.
