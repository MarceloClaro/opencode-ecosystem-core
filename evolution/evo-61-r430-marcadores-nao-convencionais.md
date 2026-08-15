# evo-61 — R430: Marcadores socioeconômicos não convencionais no artigo Crateús-IDEB

## Objetivo

Ampliar o manuscrito Crateús-IDEB com **33 marcadores não convencionais** do
Censo Demográfico 2022 (IBGE) por município — gênero, raça/etnia, trabalho,
profissões, atividade econômica, renda, condições de vida, educação/formação e
habitação — cruzados com IDEB 2025 anos iniciais (primário) e IDEB 2023
(sensibilidade), com protocolo exploratório honesto (n=9; bootstrap por cluster
seed 42, 5.000 réplicas; 66 hipóteses; FDR Benjamini–Hochberg + Bonferroni) e
**sem alterar nenhum número aprovado no R428/R429**.

## Contexto técnico

As tabelas clássicas do SIDRA v3 de trabalho/saúde/renda (9622, 9616, 9624,
9717, 9546, 9547, 9730, 9770, 9780, 9580, 9562) responderam **HTTP 500
seletivo** no ambiente (também via apisidra → 400). Solução auditável: usar as
tabelas da **amostra do Censo 2022** (publicação IBGE "Resultados preliminares
da amostra", 2024–2025), que funcionam na API v3: 10261 (posição na ocupação),
10264 (grandes grupos de ocupação + previdência), 10266 (seções de atividade),
10268 (nível de ocupação), 10280/10295/10296 (rendimento), 10056/10061/10062
(educação) + universo 9605/9606/9928/9940. Docentes INEP permanecem bloqueados
(download.inep.gov.br → 60/000) → proxy oficial: % profissionais das ciências e
intelectuais entre ocupados (10264, class 12064) + alfabetização 15+ (R427).

## Mudanças

1. `specs/SPEC-935-R430-crateus-marcadores-nao-convencionais.md` — fontes
   efetivadas (amostra), indisponibilidades declaradas, resultado principal.
2. `academic/papers/crateus_ideb/scripts/baixar_indicadores_r430.py` —
   coletor reescrito para 33 indicadores com operações (variavel, proporcao,
   soma_proporcao); coleta 33/33 OK para os 9 municípios; manifest com URL,
   tabela, variável, classificação, status.
3. `data/processed/indicadores_r430.json` + `manifest_r430.json` — gerados.
4. `academic/papers/crateus_ideb/scripts/analise_r430_marcadores.py` —
   análise com bootstrap vetorizado (numpy, B×n), Spearman/Pearson, IC95
   percentil, sinal estável, FDR (BH) e Bonferroni sobre 66 hipóteses, ranking
   e perfil de Crateús.
5. `outputs/expanded/resultados_r430.json` + `provenance_r430.json` — gerados.
6. `docs/ARTIGO_CRATEUS_RBEP.md` e `latex/ARTIGO_CRATEUS_RBEP.tex` — nova
   subseção **§4.8 "Marcadores socioeconômicos não convencionais (análise
   exploratória)"** (espelhamento 1:1), com tabela-resumo top-10, leitura
   anti-overclaim e nota de indisponibilidades (INEP/docentes; SIDRA 500).
7. `tests/test_r430_marcadores.py` — 15 testes (coleta, análise, perfil,
   manuscrito, termos proibidos, corpo 40k–70k).
8. `outputs/docx/ARTIGO_CRATEUS_RBEP.docx` regenerado; PDF LaTeX recompilado
   (20 páginas, sem erros).

## Resultado principal

- 33 marcadores × 9 municípios; 66 hipóteses; **nenhuma associação sobreviveu
  ao FDR nem a Bonferroni** (menor qBH = 0,49) — leitura correta: precisão
  insuficiente, não prova de ausência.
- Descrição (sem inferência): municípios com mais ocupados sem carteira e mais
  diretores tenderam a IDEB 2025 mais alto; com mais superior completo,
  profissionais e maior nível de ocupação, IDEB mais baixo — contextualizado
  pelo perfil da sede (Crateús: máx em renda/estudo/carteira; mín em
  sem-carteira/pobreza ≤1SM).
- Sensibilidade IDEB 2023 preserva sinais (sem carteira +0,65; mulheres e
  técnicos −0,63; profissionais −0,55), sem sobrevivência ao ajuste.

## Verificação

- `pytest tests/test_r430_marcadores.py` → 15 passed.
- Suíte R420–R430 → **125 passed**.
- `python3 -m marceloclaro.cli doctor` → 10 pass / 2 warn pré-existentes
  (loop_specs, external_clis) / 0 failed.
- PDF 20 páginas; DOCX com 5 tabelas (nova §4.8 incluída).
