# SPEC-935-R503 — Repetição pós-reinício + contra-prova multi-problema IMO

**Status**: Em implementação
**Autor**: marceloclaro (orquestrador primário)
**Data**: 2026-09-13
**Pré-requisitos**: R500 (roteamento free) | hipótese registrada: big-pickle
não confirmado na replicação por **estado acumulado do host** (sessão 1h15m).

## 1. Objetivos

1. **Repetir o experimento R499/R500 com o host reiniciado** (uptime 3:33):
   remedir big-pickle (hipótese: volta a resolver) e mimo (confirmar média).
2. **Contra-prova multi-problema**: expandir o corpus IMO de 4 → 9 problemas
   (4 canônicos + 5 novos estilo-IMO com respostas verificáveis por
   enumeração determinística) para testar generalização, não apenas o
   problema nt001.
3. **Validação cruzada**: matriz 9 problemas × 3 modelos (mimo, big-pickle,
   nemotron) na condição C2 (scaffold MASWOS); comparar acertos por problema
   e por modelo; recomputar ranking com n=9.

## 2. Novos problemas (estilo-IMO, verificação determinística)

| id | problema | resposta esperada | verificação |
|---|---|---|---|
| imo-bench-algebra-002 | menor n inteiro positivo tal que 2^n > n^2 | 5 | enumeração n=1..10 |
| imo-bench-number-theory-002 | primos p ≤ 20 tais que p^2 divide 2^p + 1 | {3} | enumeração p primos |
| imo-bench-number-theory-003 | maior expoente e com 3^e dividindo 2023! | 1006 | fórmula de Legendre / fatoração |
| imo-bench-combinatorics-002 | permutações de {1,...,5} com exatamente DOIS máximos locais (int eligiendo extremos) | 16 | enumeração exata n=5 |
| imo-bench-geometry-001 | número de diagonais de um 2023-ágono convexo | 2043230 | fórmula n(n-3)/2 |

TO�TULO: estes novos problemas são **derivados de estilo IMO** (não são
atribuídos a Shortlist oficial): o relatório deve rotulá-los com honestidade.

## 3. Critérios de aceitação

1. RealIMOSolver resolve os 5 novos problemas por enumeração (RED→GREEN).
2. Harness roda 9 problemas com solver determinístico (accuracy esperada:
   nt001/alg001/comb001/alg004 + 5 novos → 8/9 com pleno, alg004 parcial).
3. Benchmark LLM: 9 problemas × 3 modelos na C2; veredito registrado.
4. Ranking recomputado com n=9 (acurácia por modelo sobre 9 problemas).
5. Big-pickle remedido pós-reinício: registra sucesso/falha — falsea ou
   confirma a hipótese do host.
6. Artigo ABNT atualizado com a contra-prova (nova subseção + tabela 9×3).

## 4. Riscos

- Custo de tempo: 27 chamadas LLM (~15–45 min). Mitigação: prompt C2 fixo,
  timeout 95s por chamada; resultado parcial é registrado incrementalmente.
- Sem garantia de que todos os problemas sejam resolvidos pelos modelos:
  esperado (é contra-prova: levanta taxa real, não a melhora).