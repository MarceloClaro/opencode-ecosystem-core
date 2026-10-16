import Mathlib

/-!
# Álgebra do livro Core — R908

Estas provas usam números reais exatos (não ponto flutuante) e naturais para
contagens. Hipóteses estatísticas, taxas observadas, identidade dos registros e
execução do software não são demonstradas por substituição de constantes.
Em particular, o produto `p ^ n` é premissa de um modelo de independência;
a independência empírica não é uma conclusão deste arquivo.
-/

namespace BookAlgebra

/-- Partição complementar e produto assumido pelo modelo, não inferido dos dados. -/
theorem complement_from_product_model (good bad p : ℝ) (n : ℕ)
    (hTotal : good + bad = 1) (hProduct : good = p ^ n) :
    bad = 1 - p ^ n := by
  linarith

/-- Uma probabilidade individual no intervalo unitário produz risco complementar válido. -/
theorem complement_probability_bounds (p : ℝ) (n : ℕ)
    (h0 : 0 ≤ p) (h1 : p ≤ 1) :
    0 ≤ 1 - p ^ n ∧ 1 - p ^ n ≤ 1 := by
  have hp0 : 0 ≤ p ^ n := pow_nonneg h0 n
  have hp1 : p ^ n ≤ 1 := pow_le_one₀ h0 h1
  constructor <;> linarith

/-- A aproximação 0,886 tem erro absoluto menor que 0,001. -/
theorem independent_error_216_interval :
    (885 : ℝ) / 1000 < 1 - ((99 : ℝ) / 100) ^ 216 ∧
      1 - ((99 : ℝ) / 100) ^ 216 < (887 : ℝ) / 1000 := by
  norm_num

/-- Aproximação mais estreita para o complemento: 88,592%–88,593%. -/
theorem independent_error_216_tight_interval :
    (88592 : ℝ) / 100000 < 1 - ((99 : ℝ) / 100) ^ 216 ∧
      1 - ((99 : ℝ) / 100) ^ 216 < (88593 : ℝ) / 100000 := by
  norm_num

/-- Exercício com 99,9% individual: risco conjunto entre 19,4% e 19,5%. -/
theorem independent_error_216_high_accuracy_interval :
    (194 : ℝ) / 1000 < 1 - ((999 : ℝ) / 1000) ^ 216 ∧
      1 - ((999 : ℝ) / 1000) ^ 216 < (195 : ℝ) / 1000 := by
  norm_num

/-- A multiplicação decimal intermediária é exata; o logaritmo que a motivou é aproximado. -/
theorem logarithm_rounded_product :
    (216 : ℝ) * ((1005 : ℝ) / 100000) = (21708 : ℝ) / 10000 := by
  norm_num

/-- Percentagem é uma mudança de escala com denominador explícito não nulo. -/
theorem percent_unscale (part total : ℝ) (_hTotal : total ≠ 0) :
    (100 * part / total) / 100 = part / total := by
  ring

/-- Numerador contido no denominador positivo fornece fração entre zero e um. -/
theorem coverage_fraction_bounds (covered total : ℝ)
    (hc : 0 ≤ covered) (hct : covered ≤ total) (ht : 0 < total) :
    0 ≤ covered / total ∧ covered / total ≤ 1 := by
  exact ⟨div_nonneg hc ht.le, (div_le_one ht).2 hct⟩

/-- Média ponderada: pesos não negativos com soma um conservam a faixa unitária. -/
theorem weighted_coverage_bounds (w x y : ℝ)
    (hw0 : 0 ≤ w) (hw1 : w ≤ 1)
    (hx0 : 0 ≤ x) (hx1 : x ≤ 1) (hy0 : 0 ≤ y) (hy1 : y ≤ 1) :
    0 ≤ w * x + (1 - w) * y ∧ w * x + (1 - w) * y ≤ 1 := by
  have hwy : 0 ≤ 1 - w := sub_nonneg.mpr hw1
  have hLow := add_nonneg (mul_nonneg hw0 hx0) (mul_nonneg hwy hy0)
  have hUpperX := mul_le_mul_of_nonneg_left hx1 hw0
  have hUpperY := mul_le_mul_of_nonneg_left hy1 hwy
  constructor
  · exact hLow
  · nlinarith

/-- Um item crítico falso impede a conjunção, independentemente do escore médio. -/
theorem critical_gate_rejects (coverage critical : Bool) (hCritical : critical = false) :
    (coverage && critical) = false := by
  simp [hCritical]

/-- A aprovação exige que a condição crítica também seja verdadeira. -/
theorem critical_gate_acceptance_requires_critical (coverage critical : Bool)
    (h : (coverage && critical) = true) : critical = true := by
  cases coverage <;> cases critical <;> simp_all

