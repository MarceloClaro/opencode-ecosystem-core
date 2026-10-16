import Mathlib

/-!
# Fundamentos adicionais do livro — R908

Este arquivo formaliza as hipóteses de independência/mensurabilidade, a
expansão logarítmica e identidades elementares. A existência dessas provas não
estabelece independência empírica, verdade de fontes, equivalência com runtime
Python nem comportamento IEEE-754. Valores numéricos usam reais exatos.
-/

namespace BookFoundations

open MeasureTheory ProbabilityTheory
open scoped ENNReal

/-- Independência conjunta dos eventos implica o produto; as massas individuais são hipóteses. -/
theorem independent_equal_event_intersection {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) [IsProbabilityMeasure μ] (n : ℕ)
    (events : Fin n → Set Ω) (p : ℝ≥0∞)
    (hIndependent : iIndepSet events μ)
    (hMass : ∀ i, μ (events i) = p) :
    μ (⋂ i, events i) = p ^ n := by
  simpa [hMass] using hIndependent.meas_biInter (Finset.univ : Finset (Fin n))

/-- O risco de pelo menos um erro é o complemento da interseção dos acertos mensuráveis. -/
theorem independent_error_probability {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) [IsProbabilityMeasure μ] (n : ℕ)
    (events : Fin n → Set Ω) (p : ℝ≥0∞)
    (hMeasurable : ∀ i, MeasurableSet (events i))
    (hIndependent : iIndepSet events μ)
    (hMass : ∀ i, μ (events i) = p) :
    μ (⋂ i, events i)ᶜ = 1 - p ^ n := by
  rw [measure_compl (MeasurableSet.iInter hMeasurable) (measure_ne_top μ _),
    measure_univ, independent_equal_event_intersection μ n events p hIndependent hMass]

/-- Ponte explícita de probabilidade em ENNReal para o valor real usado no livro. -/
theorem independent_error_probability_real {Ω : Type*} [MeasurableSpace Ω]
    (μ : Measure Ω) [IsProbabilityMeasure μ] (n : ℕ)
    (events : Fin n → Set Ω) (p : ℝ≥0∞)
    (hMeasurable : ∀ i, MeasurableSet (events i))
    (hIndependent : iIndepSet events μ)
    (hMass : ∀ i, μ (events i) = p) :
    (μ ((⋂ i, events i)ᶜ)).toReal = 1 - p.toReal ^ n := by
  have hProduct := independent_equal_event_intersection μ n events p hIndependent hMass
  have hPower : p ^ n ≤ 1 := by
    rw [← hProduct]
    exact prob_le_one
  rw [independent_error_probability μ n events p hMeasurable hIndependent hMass,
    ENNReal.toReal_sub_of_le hPower (by norm_num), ENNReal.toReal_one,
    ENNReal.toReal_pow]

/-- A união dos erros individuais é o evento complementar a todos os acertos. -/
theorem error_union_is_complement {Ω : Type*} {n : ℕ} (events : Fin n → Set Ω) :
    (⋃ i, (events i)ᶜ) = (⋂ i, events i)ᶜ := by
  simp

/-- A série convergente de log(1-x), especializada ao x=0,01 do livro. -/
theorem log_099_hasSum :
    HasSum (fun n : ℕ => ((1 / 100 : ℝ) ^ (n + 1)) / (n + 1))
      (-Real.log (99 / 100 : ℝ)) := by
  have h := Real.hasSum_pow_div_log_of_abs_lt_one (x := (1 / 100 : ℝ)) (by norm_num)
  norm_num at h ⊢
  exact h

/-- Dois termos: |log(0,99) - (-0,01005)|≤1/990000, com erro racional demonstrado. -/
theorem log_099_taylor_error :
    |Real.log (99 / 100 : ℝ) + (201 / 20000 : ℝ)| ≤ (1 / 990000 : ℝ) := by
  have h := Real.abs_log_sub_add_sum_range_le (x := (1 / 100 : ℝ))
    (by norm_num) 2
  norm_num [Finset.sum_range_succ] at h
  simpa [add_comm] using h

/-- Faixa explícita do logaritmo derivada do controle do resto, sem assumir decimal exato. -/
theorem log_099_taylor_interval :
    -(201 / 20000 : ℝ) - 1 / 990000 ≤ Real.log (99 / 100 : ℝ) ∧
      Real.log (99 / 100 : ℝ) ≤ -(201 / 20000 : ℝ) + 1 / 990000 := by
  have h := abs_le.mp log_099_taylor_error
  constructor <;> linarith

/-- Identidade exata usada antes da aproximação numérica do logaritmo. -/
theorem logarithm_power_identity (p : ℝ) (n : ℕ) :
    Real.log (p ^ n) = (n : ℝ) * Real.log p := by
  exact Real.log_pow p n

