# Verificação formal em Lean 4 {#lean-quantum}

As identidades matemáticas usadas nas trilhas foram formalizadas em **Lean 4 +
Mathlib**. O arquivo é `livro-core/lean/QuantumTrails.lean`. Ele compila sem
`sorry` e sem `admit` no ambiente desta edição (Lean 4.35.0; Mathlib no commit
`d13f23b723b8a846827a245b89c10fc7d3f11612`).

## O que o Lean prova

| Teorema | O que prova | Onde é usado |
|---|---|---|
| `H_mul_H` | `H² = I` | Circuitos, interferência |
| `X_mul_X` | `X² = I` | Porta X, NOT quântico |
| `Z_mul_Z` | `Z² = I` | Fase, H-Z-H |
| `H_mul_Z_mul_H` | `H Z H = X` | Interferência e base X |
| `sqrt2_sq` | `(√2)² = 2` | Normalização, CHSH |
| `inv_sqrt2_sq` | `(1/√2)² = 1/2` | Hadamard |
| `quantum_chsh_sq` | `(2√2)² = 8` | Limite quântico de CHSH |
| `prob_sum` | `P(0)+P(1)=1` | Medição |
| `chsh_classical` | `S ≤ 2` para modelo local determinístico | Contraste clássico |
| `cnot` | Tabela-verdade do CNOT | Circuitos |
| `cnot_involutive` | CNOT aplicado duas vezes devolve a entrada | Circuitos |
| `bell_normalized` | Estado de Bell normalizado | Emaranhamento |
| `chsh_bell_eigen` | CHSH|Φ+⟩ = 2√2|Φ+⟩ | Valor quântico de CHSH |
| `chsh_bell_expectation` | ⟨CHSH⟩ = 2√2 no estado de Bell | Valor quântico de CHSH |
| `phaseDamping_p0` | Phase damping preserva a população | Ruído de fase |
| `phaseDamping_coh` | Coerência decai por (1−γ) | Ruído de fase |
| `phaseDamping_coh_abs_le` | Phase damping não aumenta a coerência | Ruído de fase |
| `depolarizing_p0` | Fórmula da população sob depolarizing | Ruído depolarizante |
| `depolarizing_zero` | p=0 devolve o estado original | Ruído depolarizante |
| `depolarizing_one_p0` | p=1 leva a população a 1/2 | Ruído depolarizante |
| `depolarizing_p0_nonneg` | População permanece ≥ 0 | Normalização |
| `depolarizing_p0_le_one` | População permanece ≤ 1 | Normalização |

O teorema `chsh_classical` percorre as 16 combinações de escolhas de Alice e
Bob e verifica que `a0·b0 + a0·b1 + a1·b0 − a1·b1 ≤ 2`. O valor quântico
`2√2` é formalizado para o estado de Bell e para as escolhas de observáveis
usadas no livro: `chsh_bell_eigen` prova que `|Φ+⟩` é autovetor de `CHSH` com
autovalor `2√2`, e `chsh_bell_expectation` prova o valoresperado. O limite de
Tsirelson geral não é formalizado; o que está provado é o caso específico.

Os modelos de ruído são **fenomenológicos**: `phaseDamping` e `depolarizing`
atuam sobre população e coerência real de um qubit. Eles provam preservação de
população, decaimento de coerência e normalização, mas **não** são uma
formalização completa de canais CPTP.

## O que o Lean não prova

- counts de hardware, calibração, fidelidade, ruído;
- a interpretação de Bohm;
- a vantagem quântica de um algoritmo específico;
- a validade de uma execução ou de um backend.

Essas afirmações são empíricas e dependem de dados, task IDs e desenho
experimental. O Lean prova a matemática; o experimento prova (ou não) a física.

## Como verificar

Pré-requisitos: `elan` e o projeto `livro-core/lean` com Mathlib.

```bash
cd livro-core/lean
lake env lean QuantumTrails.lean
```

