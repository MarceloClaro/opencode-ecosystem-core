/-
R908 — propriedades matemáticas da atenção, seleção e similaridade.
As definições são modelos em ℝ/conjuntos finitos, não equivalência integral
com Python nem validação de desempenho, calibração ou hipóteses empíricas.
As onze proposições históricas R755 são recompiladas neste namespace com
comentários e alcance corrigidos. A prova de limites reais não modela IEEE-754.
-/
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Data.Finset.Max
import Mathlib.Data.List.Pairwise
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

import Mathlib.Analysis.Complex.ExponentialBounds
import Mathlib.Tactic.NormNum

namespace BookAttention

noncomputable section

open BigOperators Finset

-- T1: pesos de atenção (softmax) somam 1 — normalização algébrica (attention.py: pesos somando 1).
theorem softmax_soma_um {ι : Type*} [DecidableEq ι] [Fintype ι] (f : ι → Real) [Nonempty ι] :
    ∑ i, (Real.exp (f i) / ∑ j, Real.exp (f j)) = 1 := by
  have hpos : 0 < ∑ j, Real.exp (f j) :=
    Finset.sum_pos (fun i _ => Real.exp_pos (f i)) Finset.univ_nonempty
  rw [← Finset.sum_div]
  exact div_self (ne_of_gt hpos)

-- T2: combinação convexa das cabeças fica limitada pelo melhor componente
-- (attention.py: _validated_weights exige soma 1, cada peso em [0,1]).
theorem combinacao_convexa_limitada {ι : Type*} (s : Finset ι) (w x : ι → Real) (M : Real)
    (hsum : Finset.sum s (fun i => w i) = 1) (hnn : ∀ i ∈ s, 0 ≤ w i) (hle : ∀ i ∈ s, x i ≤ M) :
    Finset.sum s (fun i => w i * x i) ≤ M := by
  calc Finset.sum s (fun i => w i * x i) ≤ Finset.sum s (fun i => w i * M) :=
        Finset.sum_le_sum (fun i hi => mul_le_mul_of_nonneg_left (hle i hi) (hnn i hi))
    _ = M := by rw [← Finset.sum_mul, hsum, one_mul]

-- T3: existe candidato de utilidade máxima — a seleção gulosa top-1 é ótima
-- (attention.py: ranking ordenado do melhor para o pior).
theorem roteamento_guloso_otimo {Agent : Type*} [DecidableEq Agent] (candidatos : Finset Agent)
    (utilidade : Agent → Real) (h : candidatos.Nonempty) :
    ∃ melhor ∈ candidatos, ∀ a ∈ candidatos, utilidade a ≤ utilidade melhor :=
  Finset.exists_max_image candidatos utilidade h

-- T4: subtrair constante (o máximo, na implementação) não muda os pesos —
-- identidade em números reais; não prova de comportamento IEEE-754 (attention.py: exps de s - m).
theorem softmax_invariante_max {ι : Type*} [DecidableEq ι] [Fintype ι] (f : ι → Real) [Nonempty ι]
    (c : Real) (i : ι) :
    Real.exp (f i - c) / ∑ j, Real.exp (f j - c)
      = Real.exp (f i) / ∑ j, Real.exp (f j) := by
  have he : Real.exp c ≠ 0 := ne_of_gt (Real.exp_pos c)
  have hS : (∑ j, Real.exp (f j)) ≠ 0 := ne_of_gt
    (Finset.sum_pos (fun k _ => Real.exp_pos (f k)) Finset.univ_nonempty)
  simp only [Real.exp_sub]
  rw [← Finset.sum_div]
  field_simp

