-- Teorema de Eficiência do Roteamento por Atenção — SPEC-935-R755
-- Espelha transformer/attention.py: softmax estável, cabeças em combinação
-- convexa (soma 1), ranking top-k. Eficiência = otimalidade relativa à
-- utilidade definida, nunca superioridade universal.

import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Data.Finset.Max
import Mathlib.Data.List.Pairwise
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

open BigOperators Finset

-- T1: pesos de atenção (softmax) somam 1 — calibração (attention.py: pesos somando 1).
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
-- estabilidade numérica sem mudar a decisão (attention.py: exps de s - m).
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

-- T5: cada peso está em (0,1) com ao menos dois candidatos — probabilidade genuína.
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

-- T11: após subtrair majorante, expoentes ≤ 0 — sem overflow (truque do código).
theorem sem_overflow_apos_max {ι : Type*} (f : ι → Real) (M : Real) (i : ι)
    (hM : ∀ j, f j ≤ M) : Real.exp (f i - M) ≤ 1 := by
  rw [Real.exp_le_one_iff]
  exact sub_nonpos.mpr (hM i)
