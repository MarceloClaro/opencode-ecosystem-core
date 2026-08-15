# evo-53 — R422: Blind Peer Review emulado + correções de submissão

## Objetivo

Submeter o manuscrito final (R410–R421) a um blind peer review emulado de
alta severidade (3 revisores) antes da revisão humana, corrigir os achados
exigidos e regenerar todos os artefatos.

## Resultado do review

- Veredictos: 3× "Revisão menor" — **nenhum bloqueio metodológico**.
- Verificação aritmética exaustiva confirmou toda a cadeia de números
  (Δ = 0,604, IC95%, amostragem 217/135/82, LOOCV, FE, ML, Tabela 8).
- 12 achados: 0 críticos; 1 de correção obrigatória (ID 9 — RBEP);
  6 menores; 5 informativos.

## Correções aplicadas (8 achados)

| ID | Correção |
|---|---|
| 9 | RBEP = Revista Brasileira de Estudos **Pedagógicos** (era "de População") — MD, TeX, PDF, DOCX |
| 6 | Introdução: "validações cruzadas por país e por tempo" → "por país e a análises de subperíodos" |
| 7 | Seção 4.8: ressalva demográfica da matrícula bruta (composição etária) |
| 8 | Tabela 10: rótulo "Oriente Médio, Norte da África, Afeganistão e Paquistão" |
| 11 | Nova seção "Declarações" (conflito de interesses, financiamento, disponibilidade de dados/código) |
| 1 | Nota de arredondamento "0,7508 − 0,1465 = 0,6043" |
| 5 | Proveniência da seção 4.7 aponta também para `channels/provenance_r413.json` |
| 10 | Datas explicitadas: download 13/08, verificação API 14/08 |

## Não resolvidos (recomendados para ciclo futuro)

- ID 2: dispersão dos folds de teste LOOCV (mediana/DP, correlação pooled);
- ID 3: coluna comparativa sem cluster na Tabela 5 (Cameron e Miller, 2015);
- ID 4: análise de equivalência (TOST) ou limites de detecção para o
  coeficiente nulo do painel FE.
- ID 12: conferência humana das diretrizes RBEP sobre resumo em espanhol.

## Verificação

- Relatório consolidado: `outputs/review/peer_review_r422.md` (triagem com
  resolução por achado).
- Testes R422 (17): relatório, correções obrigatórias/informativas, PDF sem
  Overfull/Underfull, DOCX consistente (sha256 do MANIFEST).
- Suíte R408–R422: **351 testes passed**.
- LaTeX: 19 páginas, 0 Overfull, 0 Underfull; DOCX regenerado (14 tabelas).
- Doctor: 10/12 pass, 0 failed (warns pré-existentes).

## Lições

- Blind peer review emulado é gate de alto valor imediatamente antes da
  decisão humana de submissão; detectou erro editorial que viajaria no
  envelope (nome do periódico no glossário).
- Texto de glossário em tabela DOCX não aparece em `paragraphs` —
  testes de DOCX devem varrer também as células das tabelas.
- Correções de texto não exigem reanálise; IDs que exigem reanálise ficam
  explicitados como candidatos ao próximo ciclo (R423).