-- T5: cada peso está em (0,1) com ao menos dois candidatos — pesos positivos normalizados, não probabilidade calibrada de acerto.
theorem softmax_mem_Ioo {ι : Type*} [DecidableEq ι] [Fintype ι] (f : ι → Real) [Nonempty ι]
    [Nontrivial ι] (i : ι) :
    0 < Real.exp (f i) / ∑ j, Real.exp (f j) ∧ Real.exp (f i) / ∑ j, Real.exp (f j) < 1 := by
  have hS : 0 < ∑ j, Real.exp (f j) :=
    Finset.sum_pos (fun k _ => Real.exp_pos (f k)) Finset.univ_nonempty
  refine ⟨div_pos (Real.exp_pos _) hS, ?_⟩
  rw [div_lt_one hS]
  obtain ⟨j, hji⟩ := exists_ne i
  have hR : 0 < Finset.sum (Finset.univ.erase i) (fun k => Real.exp (f k)) :=
    Finset.sum_pos (fun k _ => Real.exp_pos _) ⟨j, Finset.mem_erase.mpr ⟨hji, Finset.mem_univ j⟩⟩
  have hsplit := Finset.add_sum_erase Finset.univ (fun k => Real.exp (f k)) (Finset.mem_univ i)
  linarith

-- T6: limite inferior — fecha E2 bilateral (espelho de T2).
theorem combinacao_convexa_limitada_baixo {ι : Type*} (s : Finset ι) (w x : ι → Real) (m : Real)
    (hsum : Finset.sum s (fun i => w i) = 1) (hnn : ∀ i ∈ s, 0 ≤ w i) (hle : ∀ i ∈ s, m ≤ x i) :
    m ≤ Finset.sum s (fun i => w i * x i) := by
  calc m = Finset.sum s (fun i => w i * m) := by rw [← Finset.sum_mul, hsum, one_mul]
    _ ≤ Finset.sum s (fun i => w i * x i) :=
        Finset.sum_le_sum (fun i hi => mul_le_mul_of_nonneg_left (hle i hi) (hnn i hi))

-- T7: candidato único recebe peso 1 — complementa T5 (que exige Nontrivial).
-- Fecha a objeção do singleton: os dois casos estão cobertos.
theorem softmax_peso_total_singleton {ι : Type*} [DecidableEq ι] [Fintype ι] (f : ι → Real)
    [Nonempty ι] (i : ι) (h : ∀ j, j = i) :
    Real.exp (f i) / ∑ j, Real.exp (f j) = 1 := by
  have hS : (∑ j, Real.exp (f j)) = Real.exp (f i) :=
    Finset.sum_eq_single_of_mem i (Finset.mem_univ i) (fun j _ hji => absurd (h j) hji)
  rw [hS, div_self (ne_of_gt (Real.exp_pos _))]

-- T8: o peso cresce estritamente com o próprio escore (demais fixos) —
-- justifica a regra de decisão: maior escore, maior peso.
theorem peso_cresce_com_escore (C : Real) (hC : 0 < C) :
    StrictMono (fun x : Real => Real.exp x / (Real.exp x + C)) := by
  intro a b hab
  have hea : 0 < Real.exp a := Real.exp_pos a
  have heb : 0 < Real.exp b := Real.exp_pos b
  rw [div_lt_div_iff₀ (add_pos hea hC) (add_pos heb hC)]
  have h1 : Real.exp a * C < Real.exp b * C :=
    mul_lt_mul_of_pos_right (Real.exp_strictMono hab) hC
  linarith

-- T9: numa lista pairwise-decrescente, todo elemento dos take k domina todo
-- elemento do resto — o padrão top-k do ranking (sort + take).
theorem topk_dominam_resto (l : List Real) (k : ℕ) (hp : l.Pairwise (· ≥ ·))
    (x : Real) (hx : x ∈ l.drop k) (y : Real) (hy : y ∈ l.take k) : y ≥ x := by
  have happ : l.take k ++ l.drop k = l := List.take_append_drop k l
  rw [← happ] at hp
  rw [List.pairwise_append] at hp
  exact hp.2.2 y hy x hx

