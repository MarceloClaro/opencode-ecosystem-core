import Mathlib

/-!
# Mathlib counterproof — CB invariants (R1135)

This file checks the finite linear-algebra invariants with Mathlib:
`D` (13×15) has a right inverse `R` (15×13), hence rank 13;
`B` and `C` annihilate `D`; `C` has a nonzero 2×2 minor.

It does NOT prove the quantum channel, simulation, twirl, or hardware.
The finite identities use `native_decide`; `rank_D` uses Mathlib's rank
lemmas and depends on the native axiom through `D_mul_R`.
-/

open Matrix

def D : Matrix (Fin 13) (Fin 15) ℚ := fun i j =>
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

def R : Matrix (Fin 15) (Fin 13) ℚ := fun i j =>
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

def B : Matrix (Fin 4) (Fin 15) ℚ := fun i j =>
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

def C : Matrix (Fin 2) (Fin 15) ℚ := fun i j =>
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

theorem D_mul_R : D * R = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;> native_decide

theorem rank_D : D.rank = 13 := by
  apply le_antisymm
  · simpa using Matrix.rank_le_height D
  · have h := Matrix.rank_mul_le_left D R
    rw [D_mul_R, Matrix.rank_one, Fintype.card_fin] at h
    exact h

theorem B_mul_D_transpose : B * D.transpose = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;> native_decide

theorem C_mul_D_transpose : C * D.transpose = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;> native_decide

theorem C_independent : C 0 0 * C 1 3 - C 0 3 * C 1 0 = -1 := by
  native_decide

theorem design_rows : 7 + 6 = (13 : Nat) := by decide
theorem cycle_rank : 15 - 4 + 2 = (13 : Nat) := by decide
theorem cut_rank : 4 - 2 = (2 : Nat) := by decide

#print axioms D_mul_R
#print axioms rank_D
#print axioms C_independent
