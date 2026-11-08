# Lean 4 — referências externas e limite do apêndice (R1099)

**Data:** 2026-11-08
**Objetivo:** registrar os repositórios Lean usados como referência bibliográfica e separar o que o livro prova do que apenas consulta.

## 1. Repositórios de referência

| Repositório | Commit | Licença | Cobertura |
|---|---|---|---|
| <https://github.com/Timeroot/Lean-QuantumInfo> | `56e83a9288a3c616285038748e273b3c0e1a36bf` | MIT | informação quântica formalizada |
| <https://github.com/LionSR/QICLean> | `603fc408b9f4c2a50f2475e1e44843fdc0a9c0ac` | Apache-2.0 | informação quântica em Lean |
| <https://github.com/LionSR/TNLean> | `f1b7b26d395d19289d95dcf0f4be342a85c6a787` | Apache-2.0 | redes tensoriais em Lean |

## 2. Como são usados

- Consulta conceitual para definições, tipos e estratégias de prova.
- Comparação de enunciados e notação.
- Verificação de que o apêndice do livro não inventa lema ou tática.
- Nenhum teorema é importado automaticamente para o livro.

## 3. O que o livro prova

O apêndice `livro-core/lean/QuantumTrails.lean` é a única fonte de prova
machine-checked do livro. Ele cobre:

- CHSH quântico: `chsh_bell_eigen` e `chsh_bell_expectation`;
- `cnot_involutive`;
- `bell_normalized`;
- ruído fenomenológico: `phaseDamping_*` e `depolarizing_*`.

Compilação verificada com Lean 4.35.0 + Mathlib commit
`d13f23b723b8a846827a245b89c10fc7d3f11612`, sem `sorry` ou `admit`.

## 4. O que o livro não prova

- Tsirelson geral.
- CPTP completo.
- Fidelidade de hardware, calibração ou ruído real.
- Interpretação de Bohm.
- Eficácia pedagógica.
- Peer review ou aceite editorial.

## 5. Regras

1. Não declarar “provado em Lean” sem o log de compilação e o hash.
2. Não importar teorema externo sem compilar no ambiente do livro.
3. Não confundir formalização de um modelo com medição de laboratório.
4. Preservar a licença e a citação de cada repositório.
5. Se um enunciado depender de Mathlib, fixar o commit do Mathlib.

Formato sugerido de citação:

> Enunciado formalizado com referência metodológica em [repositório], commit [hash], licença [MIT/Apache-2.0]. A prova do livro está em `livro-core/lean/QuantumTrails.lean`, compilada com Lean [versão] e Mathlib [commit].

## 6. Limite

A existência de três repositórios Lean não aumenta a confiança do apêndice. A
confiança vem do compilador e do hash do arquivo efetivamente compilado.