/-- Valores verdadeiros/falsos positivos de um modelo: definição e expansão algébrica. -/
theorem ppv_denominator_expansion (beta odds alpha : ℝ) :
    (1 - beta) * odds + alpha = odds - beta * odds + alpha := by
  ring

/-- Derivação por chances T/F, com F não nulo e denominador do modelo não nulo. -/
theorem ppv_from_counts (trueCount falseCount beta alpha : ℝ)
    (hFalse : falseCount ≠ 0)
    (hDenom : (1 - beta) * trueCount + alpha * falseCount ≠ 0) :
    ((1 - beta) * trueCount) / ((1 - beta) * trueCount + alpha * falseCount) =
      ((1 - beta) * (trueCount / falseCount)) /
        ((1 - beta) * (trueCount / falseCount) + alpha) := by
  field_simp

/-- Não negatividade e limite unitário do PPV quando seus dois termos são válidos. -/
theorem ppv_bounds (vp fp : ℝ) (hvp : 0 ≤ vp) (hfp : 0 ≤ fp)
    (hSum : 0 < vp + fp) : 0 ≤ vp / (vp + fp) ∧ vp / (vp + fp) ≤ 1 := by
  exact coverage_fraction_bounds vp (vp + fp) hvp (by linarith) hSum

/-- Poder 0,2, chances 0,1 e alfa 0,05: resultado exato 2/7. -/
theorem ppv_low_power_exact :
    (((1 : ℝ) - 4 / 5) * (1 / 10)) /
      (((1 : ℝ) - 4 / 5) * (1 / 10) + 1 / 20) = 2 / 7 := by
  norm_num

/-- Poder 0,8, chances 0,1 e alfa 0,05: resultado exato 8/13. -/
theorem ppv_high_power_exact :
    (((1 : ℝ) - 1 / 5) * (1 / 10)) /
      (((1 : ℝ) - 1 / 5) * (1 / 10) + 1 / 20) = 8 / 13 := by
  norm_num

/-- Intervalo racional que justifica as aproximações decimais do PPV baixo. -/
theorem ppv_low_power_interval :
    (2857 : ℝ) / 10000 < 2 / 7 ∧ (2 : ℝ) / 7 < 2858 / 10000 := by
  norm_num

/-- Intervalo racional que justifica 0,61538… sem tratar a dízima como igualdade finita. -/
theorem ppv_high_power_interval :
    (61538 : ℝ) / 100000 < 8 / 13 ∧ (8 : ℝ) / 13 < 61539 / 100000 := by
  norm_num

/-- Chances iguais, poder 0,8 e alfa 0,05: PPV 16/17. -/
theorem ppv_equal_odds_exact :
    ((4 : ℝ) / 5) / ((4 : ℝ) / 5 + 1 / 20) = 16 / 17 := by
  norm_num

/-- Conservação PRISMA simplificada: as quatro partições implicam a conta global. -/
theorem prisma_conservation (identified duplicates screened excluded sought
    notRetrieved fullText excludedFull included : ℕ)
    (hIdentify : identified = duplicates + screened)
    (hScreen : screened = excluded + sought)
    (hRetrieval : sought = notRetrieved + fullText)
    (hFull : fullText = excludedFull + included) :
    identified = duplicates + excluded + notRetrieved + excludedFull + included := by
  omega

/-- A cardinalidade de uma união de classes disjuntas é a soma de suas contagens. -/
theorem partition_cardinality {α : Type*} [DecidableEq α]
    (left right : Finset α) (hDisjoint : Disjoint left right) :
    (left ∪ right).card = left.card + right.card := by
  exact Finset.card_union_of_disjoint hDisjoint

/-- Uma partição torna a conta de incluídos não maior que a inicial; não prova mérito. -/
theorem prisma_included_le_identified (identified duplicates screened excluded sought
    notRetrieved fullText excludedFull included : ℕ)
    (hIdentify : identified = duplicates + screened)
    (hScreen : screened = excluded + sought)
    (hRetrieval : sought = notRetrieved + fullText)
    (hFull : fullText = excludedFull + included) : included ≤ identified := by
  omega

/-- A EMA com 70/30 é uma combinação convexa, sob entradas unitárias explícitas. -/
theorem ema_70_30_bounds (old score : ℝ)
    (hOld0 : 0 ≤ old) (hOld1 : old ≤ 1)
    (hScore0 : 0 ≤ score) (hScore1 : score ≤ 1) :
    0 ≤ (7 / 10 : ℝ) * old + (3 / 10 : ℝ) * score ∧
      (7 / 10 : ℝ) * old + (3 / 10 : ℝ) * score ≤ 1 := by
  constructor <;> nlinarith

