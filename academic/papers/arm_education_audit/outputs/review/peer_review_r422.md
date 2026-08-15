# Blind Peer Review — Manuscrito RBEP (R422)

**Manuscrito:** "Educação terciária e trajetórias de renda: evidência associativa
de painel com validação cruzada agrupada por país (135 economias, 1960–2023)"
**Data do review:** 2026-08-14
**Versão revisada:** R410–R421 (MD canônico, espelhado em LaTeX/PDF e DOCX)
**Método:** três revisores emulados independentes (R1 econometria de painel;
R2 economia da educação; R3 metodologia/rigor de submissão), com verificação
aritmética exaustiva contra os artefatos de proveniência
(`provenance_expanded.json`, `provenance_r418.json`, `provenance_r419.json`,
`provenance_r413.json` e tabelas CSV).

## Veredictos

| Revisor | Veredicto |
|---|---|
| R1 — Econometria de painel | Revisão menor |
| R2 — Economia da educação | Revisão menor |
| R3 — Metodologia e rigor de submissão | Revisão menor |

**Nenhum bloqueio metodológico ou de conteúdo identificado.** A verificação
aritmética confirmou toda a cadeia de números-chave: Δ = 0,604
(IC95% [0,547; 0,665]; p < 0,001; 500 replicações; nenhuma com Δ ≤ 0),
ρ_níveis [0,697; 0,809], ρ_1ªdif [0,118; 0,177], robustez de semente
(42/7/2024/123), caso brasileiro (Tabela 8), decomposição amostral
217 = 135 + 82 (13 sem matrícula, 2 sem PIB, 2 sem ambos, 65 <20 obs),
LOOCV (0,751/0,542), subperíodos, painel FE (0,073; [−0,169; 0,314];
p = 0,555; 106 clusters; n = 1.146) e ML (0,694/0,609).

## Tabela de triagem consolidada e resolução (R422)

| ID | Severidade | Seção | Problema | Recomendação | Resolução |
|---|---|---|---|---|---|
| 1 | Informativa | 4.9; Resumo | "Δ = 0,604 (0,751 − 0,146)": conta com arredondados fecha 0,605 | Mostrar casas exatas ou nota de arredondamento | **Sim** — texto atualizado: "0,7508 − 0,1465 = 0,6043" |
| 2 | Menor | 4.3 / Tabela 3 | Média do ρ de teste (0,542) sem DP/mediana; folds variam −0,953 a 0,994 | Reportar mediana/DP e correlação pooled; reconhecer instabilidade | Não — melhoria metodológica (candidata a R423) |
| 3 | Menor | 4.5 / Tabela 5 | Afirmação sobre IC sem especificação sem cluster | Coluna comparativa sem cluster (Cameron e Miller, 2015) | Não — melhoria metodológica (candidata a R423) |
| 4 | Menor | 4.5 / 5 | IC [−0,169; 0,314] largo; "não discernível" sem equivalência/poder | TOST ou limites de detecção explícitos | Não — melhoria metodológica (candidata a R423) |
| 5 | Informativa | 3.3 vs 4.7 | Promessa de proveniência aponta só para `provenance_expanded.json` | Citar também `channels/provenance_r413.json` | **Sim** — texto 3.3 atualizado nos dois arquivos |
| 6 | Menor | 1 (Introdução) | "Validações cruzadas por país e por tempo" sem validação temporal | Reformular para "validação por país e análises de subperíodos" | **Sim** — frase corrigida (MD + TeX) |
| 7 | Menor | 4.8 | Matrícula bruta sem ressalva demográfica (Argentina 107,1%) | Frase sobre composição etária e medida bruta | **Sim** — frase acrescentada (MD + TeX) |
| 8 | Menor | Tabela 10 | Rótulo "Oriente Médio e Norte da África" omite Afeganistão e Paquistão | Espelhar nomenclatura oficial WDI | **Sim** — rótulo corrigido (MD + TeX) |
| 9 | Menor (obrigatória) | Apêndice A.3 | "RBEP = Revista Brasileira de Estudos de População" (periódico errado) | Corrigir para "Revista Brasileira de Estudos Pedagógicos" | **Sim** — corrigido no MD, TeX, PDF e DOCX |
| 10 | Informativa | 3.1 | Download 13/08 vs verificação API 14/08 | Uniformizar ou explicitar os dois eventos | **Sim** — texto 3.1 atualizado nos dois arquivos |
| 11 | Menor | Manuscrito (global) | Ausência de seções formais (conflito, financiamento, dados/código) | Adicionar blocos formais antes do upload | **Sim** — seção "Declarações" adicionada (MD + TeX) |
| 12 | Informativa | Resumo | Resumo em espanhol: conferir exigência nas diretrizes RBEP | Verificar instrução aos autores vigente | Aplicável — ação editorial humana |

## Resumo das resoluções

- **Corrigidos no ciclo R422 (8 achados)**: IDs 1, 5, 6, 7, 8, 9, 10, 11 —
  todos refletidos no MD canônico, no TeX, no PDF recompilado (19 páginas,
  0 Overfull/Underfull) e no DOCX regenerado.
- **Não resolvidos (3, recomendados para R423)**: IDs 2, 3, 4 — exigem
  reanálise empírica (métricas de dispersão da LOOCV; especificação sem
  cluster; análise de equivalência/limites de detecção).
- **Ação editorial humana (1)**: ID 12 — conferência das diretrizes vigentes
  da RBEP quanto ao resumo em espanhol.

## Recomendação geral

O manuscrito é cientificamente sólido: nenhum bloqueio metodológico, nenhuma
alegação sem suporte além do overclaim corrigido na Introdução, e consistência
numérica exemplar entre texto, tabelas e artefatos de proveniência. Os
achados críticos apontados foram corrigidos neste ciclo. As melhorias
metodológicas (IDs 2–4) são recomendadas, não bloqueantes. A decisão final
de submissão permanece exclusivamente com o Editor-Chefe humano; este
relatório **não** constitui aprovação, validação ou atestado de prontidão
para publicação.