-- T10: esfriar a temperatura aumenta o peso do maximizador único — nitidez
-- (literatura de calibração por temperatura; aqui em forma elementar, sem limites).
theorem temperatura_aguca_maximo {ι : Type*} [DecidableEq ι] [Fintype ι] (f : ι → Real)
    [Nonempty ι] [Nontrivial ι] (iest : ι) (hmax : ∀ j, j ≠ iest → f j < f iest)
    (τ₁ τ₂ : Real) (hτ1 : 0 < τ₁) (hτ2 : 0 < τ₂) (hlt : τ₁ < τ₂) :
    Real.exp (f iest / τ₂) / ∑ j, Real.exp (f j / τ₂)
      < Real.exp (f iest / τ₁) / ∑ j, Real.exp (f j / τ₁) := by
  have hS1 : 0 < ∑ j, Real.exp (f j / τ₁) :=
    Finset.sum_pos (fun k _ => Real.exp_pos _) Finset.univ_nonempty
  have hS2 : 0 < ∑ j, Real.exp (f j / τ₂) :=
    Finset.sum_pos (fun k _ => Real.exp_pos _) Finset.univ_nonempty
  have hinv : 1 / τ₂ < 1 / τ₁ := one_div_lt_one_div_of_lt hτ1 hlt
  have hlt_of_ne : ∀ j, j ≠ iest →
      Real.exp (f iest / τ₂) * Real.exp (f j / τ₁)
        < Real.exp (f iest / τ₁) * Real.exp (f j / τ₂) := by
    intro j hji
    have hfj : f j < f iest := hmax j hji
    have hdiff : (f iest / τ₁ + f j / τ₂) - (f iest / τ₂ + f j / τ₁)
        = (f iest - f j) * (1 / τ₁ - 1 / τ₂) := by
      field_simp
      ring
    have hpos : 0 < (f iest - f j) * (1 / τ₁ - 1 / τ₂) :=
      mul_pos (sub_pos.mpr hfj) (sub_pos.mpr hinv)
    have hlt' : f iest / τ₂ + f j / τ₁ < f iest / τ₁ + f j / τ₂ := by
      linarith
    calc Real.exp (f iest / τ₂) * Real.exp (f j / τ₁)
        = Real.exp (f iest / τ₂ + f j / τ₁) := (Real.exp_add _ _).symm
      _ < Real.exp (f iest / τ₁ + f j / τ₂) := Real.exp_strictMono hlt'
      _ = Real.exp (f iest / τ₁) * Real.exp (f j / τ₂) := Real.exp_add _ _
  have hterm : ∀ j ∈ Finset.univ,
      Real.exp (f iest / τ₂) * Real.exp (f j / τ₁)
        ≤ Real.exp (f iest / τ₁) * Real.exp (f j / τ₂) := by
    intro j _
    by_cases hji : j = iest
    · subst hji; exact le_of_eq (mul_comm _ _)
    · exact le_of_lt (hlt_of_ne j hji)
  obtain ⟨j0, hj0⟩ := exists_ne iest
  have hstrict : Real.exp (f iest / τ₂) * Real.exp (f j0 / τ₁)
      < Real.exp (f iest / τ₁) * Real.exp (f j0 / τ₂) :=
    hlt_of_ne j0 hj0
  have hsum : (∑ j, Real.exp (f iest / τ₂) * Real.exp (f j / τ₁))
      < ∑ j, Real.exp (f iest / τ₁) * Real.exp (f j / τ₂) :=
    Finset.sum_lt_sum hterm ⟨j0, Finset.mem_univ j0, hstrict⟩
  rw [← Finset.mul_sum, ← Finset.mul_sum] at hsum
  rw [div_lt_div_iff₀ hS2 hS1]
  linarith

-- T11: após subtrair majorante, a exponencial real é ≤ 1; não é prova de ausência de overflow IEEE-754.
theorem exp_apos_subtrair_majorante_le_um {ι : Type*} (f : ι → Real) (M : Real) (i : ι)
    (hM : ∀ j, f j ≤ M) : Real.exp (f i - M) ≤ 1 := by
  rw [Real.exp_le_one_iff]
  exact sub_nonpos.mpr (hM i)


/- Pesos configurados: 0,30; 0,35; 0,25; 0,10, aqui racionais exatos. -/
def utility (semantic capability confidence freeLoad : ℝ) : ℝ :=
  (30/100 : ℝ) * semantic + (35/100 : ℝ) * capability +
    (25/100 : ℝ) * confidence + (10/100 : ℝ) * freeLoad

theorem head_weights_sum_one :
    (30/100 : ℝ) + 35/100 + 25/100 + 10/100 = 1 := by norm_num

