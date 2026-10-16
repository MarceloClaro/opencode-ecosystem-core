/-
R908 — modelos finitos e verificações aritméticas complementares do livro.
O conteúdo formaliza definições explícitas, identidades e intervalos racionais.
Valores de contagens, durações, custos e probabilidades são entradas do modelo;
as provas não verificam sua coleta nem inferem causalidade ou eficácia.
-/
import Mathlib.Basic.Real.Basic
import Mathlib.Analysis.Real.Sqrt
import Mathlib.Data.Finset.Card
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

namespace BookModels

open BigOperators

noncomputable section

-- A média documental não identifica a distribuição de usos individuais.
def arithmeticMean (xs : List ℝ) : ℝ := xs.sum / xs.length

theorem reference_counts_sum : ([1, 1, 1, 9] : List ℝ).sum = 12 := by norm_num

theorem reference_counts_mean : arithmeticMean [1, 1, 1, 9] = 3 := by
  norm_num [arithmeticMean]

theorem equal_cardinality_not_equal_sets :
    ({1} : Finset ℕ).card = ({2} : Finset ℕ).card ∧
      ({1} : Finset ℕ) ≠ ({2} : Finset ℕ) := by
  decide

-- Contagens iguais não certificam igualdade de conjuntos de identificadores.
-- Uma reconciliação precisa documentar as correspondências de identidade.
-- O contraexemplo acima refuta apenas a inferência contagem => igualdade.
theorem cardinality_equality_insufficient :
    ¬(∀ A B : Finset ℕ, A.card = B.card → A = B) := by
  intro h
  exact equal_cardinality_not_equal_sets.2
    (h {1} {2} equal_cardinality_not_equal_sets.1)

/- Redução hipotética de candidatos, não ganho de latência observado. -/
theorem reduction_ratio_nonnegative_le_total (M k : ℝ) (hM : 0 ≤ M) (hk : 1 ≤ k) :
    0 ≤ M/k ∧ M/k ≤ M := by
  have hkpos : 0 < k := by linarith
  constructor
  · exact div_nonneg hM hkpos.le
  · apply (div_le_iff₀ hkpos).mpr
    nlinarith

theorem reduction_ratio_at_least_one (M k : ℝ) (hk : 0 < k) (hMk : k ≤ M) :
    1 ≤ M/k := by
  apply (le_div_iff₀ hk).mpr
  simpa using hMk

theorem reduction_example_40_5 : (40 : ℝ)/5 = 8 := by norm_num

/- Custo adicional binário: soma finita explicitamente definida sobre Bool.
Esta é uma distribuição matemática parametrizada; p não é uma taxa medida. -/
def bernoulliMass (p : ℝ) (b : Bool) : ℝ := if b then p else 1-p

def finiteBernoulliCost (p c : ℝ) : ℝ :=
  ∑ b : Bool, (if b then c else 0) * bernoulliMass p b

theorem bernoulli_mass_normalized (p : ℝ) : (∑ b : Bool, bernoulliMass p b) = 1 := by
  simp [bernoulliMass]

theorem bernoulli_mass_nonnegative (p : ℝ) (hp : 0 ≤ p ∧ p ≤ 1) (b : Bool) :
    0 ≤ bernoulliMass p b := by
  cases b <;> simp [bernoulliMass] <;> linarith [hp.1, hp.2]

theorem bernoulli_finite_cost_equals_product (p c : ℝ) :
    finiteBernoulliCost p c = c*p := by
  simp [finiteBernoulliCost, bernoulliMass]

theorem bernoulli_product_expansion (p c : ℝ) : c*p + 0*(1-p) = c*p := by ring

theorem bernoulli_example_02_2 : finiteBernoulliCost (1/5) 2 = (2/5 : ℝ) := by
  rw [bernoulli_finite_cost_equals_product]
  norm_num

theorem bernoulli_exercise_05_2 : finiteBernoulliCost (1/2) 2 = (1 : ℝ) := by
  rw [bernoulli_finite_cost_equals_product]
  norm_num

theorem bernoulli_cost_bounds (p c : ℝ) (hp : 0 ≤ p ∧ p ≤ 1) (hc : 0 ≤ c) :
    0 ≤ finiteBernoulliCost p c ∧ finiteBernoulliCost p c ≤ c := by
  rw [bernoulli_finite_cost_equals_product]
  constructor <;> nlinarith [hp.1, hp.2]

/- Partição conceitual de custo: a aditividade é definição do modelo, não
lei empírica da engenharia de software. Mesmas unidades são pressupostas. -/
def additiveCost (essential accidental : ℝ) : ℝ := essential + accidental

theorem additive_cost_identity (essential accidental : ℝ) :
    additiveCost essential accidental = essential + accidental := rfl

theorem additive_cost_lower_bound (essential accidental : ℝ) (ha : 0 ≤ accidental) :
    essential ≤ additiveCost essential accidental := by
  unfold additiveCost
  linarith

