# RELATÓRIO 2ª REVISÃO + SCANNERS — V4 FINAL
**Data:** 9 out. 2026
**Arquivo revisado:** `Artigo_revisado_inclusao_educacao_infantil_VERSAO_BANCA_V3_SUBSTITUTOS_DOI.md`
**Arquivo entregue:** `Artigo_revisado_inclusao_educacao_infantil_VERSAO_BANCA_V4_FINAL.md`
**Veredito:** APROVADO PARA BANCA, com 1 pendência da autora (afiliação/ORCID).

## 1. Scanners passados nesta rodada (V3 → V4)

| Scanner | Resultado | Leitura |
|---|---|---|
| `auditar_forca_alegacao` (9 frases, corpo + substitutos) | 1 achado, nível 5 `eficácia` em "sem pretensão de mensurar causalmente eficácia" | **Falso-positivo: é mitigador, não claim.** Frases novas `Mendes (2006)...` e `Faria e Camargo (2025)...`: 0 achados. Sem overclaim. |
| `scientific_reasoning_scan` | SRI 10, falsificabilidade 25, metodologia 0, 0 falácias, `low_rigor` | Esperado para revisão narrativa + documental. Não indica erro; indica desenho sem controle/amostra. Mitigado com limites explícitos, dispensa CEP 510/2016 e agenda empírica. |
| `super_rigor_audit` | EXS 30, `requires_refinement`, mesmos subscores, 0 falácias | Idem. Nenhuma correção causal a fazer; refinamento = transparência, já aplicada (Quadro com Nota, PRISMA declarado ausente). |
| Verificação física V4 | 0 escapes `\`, 0 tabs, 0 `CONFIRMAR/NÃO VERIFICADA`, 7 DOIs | Regressões da V3 (escapes Markdown, mailto, tabs, `2008\)`, tabela `:----`) eliminadas. |

Scanners literários (`literary_scanner_suite` 12.39 insuficiente / voz 51.25 consistente; `research_suite` 5.0 insuficiente) não repetidos: instrumentos para ficção/crítica literária, inaplicáveis a artigo educacional. Único sinal útil já incorporado (riqueza lexical e ritmo consistentes).

## 2. O que foi corrigido na V4 (revisão nova, item a item)

1. **Cabeçalho restaurado:** afiliação/ORCID `¹ [INFORMAR...]` recolocado (havia sumido na V3) + e-mail em texto puro (removido link mailto).
2. **Resumo/Abstract alinhados no presente:** `Adota-se / It adopts` (V3 oscilava para `Adotou-se`). Palavras-chave inalteradas.
3. **Escape crítico:** `(BRASIL, 2008\)` → `(BRASIL, 2008)`.
4. **Tabs e quebras:** removidos `\t` antes de "Essas dimensões..." e "Em conjunto...", removidos espaços duplos de fim de linha, tabela normalizada `|---|---|`.
5. **Títulos padronizados:** `## Resumo`, `## 1 Introdução` (sem `**` duplo no heading).
6. **Referências reescritas em ABNT limpa:** sem `\.`, sem `[https\://...](...)`, sem `\_`, sem `\`. Formato `Disponível em: https://... Acesso em: 9 out. 2026.` + `DOI: https://doi.org/...`. Títulos de periódicos sem negrito espúrio extra, apenas o padrão já adotado para monografias; artigos com periódico em texto corrido + dados completos (local, v., n., p., data).
7. **Consistência mantida:** Mendes (2006), Faria e Camargo (2025), Machado e Martins (2019), Carvalho e Schmidt (2021), Santos e Almeida (2017), Vitta et al. (2010), Pletsch (2009) citados no corpo = referenciados; 8 BRASIL com URL oficial.
8. **Quadro 1:** Fonte + Nota mantidas; texto pós-quadro sem tab.

## 3. Estado DOI final (todos verificados em Crossref neste ciclo)

- 7/7 artigos com DOI: Carvalho 2021, Faria 2025, Machado 2019, Mendes 2006, Pletsch 2009, Santos 2017, Vitta 2010.
- 8/8 normas sem DOI por natureza, com URL + acesso (NBR 6023).
- Zero colchetes. Nenhuma referência inventada.

## 4. Pendência única da autora

Preencher nota `¹` (afiliação, cidade/UF, ORCID, financiamento se houver) e aplicar modelo do programa (margens, fonte, 1,5, paginação). Nada mais bloqueia a impressão.

## 5. Reflexão

Regressão da V3 veio de edição incremental com escapes Markdown do editor. Lição: após cada `edit_file`, rodar `grep escapes/tabs/CONFIRMAR/DOI` como gate (feito na V4). Scanners quantitativos não substituem leitura normativa; seu melhor uso aqui foi anti-overclaim (aprovado) + confirmação de ausência de falácias.
