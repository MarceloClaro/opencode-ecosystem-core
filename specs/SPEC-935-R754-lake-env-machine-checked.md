---
spec_id: SPEC-935-R754
title: Verificação Lake-Env com Mathlib — machine_checked no Projeto
component: integrations/deepmind/lean4_verifier, integrations/lean_proof_mcp, tests/test_r754
status: proposed
round_id: R754
test_file: tests/test_r754_lake_env.py
---

# SPEC-935-R754 — Lake-Env com Mathlib

## 1. Contexto

R444 entrega `machine_checked` para Lean núcleo e `syntax_verified` com fallback honesto
quando Mathlib está ausente no projeto (R753). Com projeto lake + Mathlib pré-compilado
via `lake exe cache get` (`leanprover/lean4:v4.34.1`, `mathlib rev v4.34.1`), `lake env lean`
atingiu exit 0 em 47s para `simp/omega/ring` (R754). Falta expor esse caminho no pipeline,
sem quebrar o comportamento sem projeto.

## 2. Requisitos

### R754.1 — `Lean4ProofVerifier.verify_lean_code(code, project_dir=None)`

- `project_dir=None`: comportamento R444/R753 inalterado (bare `lean`, fallback Mathlib-ausente).
- `project_dir` com `lakefile.toml` + `.lake`: escreve temporário dentro do projeto e executa
  `lake env lean <tmp>` com `cwd=project_dir`, timeout 300s.
- Exit 0 → `machine_checked`. `sorry`/`admit` continuam bloqueio antes de qualquer execução.
- Erro de prova real → `compiler_error` (sem fallback). Ausência de `lake`/projeto inválido →
  fallback para o caminho sem projeto, com nota na proveniência; nunca alegar `machine_checked`.

### R754.2 — MCP `lean_verify(code, project_dir=None)`

- Repassa `project_dir`; `provenance` inclui `project_dir` e `via: lake-env|bare-lean`.

## 3. Aceite (`tests/test_r754_lake_env.py`, pula se projeto demo ausente)

1. `test_machine_checked_mathlib_no_projeto`: `simp/omega/ring` com `import Mathlib.Tactic` → `machine_checked`.
2. `test_sorry_bloqueado_no_projeto`: `sorry` → `is_valid=False`.
3. `test_prova_errada_falha_no_projeto`:(Uma igualdade falsa, ex. `2 + 2 = 5` com `decide`) → `compiler_error`, sem fallback para válido.

## 4. Invioláveis

- Backward compatible: chamada sem `project_dir` comporta-se como R753.
- `sorry`/`admit`/`axiom` não declarado sempre bloqueiam, com ou sem projeto.
- Sem projeto válido nunca `machine_checked` para código com `import Mathlib`.
