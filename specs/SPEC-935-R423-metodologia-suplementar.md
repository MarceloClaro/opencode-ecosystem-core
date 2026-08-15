# SPEC-935-R423 — Melhorias metodológicas pós-peer-review (LOOCV, cluster, TOST)

## Objetivo

Implementar as três melhorias metodológicas recomendadas pelo blind peer
review emulado (R422), sem alterar nenhum número já reportado:

1. **ID 2 — Dispersão dos folds de teste da LOOCV** (seção 4.3 / Tabela 3):
   reportar mediana, DP, IQR, mínimo/máximo e % de folds positivos do
   ρ_teste por país, além de associar a instabilidade ao tamanho amostral
   do país (n 20–54). Evidencia que a baixa transferibilidade mistura
   ausência de generalização com instabilidade amostral de n pequeno.
2. **ID 3 — Especificação comparativa sem cluster** (seção 4.5 / Tabela 5):
   executar a mesma especificação FE de país/ano com erros padrão
   homocedásticos (sem cluster) e comparar coeficiente, SE, IC95% e p.
   Demonstra quantitativamente o estreitamento dos ICs invocado no texto
   (prática recomendada por Cameron e Miller, 2015).
3. **ID 4 — Equivalência / limites de detecção** (seção 4.5):
   para o coeficiente nulo do painel FE (0,073; IC95% [−0,169; 0,314]),
   reportar (a) o menor efeito detectável (MDES) dado o SE clusterizado e
   poder de 80% e (b) teste de equivalência TOST com bounds de ±0,10 e
   ±0,05 no log da matrícula terciária.

## Critérios de aceitação

1. Script novo `scripts/analyze_metodologia_suplementar.py` reutiliza as
   funções de `analyze_expanded.py` e o painel processado, sem reescrever
   os artefatos R412/R418/R419.
2. Novos artefatos em `outputs/expanded/`:
   - `tabela12_loocv_dispersao.csv` (mediana, DP, IQR, min, max, % > 0,
     correlação n × ρ_teste);
   - `tabela5b_cluster_comparativo.csv` (coef, SE, IC95%, p com e sem
     cluster);
   - `tabela13_tost_deteccao.csv` (MDES; TOST ±0,10 e ±0,05 com p);
   - `provenance_r423.json` com todas as chaves e hashes.
3. Texto: subseção nova 4.10 (limites de detecção e equivalência), nota na
   4.3 sobre dispersão da LOOCV e nota comparativa na 4.5/Tabela 5 —
   espelhadas no MD e TeX, PDF e DOCX regenerados (0 Overfull).
4. Números antigos inalterados (0,073; [−0,169; 0,314]; p = 0,555;
   0,751/0,542).
5. Testes `tests/test_r423_metodologia_suplementar.py` (RED→GREEN):
   artefatos existem, valores-chave esperados, MD ≥ TeX.
6. Anti-overclaim: TOST com p ≥ 0,05 não é reportado como "equivalência
   demonstrada"; apenas "não se rejeita efeito relevante em magnitude
   superior a [bound]".

## Não escopo

- Alterar números já publicados nas seções 4.1–4.9.
- Reexecutar ML (seção 4.6).
- Novas coletas de dados.

## Verificação

- Suíte R408–R423 verde (351 + novos).
- LaTeX 19–20 páginas, 0 Overfull/Underfull; DOCX regenerado.
- Doctor 10/12 pass, 0 failed; ciclo R423 no EvolutionRegistry + evo-54.