/-- Exponenciar o logaritmo recupera a potência quando a base é positiva. -/
theorem exponential_logarithm_power_identity (p : ℝ) (n : ℕ) (hp : 0 < p) :
    Real.exp ((n : ℝ) * Real.log p) = p ^ n := by
  rw [← Real.log_pow, Real.exp_log (pow_pos hp n)]

/-- A identidade exata, aplicada ao exemplo n=216 e p=99/100. -/
theorem exponential_probability_example :
    Real.exp ((216 : ℝ) * Real.log (99 / 100 : ℝ)) = (99 / 100 : ℝ) ^ 216 := by
  exact exponential_logarithm_power_identity (99 / 100) 216 (by norm_num)

/-- Equação elementar usada no exemplo de ferramenta simbólica. -/
theorem linear_equation_iff (x : ℝ) : 2 * x + 1 = 5 ↔ x = 2 := by
  constructor <;> intro h <;> linarith

/-- Fatoração por diferença de quadrados. -/
theorem difference_of_squares_factorization (x : ℝ) :
    x ^ 2 - 1 = (x - 1) * (x + 1) := by
  ring

/-- Verificação exata da soma simples; não é teste do interpretador Python. -/
theorem simple_sum_exact : (2 : ℝ) + 3 = 5 := by
  norm_num

/-- Derivação da primitiva -cos(x)+C para qualquer constante real. -/
theorem sine_antiderivative (x c : ℝ) :
    HasDerivAt (fun t : ℝ => -Real.cos t + c) (Real.sin x) x := by
  simpa using (Real.hasDerivAt_cos x).neg.add_const c

/-- Modus ponens é uma regra lógica, sem pressupor a verdade empírica das premissas. -/
theorem modus_ponens (p q : Prop) (hp : p) (hpq : p → q) : q := by
  exact hpq hp

/-- Um produto de quatro indicadores binários vale1 exatamente quando todos valem1. -/
theorem four_binary_indicators (a b c d : ℝ)
    (ha : a = 0 ∨ a = 1) (hb : b = 0 ∨ b = 1)
    (hc : c = 0 ∨ c = 1) (hd : d = 0 ∨ d = 1) :
    a * b * c * d = 1 ↔ a = 1 ∧ b = 1 ∧ c = 1 ∧ d = 1 := by
  rcases ha with rfl | rfl <;> rcases hb with rfl | rfl <;>
    rcases hc with rfl | rfl <;> rcases hd with rfl | rfl <;> norm_num

/-- A nota100 para quatro indicadores binários exige o atendimento de todos. -/
theorem four_binary_indicators_percent (a b c d : ℝ)
    (ha : a = 0 ∨ a = 1) (hb : b = 0 ∨ b = 1)
    (hc : c = 0 ∨ c = 1) (hd : d = 0 ∨ d = 1) :
    100 * (a * b * c * d) = 100 ↔ a = 1 ∧ b = 1 ∧ c = 1 ∧ d = 1 := by
  have h := four_binary_indicators a b c d ha hb hc hd
  constructor
  · intro hPercent
    apply h.mp
    linarith
  · intro hAll
    rw [h.mpr hAll]
    norm_num

/-- Cinco intervalos consecutivos telescopam; timestamps, não duração medida, são os dados. -/
theorem five_consecutive_intervals (t0 t1 t2 t3 t4 t5 : ℝ) :
    (t1 - t0) + (t2 - t1) + (t3 - t2) + (t4 - t3) + (t5 - t4) = t5 - t0 := by
  ring

/-- Se os instantes são ordenados, a duração total telescópica é não negativa. -/
theorem consecutive_duration_nonnegative (t0 t1 t2 t3 t4 t5 : ℝ)
    (h01 : t0 ≤ t1) (h12 : t1 ≤ t2) (h23 : t2 ≤ t3)
    (h34 : t3 ≤ t4) (h45 : t4 ≤ t5) : 0 ≤ t5 - t0 := by
  linarith

/-- Um MiB corresponde a2^20 bytes, não a10^6 bytes. -/
theorem mebibyte_bytes : (2 : ℕ) ^ 20 = 1048576 := by
  norm_num

/-- Um MB decimal corresponde a10^6 bytes. -/
theorem megabyte_bytes : (10 : ℕ) ^ 6 = 1000000 := by
  norm_num

/-- As duas unidades diferem por48576 bytes, logo não são intercambiáveis. -/
theorem mebibyte_megabyte_difference : (2 : ℕ) ^ 20 - 10 ^ 6 = 48576 := by
  norm_num

/-- Guarda de peso total do diretório:1240MiB excedem o teto de1000MiB. -/
theorem directory_weight_guard_rejects_example : (1240 : ℕ) > 1000 := by
  norm_num

/-- Guarda de peso do arquivo:1180MiB excedem o teto de25MiB. -/
theorem file_weight_guard_rejects_example : (1180 : ℕ) > 25 := by
  norm_num

end BookFoundations
