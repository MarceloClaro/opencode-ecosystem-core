# Verificação com números complexos — Lean 4 + Mathlib (R1146)

**Data:** 2026-11-10
**Arquivo formal:** `lean/quantum-cb/ComplexProofs.lean`
**Gate:** `quantum_mitigation/complex_proof_gate.py`
**Certificado:** `harnesses/quantum-error-mitigation/resultados/r1146_complex_proofs/certificate.json`

## 1. Por que complexos

Os pilotos anteriores usavam matrizes racionais e identidades finitas. Uma
inovação em mitigação quântica, porém, quase sempre envolve **amplitudes
complexas**: fase global, fase relativa, interferência, conjugação e
normalização. O Core agora verifica essas identidades diretamente em `ℂ`,
com prova e contraprova, em vez de reduzi-las a inteiros.

## 2. O que foi provado

Compilação real com Lean v4.34.1 + Mathlib, retorno **0**. Todos os teoremas
dependem apenas dos axiomas padrão `propext`, `Classical.choice` e
`Quot.sound`; **nenhum** usa `sorryAx`, `native_decide` ou `axiom`.

| Teorema | Enunciado | Status |
|---|---|---|
| `normSq_global_phase` | `‖e^{iθ} z‖² = ‖z‖²` | kernel-checked |
| `normSq_conj` | `‖conj z‖² = ‖z‖²` | kernel-checked |
| `born_nonneg` | `0 ≤ ‖z‖²` | kernel-checked |
| `born_le_one` | estado normalizado ⇒ `‖α‖² ≤ 1` | kernel-checked |
| `interference` | `‖e^{ia}+e^{ib}‖² = 2 + 2cos(a−b)` | kernel-checked |
| `phaseGate_unitary` | `diag(1, e^{iθ}) · diag(1, e^{iθ})ᴴ = 1` | kernel-checked |

## 3. Contraprovas

| Teorema | O que falsifica |
|---|---|
| `relative_phase_not_one` | `e^{iπ} ≠ 1`: fase relativa não é fase global trivial |
| `scaling_changes_normSq` | dobrar a amplitude muda `‖z‖²`; não é mitigação unitária |
| `no_negative_normSq` | não existe `z` com `‖z‖² = −1`: probabilidade negativa é impossível |

As contraprovas não são comentários: são teoremas compilados e auditados pelo
mesmo gate.

## 4. Gate de inovação

```bash
python3 quantum_mitigation/complex_proof_gate.py
```

O gate:

1. remove comentários e verifica `sorry`, `admit` e `axiom`;
2. compila com `lake env lean`;
3. lê `#print axioms`;
4. classifica cada teorema (`kernel_checked`, `native`, `blocked`,
   `review_required`);
5. exige que cada alegação tenha **teorema + contraprova nomeada**;
6. grava certificado com SHA-256 do `.lean` e do log.

Regras fail-closed:

- `sorryAx` → `blocked`;
- axioma nativo → `native` e gate **não aceito**;
- teorema ausente ou não reportado → gate **não aceito**;
- alegação sem contraprova → gate **não aceito**;
- sem `lake` → `blocked`, nunca `machine_checked`.

## 5. Resultado desta rodada

| Item | Resultado |
|---|---|
| Compilação | retorno 0 (~18 s com cache quente) |
| Teoremas auditados | 9 |
| Kernel-checked | 9 |
| Axiomas nativos | 0 |
| Alegações aceitas | 4/4 |
| Alegações bloqueadas | 0 |
| SHA-256 do certificado | `5bdad31fe568f8141b221ff4db4df2bbf50bad7f4da4f08ba687fdc86fb46168` |

## 6. Limites

- Prova **algébrica**; não prova hardware, calibração, ruído, canal quântico,
  twirl, fidelidade ou vantagem quântica.
- O pareamento alegação↔contraprova é editorial e exige revisão humana.
- O gate aceitar não promove confiança, não valida eficácia e não autoriza
  execução.
- A interferência é uma identidade de duas fases ideais; não modela ruído.
- A porta de fase é unitária ideal; não representa pulsos reais.

## 7. Reprodução

```bash
# compilação direta
cd livro-core/lean
lake env lean ../../lean/quantum-cb/ComplexProofs.lean

# gate + certificado
cd ../..
python3 quantum_mitigation/complex_proof_gate.py

# teste pesado dedicado
RUN_LEAN_COMPLEX=1 .venv-quantum/bin/python \
  -m pytest tests/test_r1146_complex_proof_gate.py -q
```