theorem utility_mem_unit (s c f l : ℝ)
    (hs : 0 ≤ s ∧ s ≤ 1) (hc : 0 ≤ c ∧ c ≤ 1)
    (hf : 0 ≤ f ∧ f ≤ 1) (hl : 0 ≤ l ∧ l ≤ 1) :
    0 ≤ utility s c f l ∧ utility s c f l ≤ 1 := by
  unfold utility
  constructor <;> linarith [hs.1, hs.2, hc.1, hc.2, hf.1, hf.2, hl.1, hl.2]

-- Exemplos de combinação explícita; não são avaliações empíricas de agentes.
theorem utility_example_075 : utility (4/5) (9/10) (1/2) (7/10) = (3/4 : ℝ) := by
  norm_num [utility]

theorem utility_example_064 : utility (3/5) (7/10) (1/2) (9/10) = (16/25 : ℝ) := by
  norm_num [utility]

/- Similaridade lexical. Exige união não vazia para interpretação do quociente.
A convenção Lean 0/0=0 não é usada para justificar similaridade de vazios. -/
def jaccard {α : Type*} [DecidableEq α] (A B : Finset α) : ℝ :=
  ((A ∩ B).card : ℝ) / ((A ∪ B).card : ℝ)

theorem jaccard_mem_unit {α : Type*} [DecidableEq α] (A B : Finset α)
    (h : (A ∪ B).Nonempty) : 0 ≤ jaccard A B ∧ jaccard A B ≤ 1 := by
  have hd : 0 < ((A ∪ B).card : ℝ) := by
    exact_mod_cast Finset.card_pos.mpr h
  have hn : ((A ∩ B).card : ℝ) ≤ ((A ∪ B).card : ℝ) := by
    exact_mod_cast Finset.card_le_card (show A ∩ B ⊆ A ∪ B by
      intro x hx
      exact Finset.mem_union.mpr (Or.inl (Finset.mem_inter.mp hx).1))
  unfold jaccard
  exact ⟨div_nonneg (Nat.cast_nonneg _) hd.le, (div_le_one hd).mpr hn⟩

theorem jaccard_symmetric {α : Type*} [DecidableEq α] (A B : Finset α) :
    jaccard A B = jaccard B A := by
  simp only [jaccard, Finset.inter_comm, Finset.union_comm]

theorem jaccard_identical {α : Type*} [DecidableEq α] (A : Finset α)
    (h : A.Nonempty) : jaccard A A = 1 := by
  have hn : (A.card : ℝ) ≠ 0 := by exact_mod_cast (Finset.card_pos.mpr h).ne'
  simp [jaccard, hn]

theorem jaccard_disjoint {α : Type*} [DecidableEq α] (A B : Finset α)
    (h : Disjoint A B) : jaccard A B = 0 := by
  simp [jaccard, Finset.disjoint_iff_inter_eq_empty.mp h]

-- Os elementos são índices de tokens, não inferências sobre competência.
theorem jaccard_example_half :
    jaccard ({0, 1, 2} : Finset ℕ) {0, 2, 3} = (1/2 : ℝ) := by
  norm_num [jaccard]

theorem jaccard_example_third :
    jaccard ({0, 1} : Finset ℕ) {0, 2} = (1/3 : ℝ) := by
  norm_num [jaccard]

theorem jaccard_example_three_fifths :
    jaccard ({0, 1, 2, 3} : Finset ℕ) {0, 1, 2, 4} = (3/5 : ℝ) := by
  norm_num [jaccard]

/- Seleção restrita: um mínimo existe no conjunto finito não vazio elegível.
O critério de custo é modelo hipotético do livro, não a implementação _on_cfp. -/
theorem eligible_minimum_exists {α : Type*} [DecidableEq α] (C : Finset α)
    (cost : α → ℝ) (hC : C.Nonempty) :
    ∃ chosen ∈ C, ∀ a ∈ C, cost chosen ≤ cost a :=
  Finset.exists_min_image C cost hC

theorem excluded_cannot_be_chosen {α : Type*} [DecidableEq α]
    (C : Finset α) (chosen excluded : α) (hc : chosen ∈ C) (he : excluded ∉ C) :
    chosen ≠ excluded := by
  intro h
  exact he (h ▸ hc)

