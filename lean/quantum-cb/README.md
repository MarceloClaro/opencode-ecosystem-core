# Contraprova Lean 4 — CB intercalado do CZ

Arquivo: `QuantumCB.lean`
Compilação: `lean QuantumCB.lean` (Lean 4 core; não requer Mathlib).

## O que é provado

1. `D_mul_R`: a matriz de desenho `D` (13×15) tem inversa à direita `R`
   (15×13), logo as 13 linhas são linearmente independentes.
2. `B_mul_D_transpose`: a matriz de incidência `B` (4×15) anula as 13 linhas
   de `D`; os 13 ciclos estão no espaço de ciclos.
3. `C_mul_D_transpose`: as duas linhas de corte `C` (2×15) são ortogonais às
   13 funções.
4. `C_independent`: as duas linhas de corte têm um menor 2×2 não nulo.
5. `design_rows`: `7 + 6 = 13`.
6. `cycle_rank`: `15 − 4 + 2 = 13`.
7. `cut_rank`: `4 − 2 = 2`.

## O que não é provado

- O canal quântico, a simulação por matriz densidade, o decaimento
  exponencial e a recuperação numérica das fidelidades.
- Twirl/frame, ruído das correções, compilação ou qualquer execução no Baihua.
- Que as 2 funções de corte sejam identificáveis sem hipótese adicional.
- Que o desenho seja um protocolo experimental validado.

Lean verifica identidades finitas; não substitui evidência experimental.
Não prova hardware, calibração, fidelidade, twirl ou ruído real.

## Axiomas

As identidades matriciais usam `native_decide`, que depende do axioma de
avaliação nativa do Lean (`..._native.native_decide.ax_1_1`) além dos axiomas
padrão (`propext`, `Classical.choice`, `Quot.sound`). As contagens
`design_rows`, `cycle_rank` e `cut_rank` não dependem de axiomas adicionais.
Isso está registrado em `compile.log`; não é uma prova kernel-only das
identidades matriciais.

## Reprodução

```bash
cd lean/quantum-cb
lean QuantumCB.lean
```

O arquivo imprime os axiomas usados por cada teorema.

## Prova Mathlib

Arquivo: `MathlibCounterproof.lean`.

```bash
cd livro-core/lean
lake env lean ../../lean/quantum-cb/MathlibCounterproof.lean
```

Compilou com retorno **0**. O teorema `rank_D` usa `Matrix.rank_le_height` e
`Matrix.rank_mul_le_left` do Mathlib, junto com `D_mul_R`. As identidades
`D_mul_R`, `B_mul_D_transpose`, `C_mul_D_transpose` e `C_independent` usam
`native_decide`; o log `mathlib_compile.log` mostra **338 axiomas nativos**
associados a `D_mul_R` e um para `C_independent`. Portanto, é uma prova
assistida por Mathlib, **não kernel-only** para as identidades matriciais.

O que continua não provado: canal quântico, simulação, twirl, ruído real,
hardware e identificação das 2 funções de corte.

## Provas complexas (R1146)

Arquivo: `ComplexProofs.lean`.

```bash
cd livro-core/lean
lake env lean ../../lean/quantum-cb/ComplexProofs.lean
```

Verifica, em `ℂ`: fase global (`‖e^{iθ}z‖² = ‖z‖²`), conjugação, Born não
negativo, Born ≤ 1, interferência (`2 + 2cos(a−b)`) e unitariedade da porta de
fase. Inclui contraprovas: fase relativa observável, escala de amplitude altera
`normSq` e probabilidade negativa é impossível.

Todos os 9 teoremas dependem apenas de `propext`, `Classical.choice` e
`Quot.sound`; **não** usam `native_decide`, `sorry`, `admit` ou `axiom`. O gate
`python3 quantum_mitigation/complex_proof_gate.py` compila, lê
`#print axioms`, exige uma contraprova por alegação e grava certificado com
SHA-256 em `harnesses/quantum-error-mitigation/resultados/r1146_complex_proofs/`.

Limite: prova algébrica ideal; não prova hardware, ruído, canal quântico,
calibração ou vantagem quântica.

## Correlação (R1147)

Arquivo: `CorrelationCounterproof.lean`.

```bash
cd livro-core/lean
lake env lean ../../lean/quantum-cb/CorrelationCounterproof.lean
```

Prova, em `ℚ`, que duas tabelas de erro de leitura com **as mesmas marginais**
podem ter juntas diferentes: a correlação positiva aumenta `P(0 erro)` e
`P(2 erros)`, mas diminui `P(≥1 erro)`. Inclui cotas de união e a síntese
`marginals_do_not_determine_joint`.

Os 10 teoremas são kernel-checked (`propext`, `Classical.choice`,
`Quot.sound`), sem `native_decide`. Gate:
`python3 -m quantum_mitigation.correlation_gate` (no `.venv-quantum`).
