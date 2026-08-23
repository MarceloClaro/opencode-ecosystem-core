---
spec_id: SPEC-935-R445
title: AlphaGeometry Neuro-Simbólico, Auto-Formalização Bidirecional e Validação Cruzada
component: integrations/deepmind, marceloclaro/orchestrator, marceloclaro/cli, doctor
status: verified
round_id: R445
test_file: tests/test_r445_alphageometry_autoformalization.py
---

# SPEC-935-R445 — AlphaGeometry Neuro-Simbólico, Auto-Formalização Bidirecional e Validação Cruzada

## 1. Contexto e Motivação

Para expandir o raciocínio científico do OpenCode Ecosystem Core para o domínio da geometria formal olímpica e garantir a integridade entre raciocínio informal e código formal:
1. **AlphaGeometry Neuro-Simbólico**: Implementação do motor de geometria combinando Base Dedutiva (*Deductive Database - DD*) e o Método Algébrico de Wu (*Wu's Method*) com coordenadas baricêntricas/cartesianas e renderização TikZ/SVG.
2. **Auto-Formalização Bidirecional**: Tradução autônoma de linguagem natural/LaTeX para Lean 4 / Mathlib 4 e decompilação explicativa de código formal para demonstrações passo a passo em português formal.
3. **Validação Cruzada Tripla (*Triple Cross-Validation*)**: Verificação concorrente entre a demonstração textual informal, o sistema de polinômios de Wu/SymPy e a checagem formal sintática/compilada em Lean 4.

---

## 2. Requisitos e Componentes

### R445.1 — Motor de Geometria AlphaGeometry (`geometry_engine.py`)
- `GeometricDeductiveDatabase`: Deduções geométricas de colinearidade, paralelismo, ortogonalidade, ciclicidade e triângulos semelhantes.
- `WuGeometryProver`: Conversão de hipóteses geométricas em ideais polinomiais e verificação da conclusão por pseudo-divisão e anulação de restos polinomiais.
- `TikzGeometryRenderer`: Exportação automática da construção geométrica para LaTeX TikZ e SVG vetorial.
- `OpenCodeAlphaGeometry`: Solucionador unificado que coordena a base dedutiva, o método de Wu e a exportação visual.

### R445.2 — Motor de Auto-Formalização Bidirecional (`autoformalizer.py`)
- `AutoFormalizerEngine`:
  - `informal_to_lean4(text, domain)`: Converte texto matemático ou hipóteses informais em teoremas formais estruturados em Lean 4 (`import Mathlib... theorem... := by ...`).
  - `lean4_to_informal(code, language)`: Decompila e explica scripts Lean 4 em demonstrações matemáticas rigorosas em linguagem natural.
  - `cross_validate(informal, lean_code)`: Executa validação cruzada identificando consistência semântica, alinhamento de variáveis e completude de prova (rejeitando `sorry`).

### R445.3 — Integração no Orquestrador e CLI
- Métodos nativos no `MarceloClaroOrchestrator`:
  - `solve_geometry_problem(problem_spec)`
  - `autoformalize_to_lean4(statement, domain)`
  - `explain_lean4_proof(code, language)`
  - `cross_validate_reasoning(informal_text, lean_code)`
- Subcomandos CLI no `marceloclaro.cli`:
  - `python3 -m marceloclaro.cli geometry "<spec_geometria>"`
  - `python3 -m marceloclaro.cli autoformalize "<enunciado_informal>"`
- Check do `doctor`: `geometry_autoformalization_engine` (18 checks estruturais totais).

---

## 3. Critérios de Aceite (SDD/TDD)

1. `test_geometry_deductive_database`: Dedução de propriedades geométricas elementares (ponto médio, paralelismo, ortogonalidade).
2. `test_wu_method_polynomial_prover`: Demonstração exata de teoremas geométricos por anulação de restos polinomiais (ex: Teorema do Ponto Médio / Triângulo Retângulo).
3. `test_tikz_renderer_output`: Geração de código TikZ e SVG sintaticamente válidos.
4. `test_informal_to_lean4_generation`: Tradução de problemas algébricos e aritméticos para código formal Lean 4 com Mathlib.
5. `test_lean4_to_informal_decompilation`: Tradução explicativa de scripts Lean 4 para português formal.
6. `test_cross_validation_consistency`: Identifica consistência e detecta inconsistências ou omissões (`sorry`) entre código e texto.
7. `test_orchestrator_and_cli_geometry_autoformalize`: Execução integrada no `MarceloClaroOrchestrator` e CLI.
8. `test_doctor_check_18_geometry`: Validação do 18º check estrutural no `doctor` (18 checks ativos, 0 fails).
