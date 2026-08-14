# Evo-46 — R412: Expansão da pesquisa para eliminar limitações reais e relevantes

## Contexto

O usuário solicitou, após o R411 (correção da numeração da Tabela 2 no
LaTeX/PDF): "melhore a pesquisa buscando eliminar as limitações reais e
relevantes". O artigo (R409–R411) usava apenas **7 países** (selecionados
por conveniência), sem controles institucionais, sem erros padrão ajustados
à correlação serial e com cobertura parcial.

## O que foi feito (eliminação das limitações)

| Limitação (R409) | Estratégia R412 | Resultado |
|---|---|---|
| (i) 7 países | Painel expandido com critério transparente (≥ 20 obs não nulas de matrícula e PIB; exclui agregados) | **135 países**, 8.640 obs país-ano |
| (ii) cobertura parcial | Painel maior + reporte de cobertura por variável | cobertura documentada na provenance |
| (iii) sem controles | **WGI** (6 dimensões de governança) + estrutura econômica (manufatura, alta tecnologia, vida, investimento) | controles no painel FE |
| (iv) erros sem ajuste | **Cluster por país** (statsmodels `cov_type='cluster'`) | 106 clusters |
| (v) caráter associativo | Declarado com rigor; defasagem de 5 anos | mantém (inevitável) |

## Principais achados (mudança substantiva)

- ρ níveis (matrícula × log PIB): **0,751** (n = 4374) — forte, mas menor
  que 0,934 dos 7 países; reflete diferenças entre países.
- ρ primeiras diferenças: **0,146** (n = 4373).
- LOOCV: média treino 0,751 (DP 0,003); média teste **0,542**.
- Painel FE país+ano+controles WGI: coef log-PIB lag5 **0,073**
  (IC95% −0,169 a 0,314; p = 0,555; 106 clusters) → **não significativo**:
  com controles institucionais e erros clusterizados, a associação dentro
  do país não é discernível. Achado negativo reportado com honestidade.
- ML: AUC linha 0,694 vs agrupado por país **0,609** — fraca transferência.

## Entregáveis

- `specs/SPEC-935-R412-expansao-pesquisa.md`
- `tests/test_r412_expansao_pesquisa.py` (18 falhas RED → GREEN)
- `scripts/download_expanded_data.py` + `data/raw_expandido/` (18 arquivos,
  manifest com SHA-256)
- `scripts/analyze_expanded.py` + `data/processed/panel_wdi_expandido_1960_2023.csv`
- `outputs/expanded/` (6 tabelas + provenance_expanded.json + folds)
- `ARTIGO_RBEP_SUBMISSAO.md`, `latex/ARTIGO_RBEP_SUBMISSAO.tex/.pdf`,
  `CARTA_AO_EDITOR.md` atualizados
- testes R410/R411 atualizados para a proveniência expandida (documentado)

## Lições registradas

1. WGI não está no source principal do WDI: IDs usam prefixo `GOV_WGI_`
   (source 3) e o endpoint responde em `country/all/indicator/GOV_WGI_*`.
2. Agregados regionais (AFE, ARB…) têm ISO3 de 3 letras: filtrar pela lista
   oficial de países baixada da API.
3. Erros homocedásticos inflavam a significância: com cluster por país, o
   coeficiente FE deixa de ser significativo — lição metodológica central.
4. Expandir amostra muda números do manuscrito: atualizar testes R410/R411
   junto, preservando R408/R409 como auditoria histórica.
5. Sinal Unicode − (U+2212) quebra parsing de float em testes: tratar.

## Estado

- Suíte R408–R412: **202 testes verdes**.
- Score do ciclo: 8.5/10.
