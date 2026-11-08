---
name: verificacao-lean-quantum
description: Verifica identidades matemáticas de informação quântica em Lean 4 + Mathlib, incluindo portas, CHSH, normalização e modelos fenomenológicos de ruído. Use ao formalizar ou revisar provas; não declare hardware, calibração, fidelidade ou Bohm como provados pelo Lean.
metadata:
  version: "1"
  origem: "R1099 — QuantumTrails.lean"
---

# Verificação Lean 4

## O que provar

- `H² = I`, `X² = I`, `Z² = I`, `HZH = X`.
- `P(0)+P(1)=1`.
- CHSH clássico `S ≤ 2`.
- CHSH quântico `CHSH|Φ+⟩ = 2√2|Φ+⟩`.
- Modelos fenomenológicos: phase damping e depolarizing.

## Comando

```bash
cd livro-core/lean
lake env lean QuantumTrails.lean
```

## Regras

- Sem `sorry` e sem `admit`.
- Teorema novo exige nome, enunciado e comentário de escopo.
- Separe `machine-checked` de `calculated` e `measured`.
- O limite de Tsirelson geral e canais CPTP completos não estão formalizados.

## Saída

Atualizar `LEAN_QUANTUM.md` e `LEDGER_AFIRMACOES.md` com o status real.
