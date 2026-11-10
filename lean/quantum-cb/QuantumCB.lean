import Init

/-!
# Contraprova Lean 4 — CB intercalado do CZ (R1129/R1130)

Este arquivo formaliza apenas a parte **finita e linear** da contraprova:

1. a matriz de desenho `D` (13×15) tem uma inversa à direita `R` (15×13),
   com entradas inteiras; logo as 13 funções são linearmente independentes;
2. a matriz de incidência `B` (4×15) anula as 13 linhas de `D`;
3. a base de corte `C` (2×15) anula as 13 linhas de `D` e tem posto 2
   (menor 2×2 não nulo);
4. as contagens `7+6=13`, `15-4+2=13` e `4-2=2`.

O que NÃO é provado aqui:
- o canal quântico, a simulação por matriz densidade, o decaimento exponencial
  e a recuperação numérica das fidelidades;
- ruído real, compilação, twirl/frame ou qualquer execução no Baihua;
- que as 2 funções de corte sejam identificáveis sem hipótese adicional.

Lean verifica identidades finitas; não substitui evidência experimental.
-/

namespace QuantumCB

abbrev Mat (m n : Nat) := Fin m → Fin n → Rat

def dot {n : Nat} (a b : Fin n → Rat) : Rat :=
  (List.finRange n).map (fun i => a i * b i) |>.sum

def mul {m n p : Nat} (A : Mat m n) (B : Mat n p) : Mat m p :=
  fun i k => dot (fun j => A i j) (fun j => B j k)

def transpose {m n : Nat} (A : Mat m n) : Mat n m :=
  fun i j => A j i

def one (n : Nat) : Mat n n :=
  fun i j => if i = j then 1 else 0

def D : Mat 13 15 := fun i j =>
  match i.val, j.val with
  | 0, 2 => 1
  | 1, 11 => 1
  | 2, 4 => 1
  | 3, 5 => 1
  | 4, 8 => 1
  | 5, 9 => 1
  | 6, 14 => 1
  | 7, 0 => 1
  | 7, 12 => 1
  | 8, 0 => 1
  | 8, 13 => 1
  | 9, 1 => 1
  | 9, 12 => 1
  | 10, 3 => 1
  | 10, 6 => 1
  | 11, 3 => 1
  | 11, 10 => 1
  | 12, 6 => 1
  | 12, 7 => 1
  | _, _ => 0

def R : Mat 15 13 := fun i j =>
  match i.val, j.val with
  | 0, 8 => 1
  | 1, 7 => -1
  | 1, 8 => 1
  | 1, 9 => 1
  | 2, 0 => 1
  | 3, 11 => 1
  | 4, 2 => 1
  | 5, 3 => 1
  | 6, 10 => 1
  | 6, 11 => -1
  | 7, 10 => -1
  | 7, 11 => 1
  | 7, 12 => 1
  | 8, 4 => 1
  | 9, 5 => 1
  | 11, 1 => 1
  | 12, 7 => 1
  | 12, 8 => -1
  | 14, 6 => 1
  | _, _ => 0

def B : Mat 4 15 := fun i j =>
  match i.val, j.val with
  | 1, 0 => 1
  | 1, 1 => 1
  | 1, 12 => -1
  | 1, 13 => -1
  | 2, 3 => 1
  | 2, 6 => -1
  | 2, 7 => 1
  | 2, 10 => -1
  | 3, 0 => -1
  | 3, 1 => -1
  | 3, 3 => -1
  | 3, 6 => 1
  | 3, 7 => -1
  | 3, 10 => 1
  | 3, 12 => 1
  | 3, 13 => 1
  | _, _ => 0

def C : Mat 2 15 := fun i j =>
  match i.val, j.val with
  | 0, 3 => -1
  | 0, 6 => 1
  | 0, 7 => -1
  | 0, 10 => 1
  | 1, 0 => -1
  | 1, 1 => -1
  | 1, 12 => 1
  | 1, 13 => 1
  | _, _ => 0

/-- `D` tem inversa à direita: as 13 linhas são independentes. -/
theorem D_mul_R : ∀ i j, mul D R i j = one 13 i j := by
  native_decide

/-- As 13 funções estão no núcleo da matriz de incidência do grafo do CZ. -/
theorem B_mul_D_transpose : ∀ i j, mul B (transpose D) i j = 0 := by
  native_decide

/-- As duas linhas de corte são ortogonais às 13 funções. -/
theorem C_mul_D_transpose : ∀ i j, mul C (transpose D) i j = 0 := by
  native_decide

/-- As duas linhas de corte são independentes (menor 2×2 não nulo). -/
theorem C_independent :
    C 0 0 * C 1 3 - C 0 3 * C 1 0 ≠ 0 := by
  native_decide

theorem design_rows : 7 + 6 = (13 : Nat) := by decide

theorem cycle_rank : 15 - 4 + 2 = (13 : Nat) := by decide

theorem cut_rank : 4 - 2 = (2 : Nat) := by decide

end QuantumCB


#print axioms QuantumCB.D_mul_R
#print axioms QuantumCB.B_mul_D_transpose
#print axioms QuantumCB.C_mul_D_transpose
#print axioms QuantumCB.C_independent
#print axioms QuantumCB.design_rows
#print axioms QuantumCB.cycle_rank
#print axioms QuantumCB.cut_rank
