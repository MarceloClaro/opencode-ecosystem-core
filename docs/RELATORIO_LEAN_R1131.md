# R1131 — Contraprova Lean 4 dos invariantes do CB

**Status:** compilação local verificada.
**Arquivo:** `lean/quantum-cb/QuantumCB.lean`.
**Comando:** `cd lean/quantum-cb && lean QuantumCB.lean`.

## O que foi provado

| Teorema | Conteúdo |
|---|---|
| `D_mul_R` | `D` (13×15) tem inversa à direita `R` (15×13); as 13 funções são independentes |
| `B_mul_D_transpose` | a incidência `B` (4×15) anula as 13 linhas de `D` |
| `C_mul_D_transpose` | as 2 linhas de corte são ortogonais às 13 funções |
| `C_independent` | as 2 linhas de corte têm menor 2×2 não nulo |
| `design_rows` | `7 + 6 = 13` |
| `cycle_rank` | `15 − 4 + 2 = 13` |
| `cut_rank` | `4 − 2 = 2` |

O arquivo é Lean 4 core, sem Mathlib. Compilou com `lean` 4.35, retorno 0.
`compile.log` registra os axiomas.

## O que o Lean não prova

- O canal quântico, a matriz densidade, a exponencial e a recuperação numérica.
- Twirl/frame, ruído das correções, compilação ou Baihua.
- Identificação das 2 funções de corte sem hipótese adicional.
- Validade experimental do protocolo.

## Axiomas

As quatro identidades matriciais usam `native_decide`; dependem de
`propext`, `Classical.choice`, `Quot.sound` e do axioma de avaliação nativa
`..._native.native_decide.ax_1_1`. As três contagens não dependem de axiomas
adicionais. Portanto, a contraprova é uma verificação finita assistida por
Lean, **não** uma prova kernel-only das identidades matriciais.

## Reprodução

```bash
cd lean/quantum-cb
lean QuantumCB.lean
sha256sum -c SHA256SUMS
```

Teste Python: `tests/test_r1131_lean_counterproof.py` (pula a compilação se
`lean` não estiver instalado).
