---
spec_id: SPEC-935-R444
title: Integração Nativa Lean 4 & Motor de Igualdade Saturada E-Graph (Egglog)
component: integrations/deepmind, marceloclaro/orchestrator, marceloclaro/cli, doctor
status: verified
round_id: R444
test_file: tests/test_r444_lean4_egraph_saturation.py
---

# SPEC-935-R444 — Integração Nativa Lean 4 & Motor de Igualdade Saturada E-Graph (Egglog)

## 1. Contexto e Motivação

Para superar os dois gaps técnicos identificados no diagnóstico comparativo com o Google DeepMind Superhuman:
1. **Verificação Machine-Checked em Lean 4**: Transição da verificação puramente algébrica para a linguagem de assistente de provas interativo **Lean 4 / Mathlib 4**, gerando scripts formais verificáveis por compilador.
2. **Descoberta Automatizada de Lemas via E-Graph (Equality Saturation)**: Implementação de um motor de grafos de equivalência (*E-Graph*) e saturação de igualdade (*Egg/Egglog paradigm*) para simplificação de termos e derivação autônoma de identidades matemáticas complexas a partir de axiomas fundamentais.

---

## 2. Requisitos e Componentes

### R444.1 — Verificador e Gerador Lean 4 (`lean4_verifier.py`)
- `Lean4Bridge` / `Lean4ProofVerifier`:
  - Detecção dinâmica de binários `lean`, `lake` ou `lean4` no PATH e ambiente.
  - Modo híbrido resiliente: execução nativa de compilador quando presente + analisador estático de sintaxe Lean 4 com validação de táticas (`intro`, `exact`, `apply`, `rw`, `ring`, `linarith`, `omega`, `aesop`, `simp`).
  - Detecção rigorosa de `sorry` (incompletude de prova).
  - Exportação de arquivos `.lean` e estrutura de projeto `lakefile.lean`.

### R444.2 — Motor de E-Graph e Saturação de Igualdade (`egraph_rewriter.py`)
- `EClass`, `ENode`, `EGraph`: Estrutura de dados com união-busca (*Union-Find*) e fechamento por congruência (*Congruence Closure*).
- `EqualitySaturationEngine`: Aplicação iterativa de regras de reescrita bidirecionais ($L \leftrightarrow R$), descobrindo identidades algébricas e simplificando termos para a menor forma canônica sem loop infinito.

### R444.3 — Integração com AlphaProof e Orquestrador
- Extensão do `OpenCodeAlphaProof` com a tática `EGraphSaturation` e exportação direta em código Lean 4.
- Métodos nativos no `MarceloClaroOrchestrator`:
  - `orchestrator.lean4_verify_code(code)`
  - `orchestrator.lean4_export_theorem(theorem_name, statement, proof_script)`
  - `orchestrator.egraph_saturate_term(expr, rules)`
- Subcomandos CLI no `marceloclaro.cli`:
  - `python3 -m marceloclaro.cli lean4 "<codigo_ou_arquivo>"`
  - `python3 -m marceloclaro.cli egraph "<expressao>"`
- Check do `doctor`: `lean4_egraph_engine` (17 checks totais).

---

## 3. Critérios de Aceite (SDD/TDD)

1. `test_lean4_syntax_and_tactic_validation`: Valida scripts corretos em Lean 4 (com `ring`, `linarith`, `intro`) e rejeita códigos com erros sintáticos ou `sorry`.
2. `test_lean4_file_and_lake_export`: Exporta projetos e arquivos `.lean` bem-estruturados com metadados.
3. `test_egraph_congruence_closure`: Valida união de classes de equivalência e congruência ($f(a) \equiv f(b)$ quando $a \equiv b$).
4. `test_egraph_equality_saturation_simplification`: Simplifica expressões matemáticas complexas (ex.: $(x \cdot 1) + 0 \to x$) via saturação.
5. `test_egraph_lemma_discovery`: Descobre identidades não triviais a partir de regras axiomáticas.
6. `test_alphaproof_lean4_generation`: AlphaProof gera saída paralela em código formal Lean 4.
7. `test_orchestrator_and_cli_lean4_egraph`: Métodos do orquestrador e comandos CLI executam perfeitamente.
8. `test_doctor_check_17_lean4_egraph`: Diagnóstico doctor passa com 17/17 checks ativos.
