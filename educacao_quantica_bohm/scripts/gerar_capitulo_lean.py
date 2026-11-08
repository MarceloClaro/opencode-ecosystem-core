#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o apêndice com o código Lean 4 verificado."""
from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LEAN = RAIZ.parent / "livro-core" / "lean" / "QuantumTrails.lean"
SAIDA = RAIZ / "livro_pixel" / "LEAN_QUANTUM.md"


def main() -> None:
    codigo = LEAN.read_text(encoding="utf-8").rstrip()
    texto = f"""# Verificação formal em Lean 4 {{#lean-quantum}}

As identidades matemáticas usadas nas trilhas foram formalizadas em **Lean 4 +
Mathlib**. O arquivo é `livro-core/lean/QuantumTrails.lean`. Ele compila sem
`sorry` e sem `admit` no ambiente desta edição (Lean 4.35.0; Mathlib no commit
`d13f23b723b8a846827a245b89c10fc7d3f11612`).

## O que o Lean prova

| Teorema | O que prova | Onde é usado |
|---|---|---|
| `H_mul_H` | `H² = I` | Circuitos, interferência |
| `X_mul_X` | `X² = I` | Porta X, NOT quântico |
| `Z_mul_Z` | `Z² = I` | Fase, H-Z-H |
| `H_mul_Z_mul_H` | `H Z H = X` | Interferência e base X |
| `sqrt2_sq` | `(√2)² = 2` | Normalização, CHSH |
| `inv_sqrt2_sq` | `(1/√2)² = 1/2` | Hadamard |
| `quantum_chsh_sq` | `(2√2)² = 8` | Limite quântico de CHSH |
| `prob_sum` | `P(0)+P(1)=1` | Medição |
| `chsh_classical` | `S ≤ 2` para modelo local determinístico | Contraste clássico |
| `cnot` | Tabela-verdade do CNOT | Circuitos |
| `cnot_involutive` | CNOT aplicado duas vezes devolve a entrada | Circuitos |
| `bell_normalized` | Estado de Bell normalizado | Emaranhamento |
| `chsh_bell_eigen` | CHSH|Φ+⟩ = 2√2|Φ+⟩ | Valor quântico de CHSH |
| `chsh_bell_expectation` | ⟨CHSH⟩ = 2√2 no estado de Bell | Valor quântico de CHSH |
| `phaseDamping_p0` | Phase damping preserva a população | Ruído de fase |
| `phaseDamping_coh` | Coerência decai por (1−γ) | Ruído de fase |
| `phaseDamping_coh_abs_le` | Phase damping não aumenta a coerência | Ruído de fase |
| `depolarizing_p0` | Fórmula da população sob depolarizing | Ruído depolarizante |
| `depolarizing_zero` | p=0 devolve o estado original | Ruído depolarizante |
| `depolarizing_one_p0` | p=1 leva a população a 1/2 | Ruído depolarizante |
| `depolarizing_p0_nonneg` | População permanece ≥ 0 | Normalização |
| `depolarizing_p0_le_one` | População permanece ≤ 1 | Normalização |

O teorema `chsh_classical` percorre as 16 combinações de escolhas de Alice e
Bob e verifica que `a0·b0 + a0·b1 + a1·b0 − a1·b1 ≤ 2`. O valor quântico
`2√2` é formalizado para o estado de Bell e para as escolhas de observáveis
usadas no livro: `chsh_bell_eigen` prova que `|Φ+⟩` é autovetor de `CHSH` com
autovalor `2√2`, e `chsh_bell_expectation` prova o valoresperado. O limite de
Tsirelson geral não é formalizado; o que está provado é o caso específico.

Os modelos de ruído são **fenomenológicos**: `phaseDamping` e `depolarizing`
atuam sobre população e coerência real de um qubit. Eles provam preservação de
população, decaimento de coerência e normalização, mas **não** são uma
formalização completa de canais CPTP.

## O que o Lean não prova

- counts de hardware, calibração, fidelidade, ruído;
- a interpretação de Bohm;
- a vantagem quântica de um algoritmo específico;
- a validade de uma execução ou de um backend.

Essas afirmações são empíricas e dependem de dados, task IDs e desenho
experimental. O Lean prova a matemática; o experimento prova (ou não) a física.

## Como verificar

Pré-requisitos: `elan` e o projeto `livro-core/lean` com Mathlib.

```bash
cd livro-core/lean
lake env lean QuantumTrails.lean
```

Se o comando terminar sem mensagens de erro, os teoremas foram verificados pelo
compilador. Se você não tem Lean instalado, a tabela acima e a explicação do
texto bastam para a leitura; o código é para quem quiser conferir a prova.

## Código Lean completo {{#lean-codigo}}

```lean
{codigo}
```

> **Regra:** não declare “provado” o que o compilador não verificou. O status
> deste arquivo é: compilado nesta edição com o comando acima. Se você alterar
> o código, o status volta a “não verificado” até nova compilação.
"""
    SAIDA.write_text(texto, encoding="utf-8")
    print(f"Apêndice Lean: {SAIDA}")


if __name__ == "__main__":
    main()