/-- Exemplo da API legada: nota 0,9 e histórico 0,5 produzem exatamente 0,62. -/
theorem ema_70_30_example :
    (7 / 10 : ℝ) * (1 / 2) + (3 / 10 : ℝ) * (9 / 10) = 31 / 50 := by
  norm_num

/-- A atualização se move em direção à nota sem ultrapassá-la quando a nota é maior. -/
theorem ema_moves_toward_score (old score : ℝ) (hOrder : old ≤ score) :
    old ≤ (7 / 10 : ℝ) * old + (3 / 10 : ℝ) * score ∧
      (7 / 10 : ℝ) * old + (3 / 10 : ℝ) * score ≤ score := by
  constructor <;> linarith

/-- A hipótese de faixa é necessária: a fórmula isolada permite resultado maior que um. -/
theorem ema_out_of_range_counterexample :
    (7 / 10 : ℝ) * 1 + (3 / 10 : ℝ) * 2 > 1 := by
  norm_num

/-- Normalização do tempo de uma única unidade no modelo de Amdahl. -/
theorem amdahl_single_worker_time (s : ℝ) : s + (1 - s) / 1 = 1 := by
  ring

/-- Fração sequencial em [0,1], com N positivo: tempo paralelo estritamente positivo. -/
theorem amdahl_time_positive (s n : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1)
    (hn : 0 < n) : 0 < s + (1 - s) / n := by
  by_cases hs : s = 0
  · subst s
    simpa using one_div_pos.mpr hn
  · exact add_pos_of_pos_of_nonneg (lt_of_le_of_ne hs0 (Ne.symm hs))
      (div_nonneg (sub_nonneg.mpr hs1) hn.le)

/-- O teto 1/s exige s>0; a prova usa a ordem dos denominadores positivos. -/
theorem amdahl_speedup_ceiling (s n : ℝ) (hs0 : 0 < s) (hs1 : s ≤ 1)
    (hn : 0 < n) : 1 / (s + (1 - s) / n) ≤ 1 / s := by
  apply one_div_le_one_div_of_le hs0
  exact le_add_of_nonneg_right (div_nonneg (sub_nonneg.mpr hs1) hn.le)

/-- No caso idealizado sem trabalho sequencial, o ganho é N (N não nulo). -/
theorem amdahl_zero_sequential (n : ℝ) (_hn : n ≠ 0) :
    1 / ((0 : ℝ) + (1 - 0) / n) = n := by
  simp

/-- Para um trabalhador, o ganho é um, qualquer que seja a divisão normalizada. -/
theorem amdahl_single_worker_speedup (s : ℝ) :
    1 / (s + (1 - s) / 1) = 1 := by
  rw [amdahl_single_worker_time]
  norm_num

/-- Limite assintótico real: o teto 1/s é atingido no limite, para s não nulo. -/
theorem amdahl_limit (s : ℝ) (hs : s ≠ 0) :
    Filter.Tendsto (fun n : ℝ => 1 / (s + (1 - s) / n))
      Filter.atTop (nhds (1 / s)) := by
  have hInv : Filter.Tendsto (fun n : ℝ => n⁻¹)
      Filter.atTop (nhds (0 : ℝ)) := tendsto_inv_atTop_zero
  have hPart : Filter.Tendsto (fun n : ℝ => (1 - s) / n)
      Filter.atTop (nhds (0 : ℝ)) := by
    simpa [div_eq_mul_inv] using hInv.const_mul (1 - s)
  have hTime : Filter.Tendsto (fun n : ℝ => s + (1 - s) / n)
      Filter.atTop (nhds s) := by
    simpa using hPart.const_add s
  exact Filter.Tendsto.div tendsto_const_nhds hTime hs

/-- O mesmo limite ao longo de contagens naturais de executores. -/
theorem amdahl_natural_executor_limit (s : ℝ) (hs : s ≠ 0) :
    Filter.Tendsto (fun n : ℕ => 1 / (s + (1 - s) / (n : ℝ)))
      Filter.atTop (nhds (1 / s)) := by
  exact (amdahl_limit s hs).comp tendsto_natCast_atTop_atTop

/-- O exemplo com treze executores vale 65/17, não um decimal truncado exato. -/
theorem amdahl_thirteen_exact :
    1 / ((1 / 5 : ℝ) + (1 - 1 / 5) / 13) = 65 / 17 := by
  norm_num

/-- Faixa racional do exemplo: 3,82 < 65/17 < 3,83. -/
theorem amdahl_thirteen_interval :
    (382 : ℝ) / 100 < 65 / 17 ∧ (65 : ℝ) / 17 < 383 / 100 := by
  norm_num

/-- Exemplo com quatro executores: ganho 2,5. -/
theorem amdahl_four_exact :
    1 / ((1 / 5 : ℝ) + (1 - 1 / 5) / 4) = 5 / 2 := by
  norm_num

