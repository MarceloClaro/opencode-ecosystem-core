# SPEC-935-R499 — Estudo Empírico: Raciocínio Automatizado em Problemas da IMO + Benchmark LLM Free + Raio-X da Orquestração

**Status**: Concluída (implementação v1; manuscrito draft + pacote de submissão gerados)
**Autor**: marceloclaro (orquestrador primário)
**Data**: 2026-09-13
**Pré-requisitos**: R442 (IMOBenchmarkHarness/GradingHead/FormalProofVerifier), R489 (paisagem DeepMind: AlphaGeometry/AG2/Aletheia)

## 0. Adendo — Benchmark de LLMs free reais e raio-x da orquestração

- **Dados reais**: `research/imo_study/llm_free_benchmark.json` (6 trials,
  2 modelos free × 3 condições) + `llm_free_ranking.json`.
- **Ranking free**: 1º mimo-v2.5-free (score 0.987, latência 23.8 s) >
  2º nemotron-3-ultra-free (score 0.709, latência 107.4 s).
- **Fator decisivo**: scaffold MASWOS (C2) elevou acurácia de 0% (C0/C1) para
  100% (C2) em ambos os modelos — a orquestração decide resultado utilizável.
- **Ineficiências mapeadas**: llama3.2 local (latência >10 min/16 estágios,
  descartado); deepseek-v4-flash (saldo insuficiente); gemini-2.5-flash (erro
  de servidor); C1 (contexto sem scaffold) piorou latência sem ganho.
- **Gate de verificação**: `FormalProofVerifier` confirmou 7³−3⁵=(7+3)².
- **Relatório completo**: `research/imo_study/raio-x_orquestracao.md`.

## 1. Objetivo

Produzir um **artigo científico piloto de submissão real** (pacote LaTeX/PDF/DOCX)
cujo **objeto de estudo são problemas da IMO** (corpus amostral canônico do
IMO Shortlist 2020–2022 já curado no harness R442), avaliando o raciocínio
automatizado do ecossistema com **solvers determinísticos sem acesso à resposta**
(anti-leak), e comparando contextualmente com a literatura (AlphaGeometry/AG2/Aletheia)
**sem reivindicar superioridade** (anti-overclaim, CORRIGENDUM).

## 2. Problema de pesquisa

- **P1**: Em que taxa um ecossistema de raciocínio determinístico (enumeração
  exata + álgebra simbólica SymPy + verificação formal) resolve corretamente os
  4 problemas canônicos do IMO-AnswerBench sample (Shortlist 2020–2022)?
- **P2**: Que **limitações de formalização** emergem quando paráfrases de
  enunciado (harness) divergem da semântica matemática oficial (ex.: "quotient"
  = divisão inteira vs racional; "local maximum" = interior vs inclui extremos)?
- **P3**: Como classificar honestamente os resultados na escala 0–7 do
  GradingHead, sem leak e sem overclaim?

## 3. Corpus (fixo, do harness R442)

| id | categoria | short_answer | fonte |
|---|---|---|---|
| imo-bench-algebra-001 | Algebra | 3 | IMO Shortlist 2021 |
| imo-bench-algebra-004 | Algebra | 2^{u-2} | IMO Shortlist 2021 |
| imo-bench-number-theory-001 | Number Theory | (7, 3) | IMO Shortlist 2022 |
| imo-bench-combinatorics-001 | Combinatorics | 2^{n-1} | IMO Shortlist 2020 |

## 4. Solver determinístico real (sem acesso a short_answer)

Novo módulo `integrations/deepmind/imo_real_solver.py`:

- `RealIMOSolver.solve(problem) -> str` — para cada categoria:
  - **algebra-001**: enumeração exata de N em 1..60 com `fractions` e **divisão
    inteira** (quotient floor); retorna o conjunto de N que satisfaz a soma
    alvo. Resultado esperado: N=3.
  - **algebra-004**: validação numérica extensiva da desigualdade para u=2..6 e
    grade de t (não prova formal); candidato C = 2^{u-2} verificado por
    amostragem; resultado "parcial: evidência numérica forte, sem prova formal".
  - **number-theory-001**: enumeração exata de primos p,q em 2..400 testando
    p^3 − q^5 = (p+q)^2. Resultado esperado: (7,3).
  - **combinatorics-001**: enumeração exata de permutações para n=1..6 com
    definição de **local maximum incluindo extremos**; verificação da fórmula
    2^{n-1}. Resultado esperado: confirmado para n=1..6.

- **Anti-leak**: o solver NUNCA recebe `short_answer`; a solução gerada é o
  texto da verificação exata (valores encontrados + método), não eco da
  resposta.

## 5. Critérios de aceitação (gate SDD)

1. `RealIMOSolver` resolve corretamente (sem receber short_answer):
   - nt001 → (7, 3) exato
   - alg001 (floor) → N=3
   - comb001 → 2^{n-1} para n=1..6
   - alg004 → conclusão "parcial/evidência numérica", nunca score 7 sem prova
2. `IMOBenchmarkHarness.run_benchmark(solver_fn=RealIMOSolver.solve)` retorna
   métricas sem leak; textos de solução NÃO contêm a short_answer antes da
   dedução.
3. Relatório do estudo (dados reais) alimenta o manuscrito MASWOS: seções
   método/resultados com números da execução real; **nenhuma alegação
   "superhuman"/"melhor que AlphaGeometry"** — comparação contextual da
   literatura, não benchmark head-to-head.
4. Pacote de submissão: LaTeX + PDF + DOCX gerados a partir do manuscrito
   aprovado na banca simulada (gate honesto ≥ nota mínima).
5. Testes: `tests/test_r499_imo_real_solver.py` cobre os 4 problemas, o
   anti-leak e o relatório sem overclaim.

## 6. Riscos e mitigação

- **Risco 1: leak por eco** — mitigado: solver determinístico sem short_answer;
  teste verifica ausência de "3"/"(7,3)"/"2^{u-2}"/"2^{n-1}" em solução pré-grading? (não — a solução CONTERÁ os valores encontrados; o leak é ausência de dedução. O teste garante presença de dedução/justificativa de cálculo).
- **Risco 2: overclaim de "melhor que DeepMind"** — proibido no manuscrito;
  banca simulada verifica.
- **Risco 3: corpus amostral pequeno (4 problemas)** — declarado como limitação
  explícita; generalização não reivindicada.
- **Risco 4: definição divergente de problema (alg001 frac vs floor; comb001
  interior vs extremos)** — tratado como **achado** (P2), não como falha
  escondida.

## 7. Entregáveis

- `integrations/deepmind/imo_real_solver.py` (solver determinístico)
- `tests/test_r499_imo_real_solver.py` (testes)
- `research/imo_study/` — dados, relatório, manuscrito MASWOS, pacote de submissão