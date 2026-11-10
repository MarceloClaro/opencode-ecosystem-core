import Mathlib

/-!
# Contraprova de correlação (R1147)

Duas tabelas de erro de leitura com as MESMAS marginais, mas juntas
diferentes. Isso mostra que marginais não determinam a correlação e que o
modelo independente pode errar em direções opostas dependendo do estatístico.

Tabela A (correlacionada), preparada em |00>:

|       | q1=0 | q1=1 |
|-------|------|------|
| q0=0  | 4/5  | 1/20 |
| q0=1  | 1/20 | 1/10 |

Tabela B (independente), mesmas marginais:

|       | q1=0   | q1=1   |
|-------|--------|--------|
| q0=0  | 289/400| 51/400 |
| q0=1  | 51/400 | 9/400  |

Em A: covariância positiva, P(0 erros)=0,8, P(2 erros)=0,1, P(≥1)=0,2.
Em B: covariância zero, P(0 erros)=0,7225, P(2 erros)=0,0225, P(≥1)=0,2775.

Portanto a independência **subestima** a fidelidade e o erro duplo, mas
**superestima** a união de erros. Nenhuma conclusão de mitigação/layout deve
usar apenas as marginais.

O arquivo não prova hardware, ruído real, crosstalk ou vantagem. Todas as
provas são kernel-checked; não há `sorry`, `admit`, `axiom` nem
`native_decide`.
-/

namespace CoreCorrelation

/-- Tabela A: erros correlacionados. -/
def p00A : ℚ := 4 / 5
def p01A : ℚ := 1 / 20
def p10A : ℚ := 1 / 20
def p11A : ℚ := 1 / 10

def p0A : ℚ := p10A + p11A
def p1A : ℚ := p01A + p11A

/-- Tabela B: mesmo marginal, juntas independentes. -/
def p00B : ℚ := 289 / 400
def p01B : ℚ := 51 / 400
def p10B : ℚ := 51 / 400
def p11B : ℚ := 9 / 400

def p0B : ℚ := p10B + p11B
def p1B : ℚ := p01B + p11B

/-- As marginais das duas tabelas são iguais. -/
theorem marginals_equal : p0A = p0B ∧ p1A = p1B := by
  constructor <;>
    norm_num [p0A, p0B, p1A, p1B, p10A, p11A, p10B, p11B, p01A, p01B]

/-- As juntas diferem: as marginais não determinam a tabela. -/
theorem joints_differ : p00A ≠ p00B := by
  norm_num [p00A, p00B]

/-- Em A, a covariância é positiva. -/
theorem covariance_A_positive : p11A - p0A * p1A > 0 := by
  norm_num [p11A, p0A, p1A, p10A, p01A]

/-- Em B, a covariância não é positiva (é zero). -/
theorem covariance_B_not_positive : ¬ (p11B - p0B * p1B > 0) := by
  norm_num [p11B, p0B, p1B, p10B, p01B]

/-- A correlação positiva aumenta a probabilidade de zero erros. -/
theorem no_error_A_gt_B : p00A > p00B := by
  norm_num [p00A, p00B]

/-- A correlação positiva aumenta a probabilidade de dois erros. -/
theorem double_error_A_gt_B : p11A > p11B := by
  norm_num [p11A, p11B]

/-- A correlação positiva diminui a probabilidade de pelo menos um erro. -/
theorem any_error_A_lt_B :
    p01A + p10A + p11A < p01B + p10B + p11B := by
  norm_num [p01A, p10A, p11A, p01B, p10B, p11B]

/-- A direção do efeito se inverte quando o estatístico muda. -/
theorem any_error_direction_reverses :
    p01A + p10A + p11A ≠ p01B + p10B + p11B := by
  norm_num [p01A, p10A, p11A, p01B, p10B, p11B]

/-- O limite de união não é justo: 0,7 < 0,8. -/
theorem union_bound_not_tight : 1 - p0A - p1A < p00A := by
  norm_num [p0A, p1A, p00A, p10A, p01A, p11A]

/-- Síntese: marginais iguais, junta diferente. -/
theorem marginals_do_not_determine_joint :
    p0A = p0B ∧ p1A = p1B ∧ p00A ≠ p00B := by
  exact ⟨marginals_equal.1, marginals_equal.2, joints_differ⟩

end CoreCorrelation

#print axioms CoreCorrelation.marginals_equal
#print axioms CoreCorrelation.joints_differ
#print axioms CoreCorrelation.covariance_A_positive
#print axioms CoreCorrelation.covariance_B_not_positive
#print axioms CoreCorrelation.no_error_A_gt_B
#print axioms CoreCorrelation.double_error_A_gt_B
#print axioms CoreCorrelation.any_error_A_lt_B
#print axioms CoreCorrelation.any_error_direction_reverses
#print axioms CoreCorrelation.union_bound_not_tight
#print axioms CoreCorrelation.marginals_do_not_determine_joint