/-- Exemplo com oito executores: ganho 10/3. -/
theorem amdahl_eight_exact :
    1 / ((1 / 5 : ℝ) + (1 - 1 / 5) / 8) = 10 / 3 := by
  norm_num

/-- Caução devolvida com recompensa: identidade distributiva, sem transferência financeira. -/
theorem staking_reward_formula (stake reward : ℝ) :
    stake + reward * stake = stake * (1 + reward) := by
  ring

/-- Caução 2 e recompensa 20%: retorno 2,4 unidades internas. -/
theorem staking_reward_example : (2 : ℝ) + (1 / 5 : ℝ) * 2 = 12 / 5 := by
  norm_num

/-- O desconto não aumenta nem torna negativa a caução quando stake≥0 e 0≤d≤1. -/
theorem slashing_bounds (stake discount : ℝ) (hStake : 0 ≤ stake)
    (hd0 : 0 ≤ discount) (hd1 : discount ≤ 1) :
    0 ≤ stake * (1 - discount) ∧ stake * (1 - discount) ≤ stake := by
  constructor
  · positivity
  · nlinarith

/-- Desconto de 50% sobre caução2: remanescente1. -/
theorem slashing_example : (2 : ℝ) * (1 - (1 / 2 : ℝ)) = 1 := by
  norm_num

/-- Fator de congestionamento por blocos inteiros de dez, com q natural não negativo. -/
def congestionFactor (q : ℕ) : ℚ := 1 + ((q / 10 : ℕ) : ℚ) / 10

/-- A taxa permanece base até nove tarefas abertas. -/
theorem congestion_below_first_block (q : ℕ) (hq : q < 10) :
    congestionFactor q = 1 := by
  simp [congestionFactor, Nat.div_eq_of_lt hq]

/-- De dez a dezenove tarefas, há exatamente um bloco adicional de10%. -/
theorem congestion_first_block (q : ℕ) (hLow : 10 ≤ q) (hHigh : q < 20) :
    congestionFactor q = 11 / 10 := by
  have hDiv : q / 10 = 1 := by omega
  norm_num [congestionFactor, hDiv]

/-- Taxa normal com dez tarefas e base1: 1,1 unidades. -/
theorem normal_fee_example : (1 : ℚ) * 1 * congestionFactor 10 = 11 / 10 := by
  norm_num [congestionFactor]

/-- Prioridade alta multiplica por2: 2,2 unidades com dez tarefas. -/
theorem high_priority_fee_example : (1 : ℚ) * 2 * congestionFactor 10 = 11 / 5 := by
  norm_num [congestionFactor]

/-- Partição de inventário fornecida: igualdade aritmética, não descoberta do inventário. -/
theorem catalog_reconciliation : (99 : ℕ) + 213 = 312 ∧ 81 + 18 = 99 := by
  norm_num

/-- As duas maiores categorias fornecidas totalizam186. -/
theorem catalog_largest_categories : (128 : ℕ) + 58 = 186 := by
  norm_num

/-- Concentração exata 186/312 = 31/52. -/
theorem catalog_concentration_exact : (186 : ℝ) / 312 = 31 / 52 := by
  norm_num

/-- Faixa estreita para a aproximação59,6%. -/
theorem catalog_concentration_interval :
    (59615 : ℝ) / 100000 < (186 : ℝ) / 312 ∧
      (186 : ℝ) / 312 < (59616 : ℝ) / 100000 := by
  norm_num

/-- Onze categorias e312 elementos: média aritmética entre28,36e28,37. -/
theorem catalog_mean_interval :
    (2836 : ℝ) / 100 < (312 : ℝ) / 11 ∧ (312 : ℝ) / 11 < (2837 : ℝ) / 100 := by
  norm_num

/-- Proporção de categorias encontradas no exemplo histórico42%: valor exato35/83. -/
theorem historical_coverage_interval :
    (42 : ℝ) / 100 < (35 : ℝ) / 83 ∧ (35 : ℝ) / 83 < 43 / 100 := by
  norm_num

/-- Quatro dimensões FAIR com dois itens cada: contagem de itens, sem mérito científico. -/
theorem fair_item_accounting : (2 : ℕ) + 2 + 2 + 2 = 8 := by
  norm_num

/-- Seis unidades ausentes dentre78 dão complemento12/13; não medem domínio real. -/
theorem unit_coverage_complement_exact : (1 : ℝ) - 6 / 78 = 12 / 13 := by
  norm_num

/-- Custo esperado0,2×2=0,4 no modelo didático com probabilidade e custo declarados. -/
theorem expected_cost_example : (1 / 5 : ℝ) * 2 = 2 / 5 := by
  norm_num

end BookAlgebra
