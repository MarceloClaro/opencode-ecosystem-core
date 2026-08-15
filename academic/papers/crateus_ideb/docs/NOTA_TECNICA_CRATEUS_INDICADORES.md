# Nota Técnica — Diagnóstico de indicadores correlacionados com o IDEB no Sertão de Crateús (foco: Crateús)

**Ciclo R427** — SPEC-935-R427-crateus-diagnostico.md
**Data:** 2026-08-15 · **Autor:** Marcelo Claro Laranjeira

## 1. Pergunta

Dentre os indicadores municipais oficiais disponíveis, **quais se correlacionam mais
(positivamente) e quais menos** com o desempenho escolar (IDEB) nos nove municípios do
Sertão de Crateús — e onde Crateús se posiciona nos indicadores de maior correlação,
para orientar prioridades de política pública?

## 2. Método e dados

- Unidades: 9 municípios da microrregião IBGE 23018 (Censo 2022).
- Desfechos: IDEB 2025 anos iniciais e finais; ganho de IDEB anos iniciais 2007–2025 (INEP).
- Indicadores (Censo 2022, IBGE/SIDRA): alfabetização 15+, água da rede geral, esgoto em
  rede, lixo coletado, banheiro exclusivo, internet domiciliar; mais renda média do
  responsável (2022) e PIB per capita (2021).
- Métrica: correlação de Pearson e Spearman com **bootstrap não paramétrico** (5.000
  reamostragens, seed 42), IC95 percentil e % de reamostragens com o mesmo sinal.
- **Limite de inferência:** n=9 → todos os IC95 são amplos e incluem zero; o resultado é
  um **ranqueamento exploratório de associações**, não inferência confirmatória, e nunca
  causalidade.

## 3. Ranking — indicadores mais e menos correlacionados (média dos três desfechos)

| # | Indicador (família) | r médio | sinal | bootstrap |
|---|---|---|---|---|
| 1 | Banheiro exclusivo (saneamento) | **+0,46** | positivo | 84% |
| 2 | Água da rede geral (saneamento) | **+0,41** | positivo | 86% |
| 3 | Lixo coletado (saneamento) | **+0,31** | positivo | 76% |
| 4 | Esgoto em rede (saneamento) | −0,22 | negativo | 79% |
| 5 | Internet domiciliar (conectividade) | −0,17 | negativo | 78% |
| 6 | Renda do responsável (renda) | −0,16 | negativo | 63% |
| 7 | PIB per capita (renda) | +0,15 | positivo | 63% |
| 8 | Alfabetização 15+ (capital humano) | +0,08 | positivo | 60% |

**Leitura:** na microrregião, os indicadores com **maior associação positiva** com o
desempenho escolar são de **saneamento básico (banheiro, água, lixo)**. Os com **menor
associação** são **renda, PIB per capita e alfabetização adulta** — e esgoto/internet
aparecem com sinal negativo (não são alavancas educacionais nesta escala).

## 4. Perfil de Crateús vs. microrregião

| Indicador | Crateús | Mediana | Melhor | Posição | Gap até o melhor |
|---|---|---|---|---|---|
| Água da rede geral (%) | 78,5 | 72,7 | 91,0 (Novo Oriente) | 4º | **−12,5 p.p. (−13,7%)** |
| Lixo coletado (%) | 80,6 | 64,8 | 85,6 (Nova Russas) | 2º | **−5,0 p.p. (−5,9%)** |
| Banheiro exclusivo (%) | 94,8 | 93,9 | 97,3 (Nova Russas) | 5º | −2,5 p.p. (−2,5%) |
| Esgoto em rede (%) | 48,6 | 16,2 | 48,6 (Crateús) | **1º** | — |
| Internet domiciliar (%) | 83,5 | 79,7 | 83,5 (Crateús) | **1º** | — |
| Alfabetização 15+ (%) | 82,1 | 76,6 | 82,1 (Crateús) | **1º** | — |
| Renda do responsável (R$) | 1.676,70 | 1.172,89 | 1.676,70 (Crateús) | **1º** | — |
| PIB per capita (R$) | 12.661 | 9.854 | 12.661 (Crateús) | **1º** | — |

**Leitura:** Crateús é o município **mais bem posicionado** da microrregião em renda,
PIB, alfabetização adulta, internet e esgoto — mas fica **abaixo do melhor em água
(−12,5 p.p.) e lixo (−5,0 p.p.)**, exatamente nos dois indicadores de saneamento que
mais se associam ao desempenho na região.

## 5. Matriz de prioridade para Crateús (correlação × gap)

| Prioridade | Indicador | r médio | Gap até o melhor | Ação sugerida (exploratória) |
|---|---|---|---|---|
| **1** | Água da rede geral | +0,41 | −12,5 p.p. | Ampliar ligações à rede geral nas zonas sem cobertura (rural) |
| **2** | Lixo coletado | +0,31 | −5,0 p.p. | Universalizar coleta domiciliar (áreas sem serviço) |
| 3 | Banheiro exclusivo | +0,46 | −2,5 p.p. | Consolidar (quase universal); programa de melhorias sanitárias |
| — | Esgoto em rede | −0,22 | já é líder | Não tratar como alavanca educacional direta |

## 6. O que NÃO é alavanca (menor correlação)

- **Renda e PIB per capita**: não apresentam associação positiva com o desempenho nem com
  o ganho na microrregião (consistente com o R426: crescimento educacional não acompanhou
  renda). Esperar crescimento econômico para melhorar o IDEB não encontra suporte nos dados.
- **Alfabetização adulta**: quase nula (variação pequena entre os 9 municípios).
- **Internet**: sinal negativo nesta escala — conectar não substitui a política pedagógica.

## 7. Conclusão operacional para Crateús

Crateús já é líder regional em renda, capital humano adulto e conectividade — portanto a
trajetória educacional **não está estagnada por falta de renda ou infraestrutura básica
mais geral**. Os dois pontos com associação positiva **e** com gap real são **água da rede
geral** e **coleta de lixo** (saneamento), com prioridade para a água. Como o R426 mostrou
que a variação temporal do IDEB não acompanhou renda, recomenda-se combinar:

1. fechar os gaps de saneamento (água, lixo) — associação transversal mais forte;
2. manter e aprofundar as políticas pedagógicas (PAIC, alfabetização na idade certa,
   regime de colaboração) — fator que a literatura do Ceará associa aos ganhos temporais;
3. monitorar indicadores escolares (fluxo, proficiência) — não disponíveis via API nesta
   coleta, indicados para extensão.

## 8. Limitações e extensões

- n=9; IC95 amplos; correlação transversal ≠ causalidade.
- Finanças municipais (FINBRA/SICONFI) e indicadores escolares (Censo Escolar: docentes,
  infraestrutura escolar, fluxo) **indisponíveis via API no momento da coleta** — extensão
  natural: despesa com educação por aluno, % docentes com superior, distorção idade-série.
- Gini municipal 2022 não publicado no SIDRA (apenas 2000/2010).
- Reprodução em todas as microrregiões cearenses daria poder estatístico para inferência
  confirmatória.
