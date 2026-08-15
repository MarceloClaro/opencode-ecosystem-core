# evo-54 — R423: Melhorias metodológicas pós-peer-review

## Objetivo

Implementar as três melhorias metodológicas recomendadas pelo blind peer
review (R422, IDs 2–4) sem alterar nenhum número já publicado.

## Resultados

1. **ID 2 — Dispersão da LOOCV** (`tabela12_loocv_dispersao.csv`):
   a média de ρ_teste (0,542) esconde assimetria: mediana 0,778, DP 0,508,
   83% dos folds positivos; a média baixa é puxada por poucos folds
   negativos extremos. A instabilidade é maior em países com poucas
   observações (corr n_obs × |ρ_teste| = 0,248; p = 0,004). Qualifica a
   leitura: parte da queda 0,751 → 0,542 reflete imprecisão amostral, não
   apenas ausência de transferibilidade.
2. **ID 3 — Cluster comparativo** (`tabela5b_cluster_comparativo.csv`):
   mesma especificação FE sem cluster → coef 0,073 (SE 0,055; IC
   [−0,036; 0,182]; p = 0,190). Confirmou quantitativamente o
   estreitamento do IC; a conclusão de não-detecção permanece.
3. **ID 4 — MDES + TOST** (`tabela13_tost_deteccao.csv`): MDES = 0,173
   (poder 80%, α 5%) no log da matrícula; TOST ±0,10 (p = 0,329) e ±0,05
   (p = 0,644) — não se declara equivalência; leitura correta:
   não-detecção.

## Mudanças

- `scripts/analyze_metodologia_suplementar.py` (reutiliza analyze_expanded
  e o painel processado; artefatos novos, sem sobrescrever R412/R418/R419).
- MD e TeX: nota de dispersão na 4.3; Tabela 5b comparativa na 4.5; nova
  subseção 4.10 (limites de detecção e equivalência) com Tabela 13.
- Testes R423 (15) + ajustes de regressão: R419 (split 4.9 termina em
  "### 4.10"), R421 (localiza Tabela 8 por conteúdo, não por índice).

## Verificação

- Suíte R408–R423: **366 testes passed**.
- LaTeX: 20 páginas, 0 Overfull, 0 Underfull; DOCX regenerado (16 tabelas).
- Doctor: 10/12 pass, 0 failed.
- Anti-overclaim: TOST com p ≥ 0,05 é reportado como "não permite declarar
  equivalência", nunca como equivalência demonstrada.

## Lições

- A mediana dos folds de teste (0,778) vs média (0,542) mostra que
  estatísticas agregadas de LOOCV sem dispersão podem enganar; sempre
  reportar distribuição quando n de países for pequeno.
- Tabelas suplementares adicionadas no corpo mudam índices fixos em testes
  de DOCX — localizar por conteúdo é mais robusto.
- MDES explicita o que "não discernível" significa (0,173 no log), evitando
  leituras de "efeito nulo" indevidas.
