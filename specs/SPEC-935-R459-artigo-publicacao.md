---
spec_id: SPEC-935-R459
title: Artigo científico — "Diversificação pós-ranqueamento no RAG científico: uma avaliação empírica do esquema posicional de Recamán vs MMR"
component: publications/r459_article/ (LaTeX, figuras, referencias)
status: green
round_id: R459
---

# SPEC-935-R459 — Artigo de publicação (Qualis A1 / conferência IR)

## Objetivo

Produzir um artigo científico **submissível** que reporte, de forma **honesta e
reprodutível**, o achado empírico do experimento de coorte (R458) e a proposta
pós-Recamán do manual técnico (R456), na área de **Recuperação de Informação
(IR) / Retrieval-Augmented Generation (RAG)**, contribuindo com:

1. A **formulação matemática** da diversificação pós-ranqueamento determinística
   (sequência de Recamán, OEIS A005132) e da métrica `Div(S)` (Eq. 6.1 do manual).
2. Uma **avaliação empírica controlada** comparando três estratégias de seleção
   pós-ranqueamento: **top-k (estado atual)**, **MMR** e **Recamán**.
3. Um **achado factual e reprodutível**: no corpus-piloto, Recamán **empata** com
   o top-k em diversidade (`gain_div = 0.0`) enquanto MMR supera ambas
   (`Div 0.75 vs 0.50`) — revelando a **limitação estrutural** de diversificadores
   **posicionais** (operam sobre posição, não âncora/fonte) frente a rankings
   "localmente monopolistas".

## Contribuições (sem overclaim)

- C1. Formalização da diversificação pós-ranqueamento por Recamán e da métrica
  `Div(S)` sobre âncoras canônicas (aditiva, determinística, O(K)).
- C2. *Benchmark* de coorte aberto e reprodutível (corpus-piloto determinístico,
  `benchmarks/cohort_recaman.py`) para comparar estratégias de diversificação.
- C3. Evidência empírica controlada de que **diversificadores posicionais** (que
  não consultam o conteúdo) podem **coincidir com o top-k** sob ranking
  monopolista, enquanto diversificadores baseados em dissimilaridade de conteúdo
  (MMR) espalham por fonte — com implicações práticas para **landscape/cobertura
  de consultas multicunha em RAG**.

## Dados empíricos autorizados (APENAS os do R458 — proibido inventar)

Quadro 1 (médias, corpus-piloto de 6 ângulos × 3 docs, n_queries=4, k=4):
| Estratégia | Div(S) | groundedness | coverage |
|---|---|---|---|
| atual (top-k) | 0.500 | 0.4561 | 0.667 |
| MMR (λ=0.7)  | 0.750 | 0.4256 | 0.917 |
| Recamán       | 0.500 | 0.4561 | 0.667 |

Achados autorizados: `gain_div_vs_atual=0.0`; `loss_rel_groundedness(Recamán)=0.0`;
`mmr_supera_recaman=true`. Veredito H2: `refuta_H2`.

**Limites obrigatórios** (anti-overclaim):
- É observação em **corpus-piloto controlado/sintético**; NÃO generaliza para
  produção/corpus real.
- MMR usar similaridade por **sobreposição de tokens** (sem embeddings externos).
- Não há comparação com LLM/qualidade de texto gerado — apenas seleção/recuperação.
- Não são alegações de superioridade da proposta; o resultado **qualifica** a proposta.

## Estrutura do manuscrito (IAS / ACM / IEEE sugestão)

1. Introdução (problema: RAG mede relevância mas não diversidade; lacuna de métrica).
2. Trabalhos relacionados (BM25 ~ Robertson & Zaragoza 2009; RAG ~ Lewis 2020;
   MMR ~ Carbonell & Goldstein 1998; diversificação em IR).
3. Metodologia: proposta Recamán + métrica Div(S) (Eq. 6.1), desenho do corpus,
   protocolo de coorte, baseline MMR, métricas de avaliação, correções de validade.
4. Resultados: Quadro 1 + tabela por-query (cohort_report.json) + figuras.
5. Discussão: por que o esquema posicional falha sob monopolismo; implicações para
   diversificação de âncoras; limitações; trabalho futuro.
6. Conclusão.
7. Referências (ABNT/BNP ou estilo ACM — definir).

## Critérios de Aceitação Executáveis

- `article_dir_exists` — existe `publications/r459_article/`.
- `manuscript_main` — `main.tex` compilável (LaTeX) gerando `.pdf`.
- `has_abstract` — resumo (português) e abstract (inglês).
- `has_intro_relwork_method` — seções 1–3 presentes.
- `has_results`: Quadro 1 com valores REAIS do R458 (0.500/0.750/0.4561/0.4256/0.667/0.917).
- `has_discussion_limitations` — seção de discussão com limitações explícitas.
- `has_references` — referências formatadas; citações casam com bibliografia.
- `no_invented_numbers` — nenhum número fora do cohort_report.json.
- `no_overclaim` — texto contém rótulo de escopo ("corpus-piloto", "não generaliza",
  "sem embeddings externos").
- `verdict_reported`: o artigo declara `refuta_H2` de forma explícita.
- `compiles` — `pdflatex`/`latexmk` gera PDF sem erros fatais.
- `passes_quality_gate` — auditoria MASWOS/Qualis A1 (agentes 13/31/34) sem ressalvas
  bloqueantes de sobre-alegação.

## Não objetivos

- Não inventar resultados de coorte em corpus real (não realizado).
- Não promover o diversificador ao pipeline padrão.
- Não alegar superioridade da proposta sobre MMR (o observado foi o oposto).
- Não gerar benchmark em larga escala/embeddings (fora do escopo).