def contractExampleCost (i : ℕ) : ℝ := if i = 1 then 10 else if i = 2 then 7 else 12

theorem contract_example_c2_minimizes :
    2 ∈ ({1, 2, 3} : Finset ℕ) ∧
      ∀ a ∈ ({1, 2, 3} : Finset ℕ), contractExampleCost 2 ≤ contractExampleCost a := by
  constructor
  · simp
  · intro a ha
    simp only [Finset.mem_insert, Finset.mem_singleton] at ha
    rcases ha with rfl | rfl | rfl <;> norm_num [contractExampleCost]

/- Softmax em duas coordenadas e duas linhas; números reais exatos. -/
def twoWeight (x y : ℝ) : ℝ := Real.exp x / (Real.exp x + Real.exp y)

theorem two_row_softmax_sum (x y : ℝ) : twoWeight x y + twoWeight y x = 1 := by
  unfold twoWeight
  have hd : Real.exp x + Real.exp y ≠ 0 := ne_of_gt (add_pos (Real.exp_pos x) (Real.exp_pos y))
  rw [add_comm (Real.exp y) (Real.exp x), ← add_div, div_self hd]

theorem two_row_reversed (x y : ℝ) : twoWeight y x = 1 - twoWeight x y := by
  linarith [two_row_softmax_sum x y]

theorem two_row_tie (x : ℝ) : twoWeight x x = (1/2 : ℝ) := by
  unfold twoWeight
  have hx : Real.exp x ≠ 0 := ne_of_gt (Real.exp_pos x)
  field_simp
  ring

theorem two_row_translation_invariant (x y c : ℝ) :
    twoWeight (x+c) (y+c) = twoWeight x y := by
  unfold twoWeight
  simp only [Real.exp_add]
  have hc : Real.exp c ≠ 0 := ne_of_gt (Real.exp_pos c)
  have hd : Real.exp x + Real.exp y ≠ 0 := ne_of_gt (add_pos (Real.exp_pos x) (Real.exp_pos y))
  have hd' : Real.exp x * Real.exp c + Real.exp y * Real.exp c ≠ 0 := by
    rw [← add_mul]
    exact mul_ne_zero hd hc
  field_simp

-- Intervalos demonstrados a partir dos limites de exp(1) da Mathlib, não
-- pela hipótese da aproximação decimal que se pretendia verificar.
theorem exp_two_rational_bounds : (7389/1000 : ℝ) < Real.exp 2 ∧ Real.exp 2 < 73891/10000 := by
  have hl := Real.exp_one_gt_d9
  have hu := Real.exp_one_lt_d9
  have hp := Real.exp_pos (1 : ℝ)
  have he : Real.exp (2 : ℝ) = Real.exp 1 * Real.exp 1 := by
    convert Real.exp_add (1 : ℝ) 1 using 1; norm_num
  rw [he]
  constructor <;> nlinarith

theorem softmax_2_0_rational_bounds :
    (8807/10000 : ℝ) < twoWeight 2 0 ∧ twoWeight 2 0 < 8809/10000 := by
  obtain ⟨hl, hu⟩ := exp_two_rational_bounds
  have hp := Real.exp_pos (2 : ℝ)
  have hd : 0 < Real.exp (2 : ℝ) + 1 := by positivity
  simp only [twoWeight, Real.exp_zero]
  constructor
  · apply (lt_div_iff₀ hd).mpr
    linarith
  · apply (div_lt_iff₀ hd).mpr
    linarith

theorem softmax_0_2_rational_bounds :
    (1191/10000 : ℝ) < twoWeight 0 2 ∧ twoWeight 0 2 < 1193/10000 := by
  have h := softmax_2_0_rational_bounds
  have hc := two_row_reversed (2 : ℝ) 0
  constructor <;> linarith [h.1, h.2]


-- Diferença das utilidades do exemplo da rota: 0,75 - 0,64 = 0,11.
-- A série finita e o resto são calculados pela biblioteca, com n=5.
theorem exp_point11_rational_bounds :
    (1116277/1000000 : ℝ) < Real.exp (11/100) ∧ Real.exp (11/100) < 1116279/1000000 := by
  have h := Real.exp_bound (x := (11/100 : ℝ)) (by norm_num) (n := 5) (by norm_num)
  norm_num [Finset.sum_range_succ] at h
  have hab := abs_le.mp h
  constructor <;> linarith [hab.1, hab.2]