Se o comando terminar sem mensagens de erro, os teoremas foram verificados pelo
compilador. Se você não tem Lean instalado, a tabela acima e a explicação do
texto bastam para a leitura; o código é para quem quiser conferir a prova.

## Código Lean completo {#lean-codigo}

```lean
/-
  QuantumTrails.lean

  Verificação formal, em Lean 4 + Mathlib, das identidades matemáticas
  usadas nas trilhas do livro *Do Bit ao Todo*.

  O que este arquivo prova:
  - H² = I, X² = I, Z² = I;
  - H Z H = X;
  - (1/√2)² = 1/2 e (2√2)² = 8;
  - P(0) + P(1) = 1 para uma distribuição normalizada em Fin 2;
  - o limite clássico de CHSH: S ≤ 2 para um modelo local determinístico;
  - a tabela-verdade do CNOT.

  O que este arquivo NÃO prova:
  - counts de hardware, calibração, fidelidade ou ruído;
  - a interpretação de Bohm;
  - a vantagem quântica de um algoritmo específico.

  Verificação:
    lake env lean QuantumTrails.lean
-/

import Mathlib

open Matrix Complex
open scoped Matrix

noncomputable section

namespace QuantumTrails

/-- Matriz de Hadamard com parâmetro `h`; no livro, `h = 1/√2`. -/
def H (h : ℂ) : Matrix (Fin 2) (Fin 2) ℂ :=
  !![h, h; h, -h]

/-- Porta X (NOT quântico). -/
def X : Matrix (Fin 2) (Fin 2) ℂ :=
  !![0, 1; 1, 0]

/-- Porta Z (fase). -/
def Z : Matrix (Fin 2) (Fin 2) ℂ :=
  !![1, 0; 0, -1]

/-- H² = I, desde que h² = 1/2. -/
theorem H_mul_H (h : ℂ) (hh : h * h = (1 / 2 : ℂ)) :
    H h * H h = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [H, Matrix.mul_apply, Fin.sum_univ_two, hh] <;>
    ring

/-- X² = I. -/
theorem X_mul_X : X * X = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [X, Matrix.mul_apply, Fin.sum_univ_two]

/-- Z² = I. -/
theorem Z_mul_Z : Z * Z = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Z, Matrix.mul_apply, Fin.sum_univ_two]

/-- H Z H = X, desde que h² = 1/2. -/
theorem H_mul_Z_mul_H (h : ℂ) (hh : h * h = (1 / 2 : ℂ)) :
    H h * Z * H h = X := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [H, Z, X, Matrix.mul_apply, Fin.sum_univ_two, hh] <;>
    ring

/-- O quadrado de √2 é 2. -/
theorem sqrt2_sq : Real.sqrt 2 * Real.sqrt 2 = 2 := by
  rw [Real.mul_self_sqrt]
  norm_num

/-- O quadrado de 1/√2 é 1/2. -/
theorem inv_sqrt2_sq :
    ((1 / (Real.sqrt 2 : ℂ)) * (1 / (Real.sqrt 2 : ℂ))) = (1 / 2 : ℂ) := by
  have h2 : (Real.sqrt 2 : ℂ) * (Real.sqrt 2 : ℂ) = 2 := by
    norm_cast
    exact sqrt2_sq
  field_simp [h2]
  rw [pow_two, h2]

/-- (2√2)² = 8. -/
theorem quantum_chsh_sq : (2 * Real.sqrt 2) ^ 2 = 8 := by
  have h : (Real.sqrt 2) ^ 2 = 2 := by
    rw [pow_two, sqrt2_sq]
  rw [mul_pow, h]
  norm_num

/-- A soma das probabilidades de uma distribuição em Fin 2 é 1. -/
theorem prob_sum (p : Fin 2 → ℝ) (hp : ∑ i, p i = 1) :
    p 0 + p 1 = 1 := by
  simpa [Fin.sum_univ_two] using hp

/-- Sinal clássico: `true ↦ +1`, `false ↦ -1`. -/
def s : Bool → ℝ
  | true => 1
  | false => -1

/-- Limite clássico de CHSH para um modelo local determinístico.
    As quatro escolhas de Alice e Bob são variáveis booleanas; o valor
    `S = a0*b0 + a0*b1 + a1*b0 - a1*b1` nunca passa de 2. -/
theorem chsh_classical (a0 a1 b0 b1 : Bool) :
    s a0 * s b0 + s a0 * s b1 + s a1 * s b0 - s a1 * s b1 ≤ 2 := by
  cases a0 <;> cases a1 <;> cases b0 <;> cases b1 <;>
    norm_num [s]

/-- CNOT com controle e alvo booleanos. -/
def cnot (x : Bool × Bool) : Bool × Bool :=
  (x.1, x.1 != x.2)

example : cnot (false, false) = (false, false) := rfl
example : cnot (false, true) = (false, true) := rfl
example : cnot (true, false) = (true, true) := rfl
example : cnot (true, true) = (true, false) := rfl

/-- O CNOT é involutivo: aplicar duas vezes devolve a entrada. -/
theorem cnot_involutive (x : Bool × Bool) : cnot (cnot x) = x := by
  rcases x with ⟨c, t⟩
  cases c <;> cases t <;> rfl

/-- Estado de Bell (|00⟩ + |11⟩)/√2 como vetor de amplitudes em Fin 4. -/
def bell : Fin 4 → ℂ
  | 0 => (1 / (Real.sqrt 2 : ℂ))
  | 1 => 0
  | 2 => 0
  | 3 => (1 / (Real.sqrt 2 : ℂ))

/-- O estado de Bell é normalizado: a soma dos módulos ao quadrado é 1. -/
theorem bell_normalized :
    (∑ i : Fin 4, Complex.normSq (bell i)) = 1 := by
  simp [bell, Fin.sum_univ_four]
  norm_num

/-- s = 1/√2 -/
def invSqrt2 : ℝ := 1 / Real.sqrt 2

/-- A0 = Z ⊗ I -/
def A0 : Matrix (Fin 4) (Fin 4) ℝ :=
  !![1, 0, 0, 0;
     0, 1, 0, 0;
     0, 0, -1, 0;
     0, 0, 0, -1]

/-- A1 = X ⊗ I -/
def A1 : Matrix (Fin 4) (Fin 4) ℝ :=
  !![0, 0, 1, 0;
     0, 0, 0, 1;
     1, 0, 0, 0;
     0, 1, 0, 0]

/-- B0 = I ⊗ (Z + X)/√2 -/
def B0 : Matrix (Fin 4) (Fin 4) ℝ :=
  !![invSqrt2, invSqrt2, 0, 0;
     invSqrt2, -invSqrt2, 0, 0;
     0, 0, invSqrt2, invSqrt2;
     0, 0, invSqrt2, -invSqrt2]

/-- B1 = I ⊗ (Z - X)/√2 -/
def B1 : Matrix (Fin 4) (Fin 4) ℝ :=
  !![invSqrt2, -invSqrt2, 0, 0;
     -invSqrt2, -invSqrt2, 0, 0;
     0, 0, invSqrt2, -invSqrt2;
     0, 0, -invSqrt2, -invSqrt2]

/-- Operador CHSH. -/
def CHSHOp : Matrix (Fin 4) (Fin 4) ℝ :=
  A0 * B0 + A0 * B1 + A1 * B0 - A1 * B1

/-- Estado de Bell (|00⟩ + |11⟩)/√2. -/
def bellR : Fin 4 → ℝ
  | 0 => invSqrt2
  | 1 => 0
  | 2 => 0
  | 3 => invSqrt2

/-- O operador CHSH tem |Φ+⟩ como autovetor com autovalor 2√2. -/
theorem chsh_bell_eigen :
    CHSHOp *ᵥ bellR = (2 * Real.sqrt 2) • bellR := by
  ext i
  fin_cases i <;>
    simp [CHSHOp, A0, A1, B0, B1, bellR, invSqrt2, Matrix.mulVec, dotProduct,
          Fin.sum_univ_four] <;>
    field_simp [Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)] <;>
    norm_num [Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)]




/-- Valor esperado de CHSH no estado de Bell: 2√2. -/
theorem chsh_bell_expectation :
    (∑ i : Fin 4, bellR i * (CHSHOp *ᵥ bellR) i) = 2 * Real.sqrt 2 := by
  rw [chsh_bell_eigen]
  simp [bellR, invSqrt2, Fin.sum_univ_four]
  field_simp [Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)]
  norm_num [Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)]




/-- Estado reduzido de um qubit: população de |0⟩ e coerência real. -/
structure QubitNoiseState where
  p0 : ℝ
  coh : ℝ

/-- Phase damping: preserva a população e atenua a coerência. -/
def phaseDamping (γ : ℝ) (ρ : QubitNoiseState) : QubitNoiseState :=
  { p0 := ρ.p0, coh := (1 - γ) * ρ.coh }

/-- Depolarizing: mistura a população com 1/2 e atenua a coerência. -/
def depolarizing (p : ℝ) (ρ : QubitNoiseState) : QubitNoiseState :=
  { p0 := (1 - p) * ρ.p0 + p / 2, coh := (1 - p) * ρ.coh }

theorem phaseDamping_p0 (γ : ℝ) (ρ : QubitNoiseState) :
    (phaseDamping γ ρ).p0 = ρ.p0 := rfl

theorem phaseDamping_coh (γ : ℝ) (ρ : QubitNoiseState) :
    (phaseDamping γ ρ).coh = (1 - γ) * ρ.coh := rfl

theorem depolarizing_p0 (p : ℝ) (ρ : QubitNoiseState) :
    (depolarizing p ρ).p0 = (1 - p) * ρ.p0 + p / 2 := rfl

theorem depolarizing_zero (ρ : QubitNoiseState) :
    depolarizing 0 ρ = ρ := by
  cases ρ
  simp [depolarizing]

theorem depolarizing_one_p0 (ρ : QubitNoiseState) :
    (depolarizing 1 ρ).p0 = 1 / 2 := by
  simp [depolarizing]

theorem depolarizing_p0_nonneg (p : ℝ) (ρ : QubitNoiseState)
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (h0 : 0 ≤ ρ.p0) (h1 : ρ.p0 ≤ 1) :
    0 ≤ (depolarizing p ρ).p0 := by
  simp [depolarizing]
  nlinarith

theorem depolarizing_p0_le_one (p : ℝ) (ρ : QubitNoiseState)
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (h0 : 0 ≤ ρ.p0) (h1 : ρ.p0 ≤ 1) :
    (depolarizing p ρ).p0 ≤ 1 := by
  simp [depolarizing]
  nlinarith

theorem phaseDamping_coh_abs_le (γ : ℝ) (ρ : QubitNoiseState)
    (hγ0 : 0 ≤ γ) (hγ1 : γ ≤ 1) :
    |(phaseDamping γ ρ).coh| ≤ |ρ.coh| := by
  simp [phaseDamping]
  have h : |1 - γ| ≤ 1 := by
    rw [abs_le]
    constructor <;> linarith
  calc
    |1 - γ| * |ρ.coh| ≤ 1 * |ρ.coh| :=
      mul_le_mul_of_nonneg_right h (abs_nonneg _)
    _ = |ρ.coh| := by ring

end QuantumTrails
```

> **Regra:** não declare “provado” o que o compilador não verificou. O status
> deste arquivo é: compilado nesta edição com o comando acima. Se você alterar
> o código, o status volta a “não verificado” até nova compilação.
