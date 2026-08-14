# Ciclo R413 — Canais associativos da educação terciária

- **Data**: 2026-08-13
- **Spec**: `specs/SPEC-935-R413-canais-associativos.md`
- **Dependência**: R412 (painel expandido de 135 países, controles WGI, erros clusterizados)
- **Score**: 8.6/10
- **Suíte**: R408–R413 = 228/228 GREEN (R413: 26/26)

## Contexto

O usuário pediu melhorias que cubram gaps reais e relevantes com resultados
auditáveis e validados. A varredura no painel expandido (R412) + cruzamento
com a literatura identificaram combinações que a literatura trata
separadamente mas raramente junta: educação terciária × saúde × governança ×
inovação.

## Entregas

1. **Spec** `SPEC-935-R413-canais-associativos.md` (SDD).
2. **Script** `analyze_channels.py`: matriz de correlações parciais (ctrl PIB);
   análise em etapas do par matrícula×PIB; canais (saúde/desigualdade/inovação)
   com painel FE clusterizado por país; interações exploratórias matrícula×WGI
   e matrícula×P&D; cluster bootstrap por país (500×, seed 42) para ICs;
   LOOCV por país (135 folds).
3. **Proveniência fechada**: `outputs/channels/provenance_r413.json` (com
   SHA-256 do painel) + 4 tabelas CSV + folds LOOCV.
4. **Nota de pesquisa** `NOTA_CANAIS_ASSOCIATIVOS.md` (resumo trilíngue,
   anti-overclaim, referências ABNT) + LaTeX + PDF compilado.
5. **Testes** `test_r413_canais_associativos.py` — 26 testes, TDD RED→GREEN.

## Resultados principais

| Métrica | Valor | IC bootstrap 95% |
|---|---|---|
| ρ matrícula×PIB (inicial) | 0,701 | [0,642; 0,756] (n=4374) |
| ρ matrícula×PIB (+WGI) | 0,653 | [0,568; 0,738] |
| ρ matrícula×PIB (+estrutura) | 0,358 | [0,205; 0,528] |
| ρ matrícula×PIB (+saúde) | 0,105 | [−0,090; 0,288] |
| Parcial matrícula×saúde | 0,684 | [0,639; 0,728] (n=4374) |
| Parcial matrícula×Gini | −0,184 | (n=1475) |
| Parcial P&D×alta tecnologia | 0,250 | (n=1148) |
| Parcial gasto educ.×WGI_CC | 0,341 | (n=2441) |

Canais FE cluster (defasagem 5 anos): saúde 0,535 (p=0,186; 106 clusters);
desigualdade −0,104 (p=0,940; 77); inovação 0,836 (p=0,529; 77).

Interações exploratórias: matrícula×WGI 0,054 (p=0,005); matrícula×P&D
−0,003 (p=0,668). Ambas marcadas `exploratorio: true`.

## Achado central

A associação matrícula terciária × PIB per capita cai de 0,701 para 0,105 ao
adicionar a expectativa de vida como controle — a associação em níveis é
sensível ao canal saúde. Reportado em linguagem estritamente associativa.

## Lições registradas

1. Gate de texto por substring é impreciso ("determinantes" contém "determina");
   refinar para word-boundary por forma flexionada.
2. Números com separador de milhar no resumo não são recuperáveis de int na
   provenance; usar sem separador.
3. Controles que colidem com a variável de interesse geram colunas duplicadas
   em pandas; filtrar.
4. Resultados negativos (p altos no FE) reportados integralmente — valor
   científico em mostrar onde a associação não se confirma.

## Pendência humana

- Nota é candidata a **apêndice** do artigo RBEP ou **segundo artigo**.
- Submissão efetiva à RBEP continua ação humana.
