import Mathlib

/-!
# Provas e contraprovas com números complexos (R1146)

Este arquivo verifica, com Lean 4 + Mathlib, identidades algébricas de
amplitudes complexas usadas em mitigação e em gates de inovação:

- fase global preserva `normSq`;
- conjugação preserva `normSq`;
- probabilidade de Born é não negativa e limitada por 1;
- interferência de duas fases unitárias;
- porta de fase é unitária;
- contraprovas: fase relativa é observável, uma porta escalada não é unitária
  e probabilidade negativa é impossível.

O arquivo NÃO prova hardware, calibração, modelo de ruído, canal quântico,
vantagem quântica ou qualquer resultado experimental. Todas as provas são
kernel-checked; não há `sorry`, `admit`, `axiom` nem `native_decide`.
-/

open Complex Matrix

namespace CoreComplex

/-- Fase global não altera o módulo ao quadrado. -/
theorem normSq_global_phase (θ : ℝ) (z : ℂ) :
    Complex.normSq (Complex.exp (θ * Complex.I) * z) = Complex.normSq z := by
  rw [map_mul, Complex.normSq_eq_norm_sq, Complex.norm_exp_ofReal_mul_I,
    one_pow, one_mul]

/-- Conjugação complexa preserva o módulo ao quadrado. -/
theorem normSq_conj (z : ℂ) :
    Complex.normSq (starRingEnd ℂ z) = Complex.normSq z := by
  simp [Complex.normSq_apply]

/-- Probabilidade de Born é não negativa. -/
theorem born_nonneg (z : ℂ) : 0 ≤ Complex.normSq z :=
  Complex.normSq_nonneg z

/-- Em estado normalizado, cada probabilidade de Born é no máximo 1. -/
theorem born_le_one (α β : ℂ)
    (h : Complex.normSq α + Complex.normSq β = 1) :
    Complex.normSq α ≤ 1 := by
  have hβ : 0 ≤ Complex.normSq β := Complex.normSq_nonneg β
  linarith

/-- Interferência de duas fases unitárias: `|e^{ia}+e^{ib}|² = 2+2cos(a-b)`. -/
theorem interference (a b : ℝ) :
    Complex.normSq (Complex.exp (a * Complex.I) + Complex.exp (b * Complex.I)) =
      2 + 2 * Real.cos (a - b) := by
  rw [Complex.normSq_add]
  have ha : Complex.normSq (Complex.exp (a * Complex.I)) = 1 := by
    rw [Complex.normSq_eq_norm_sq, Complex.norm_exp_ofReal_mul_I, one_pow]
  have hb : Complex.normSq (Complex.exp (b * Complex.I)) = 1 := by
    rw [Complex.normSq_eq_norm_sq, Complex.norm_exp_ofReal_mul_I, one_pow]
  rw [ha, hb]
  have hc : (starRingEnd ℂ) (Complex.exp (b * Complex.I)) =
      Complex.exp ((-b) * Complex.I) := by
    rw [← Complex.exp_conj]
    congr 1
    simp
  rw [hc, ← Complex.exp_add]
  have harg : a * Complex.I + (-b) * Complex.I = (a - b) * Complex.I := by ring
  rw [harg, ← Complex.ofReal_sub, Complex.exp_ofReal_mul_I_re]
  ring

/-- Porta de fase `diag(1, e^{iθ})`. -/
noncomputable def phaseGate (θ : ℝ) : Matrix (Fin 2) (Fin 2) ℂ :=
  !![1, 0; 0, Complex.exp (θ * Complex.I)]

/-- A porta de fase é unitária. -/
theorem phaseGate_unitary (θ : ℝ) :
    phaseGate θ * (phaseGate θ)ᴴ = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [phaseGate, Matrix.mul_apply, Complex.mul_conj,
      Complex.normSq_eq_norm_sq, Complex.norm_exp_ofReal_mul_I]

/-- Contraprova: dobrar a amplitude não preserva a probabilidade. -/
theorem scaling_changes_normSq :
    Complex.normSq ((2 : ℂ) * 1) ≠ Complex.normSq (1 : ℂ) := by
  norm_num [Complex.normSq_apply]

/-- Contraprova: fase relativa não é uma fase global trivial. -/
theorem relative_phase_not_one :
    Complex.exp (Real.pi * Complex.I) ≠ 1 := by
  rw [Complex.exp_pi_mul_I]
  norm_num

/-- Contraprova: nenhuma probabilidade de Born pode ser negativa. -/
theorem no_negative_normSq :
    ¬ ∃ z : ℂ, Complex.normSq z = -1 := by
  rintro ⟨z, hz⟩
  have h := Complex.normSq_nonneg z
  linarith

end CoreComplex

#print axioms CoreComplex.normSq_global_phase
#print axioms CoreComplex.normSq_conj
#print axioms CoreComplex.born_nonneg
#print axioms CoreComplex.born_le_one
#print axioms CoreComplex.interference
#print axioms CoreComplex.phaseGate_unitary
#print axioms CoreComplex.scaling_changes_normSq
#print axioms CoreComplex.relative_phase_not_one
#print axioms CoreComplex.no_negative_normSq