theorem reducing_accidental_reduces_total (essential oldAccidental newAccidental : ℝ)
    (h : newAccidental ≤ oldAccidental) :
    additiveCost essential newAccidental ≤ additiveCost essential oldAccidental := by
  unfold additiveCost
  linarith

/- Diferença assinada observado - esperado; a direção e unidade são declaradas. -/
def discrepancy (observed expected : ℝ) : ℝ := observed - expected

theorem discrepancy_reconstructs_observed (observed expected : ℝ) :
    discrepancy observed expected + expected = observed := by
  unfold discrepancy
  ring

theorem discrepancy_zero_iff (observed expected : ℝ) :
    discrepancy observed expected = 0 ↔ observed = expected := by
  exact sub_eq_zero

theorem discrepancy_reversed (observed expected : ℝ) :
    discrepancy observed expected = -discrepancy expected observed := by
  unfold discrepancy
  ring

/- Intervalos racionais dos quocientes documentais/históricos.
Provam apenas as contas condicionadas às constantes fornecidas, não os totais.
Os intervalos de arredondamento abaixo têm largura de uma unidade decimal
na casa exibida; não se identificam quocientes com os decimais arredondados. -/
theorem test_spec_ratio_260_371_bounds :
    (7008/10000 : ℝ) < 260/371 ∧ (260/371 : ℝ) < 7009/10000 := by norm_num

theorem test_spec_ratio_rounds_0701 :
    (7005/10000 : ℝ) ≤ 260/371 ∧ (260/371 : ℝ) < 7015/10000 := by norm_num

theorem series_spec_ratio_285_371_bounds :
    (7681/10000 : ℝ) < 285/371 ∧ (285/371 : ℝ) < 7682/10000 := by norm_num

theorem series_spec_ratio_rounds_0768 :
    (7675/10000 : ℝ) ≤ 285/371 ∧ (285/371 : ℝ) < 7685/10000 := by norm_num

theorem tests_per_series_spec_260_285_bounds :
    (9122/10000 : ℝ) < 260/285 ∧ (260/285 : ℝ) < 9123/10000 := by norm_num

theorem tests_per_series_spec_rounds_091 :
    (905/1000 : ℝ) ≤ 260/285 ∧ (260/285 : ℝ) < 915/1000 := by norm_num

theorem specs_per_cycle_371_455_bounds :
    (8153/10000 : ℝ) < 371/455 ∧ (371/455 : ℝ) < 8154/10000 := by norm_num

theorem specs_per_cycle_rounds_0815 :
    (8145/10000 : ℝ) ≤ 371/455 ∧ (371/455 : ℝ) < 8155/10000 := by norm_num

theorem cycles_per_day_455_69_bounds :
    (6594/1000 : ℝ) < 455/69 ∧ (455/69 : ℝ) < 6595/1000 := by norm_num

theorem cycles_per_day_rounds_66 :
    (655/100 : ℝ) ≤ 455/69 ∧ (455/69 : ℝ) < 665/100 := by norm_num

theorem amortized_diagnosis_339_12_exact : (339/100 : ℝ)/12 = 113/400 := by norm_num

theorem amortized_diagnosis_rounds_028 :
    (275/1000 : ℝ) ≤ (339/100)/12 ∧ ((339/100)/12 : ℝ) < 285/1000 := by norm_num

theorem four_sixths_equals_two_thirds : (4/6 : ℝ) = 2/3 := by norm_num

theorem four_sixths_bounds :
    (6666/10000 : ℝ) < 4/6 ∧ (4/6 : ℝ) < 6667/10000 := by norm_num

theorem one_eleventh_bounds :
    (909/10000 : ℝ) < 1/11 ∧ (1/11 : ℝ) < 910/10000 := by norm_num

theorem one_eleventh_rounds_0091 :
    (905/10000 : ℝ) ≤ 1/11 ∧ (1/11 : ℝ) < 915/10000 := by norm_num

theorem two_thirds_bounds :
    (6666/10000 : ℝ) < 2/3 ∧ (2/3 : ℝ) < 6667/10000 := by norm_num


/- Escala da matriz didática de atenção. Esta conta não atribui uma operação
QKᵀ nem multiplicação por V à rota de utilidade do Python. -/
theorem attention_dimension_sqrt_four : Real.sqrt (4 : ℝ) = 2 := by
  apply (Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)).mpr
  norm_num

theorem attention_dimension_scaled_four : (4 : ℝ) / Real.sqrt 4 = 2 := by
  rw [attention_dimension_sqrt_four]
  norm_num

-- Complemento de um PPV do modelo hipotético (não risco empírico do Core).
theorem ppv_eight_thirteenths_complement : (1 : ℝ) - 8/13 = 5/13 := by norm_num

theorem ppv_complement_percentage_bounds :
    (384/10 : ℝ) < (1-8/13)*100 ∧ ((1-8/13)*100 : ℝ) < 385/10 := by norm_num

end

end BookModels