theorem utility_softmax_reduction :
    twoWeight (3/4) (16/25) = twoWeight (11/100) 0 := by
  have h := two_row_translation_invariant (3/4 : ℝ) (16/25) (-16/25)
  norm_num at h
  exact h.symm

theorem utility_softmax_075_064_bounds :
    (52747/100000 : ℝ) < twoWeight (3/4) (16/25) ∧
      twoWeight (3/4) (16/25) < 52748/100000 := by
  rw [utility_softmax_reduction]
  obtain ⟨hl, hu⟩ := exp_point11_rational_bounds
  have hp := Real.exp_pos (11/100 : ℝ)
  have hd : 0 < Real.exp (11/100 : ℝ) + 1 := by positivity
  simp only [twoWeight, Real.exp_zero]
  constructor
  · apply (lt_div_iff₀ hd).mpr
    linarith
  · apply (div_lt_iff₀ hd).mpr
    linarith

theorem utility_softmax_064_075_bounds :
    (47252/100000 : ℝ) < twoWeight (16/25) (3/4) ∧
      twoWeight (16/25) (3/4) < 47253/100000 := by
  have h := utility_softmax_075_064_bounds
  have hc := two_row_reversed (3/4 : ℝ) (16/25)
  constructor <;> linarith [h.1, h.2]


/- Ordem no mesmo conjunto: normalizar pela mesma soma positiva preserva a
ordem dos escores reais. Isso não afirma acerto ou mérito da resposta. -/
theorem softmax_same_pool_order {ι : Type*} [DecidableEq ι] [Fintype ι]
    [Nonempty ι] (f : ι → ℝ) (i j : ι) :
    Real.exp (f i) / ∑ k, Real.exp (f k) ≤
      Real.exp (f j) / ∑ k, Real.exp (f k) ↔ f i ≤ f j := by
  have hd : 0 < ∑ k, Real.exp (f k) :=
    Finset.sum_pos (fun k _ => Real.exp_pos (f k)) Finset.univ_nonempty
  rw [div_le_div_iff_of_pos_right hd, Real.exp_le_exp]

-- Modelo restrito dos dois requisitos obrigatórios: disponibilidade e
-- todas as capacidades exigidas. Identidades duplicadas e dados inválidos
-- são controles adicionais do Python, não provados por esta definição.
def eligiblePool {α β : Type*} [DecidableEq β]
    (candidates : Finset α) (required : Finset β) (capabilities : α → Finset β)
    (available : α → Prop) [DecidablePred available] : Finset α :=
  candidates.filter (fun a => available a ∧ required ⊆ capabilities a)

theorem eligible_pool_membership {α β : Type*} [DecidableEq β]
    (candidates : Finset α) (required : Finset β) (capabilities : α → Finset β)
    (available : α → Prop) [DecidablePred available] (a : α) :
    a ∈ eligiblePool candidates required capabilities available ↔
      a ∈ candidates ∧ available a ∧ required ⊆ capabilities a := by
  simp only [eligiblePool, Finset.mem_filter]

theorem unavailable_not_eligible {α β : Type*} [DecidableEq β]
    (candidates : Finset α) (required : Finset β) (capabilities : α → Finset β)
    (available : α → Prop) [DecidablePred available] (a : α) (h : ¬available a) :
    a ∉ eligiblePool candidates required capabilities available := by
  intro ha
  exact h ((eligible_pool_membership candidates required capabilities available a).mp ha).2.1

theorem missing_capability_not_eligible {α β : Type*} [DecidableEq β]
    (candidates : Finset α) (required : Finset β) (capabilities : α → Finset β)
    (available : α → Prop) [DecidablePred available] (a : α)
    (h : ¬required ⊆ capabilities a) :
    a ∉ eligiblePool candidates required capabilities available := by
  intro ha
  exact h ((eligible_pool_membership candidates required capabilities available a).mp ha).2.2

end

end BookAttention
