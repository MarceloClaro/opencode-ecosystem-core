# evo-58 — R427: Diagnóstico de indicadores correlacionados com o IDEB (foco Crateús)

## Objetivo

Responder, com dados oficiais, **quais indicadores municipais mais e menos se
correlacionam** com o desempenho escolar na microrregião do Sertão de Cratéus (9
municípios) e onde Crateús se posiciona — para orientar prioridades de política
pública ("sair da estagnação") com evidência exploratória e anti-overclaim.

## Mudanças

1. `specs/SPEC-935-R427-crateus-diagnostico.md` — RQ, H1/H2/H3, fontes oficiais,
   método (Pearson+Spearman com bootstrap, ranking, perfil, matriz prioridade),
   critérios de aceitação e anti-overclaim.
2. `scripts/baixar_indicadores.py` — coleta via IBGE SIDRA v3 (Censo 2022):
   alfabetização 15+ (9543), água rede geral (6803), esgoto rede (6805), lixo
   coletado (6892), internet (9936), banheiro exclusivo (6806); 9 municípios;
   `data/processed/indicadores_sidra.json` + `manifest_sidra.json`.
3. `scripts/analise_indicadores_crateus.py` — fusão com R426 (IDEB 2025 AI/AF,
   ganho AI, renda, PIB); correlações Pearson e Spearman com bootstrap não
   paramétrico (seed 42, 5.000 reamostragens, IC95 percentil, estabilidade de
   sinal); ranking agregado; perfil de Crateús; matriz prioridade
   (correlação × gap até o melhor); `resultados_r427.json` + `provenance_r427.json`.
4. `outputs/figuras_r427/` — heatmap de correlações + 3 scatters top (Crateús
   destacado em vermelho).
5. `docs/NOTA_TECNICA_CRATEUS_INDICADORES.md` — ranking top/bottom, perfil de
   Crateús, matriz de prioridade e recomendações, com limites explícitos.
6. `tests/test_r427_crateus_diagnostico.py` — 16 testes.

## Resultados (resumo)

- **Mais correlacionados (positivo):** banheiro exclusivo (r=+0,46), água da rede
  geral (r=+0,41), lixo coletado (r=+0,31) — família **saneamento básico**.
- **Menos correlacionados:** renda do responsável (r=−0,16), PIB per capita
  (r=+0,15), alfabetização adulta (r=+0,08); esgoto (r=−0,22) e internet (r=−0,17)
  com sinal negativo na escala.
- **Perfil de Crateús:** líder da micro em renda, PIB, alfabetização, internet e
  esgoto; **gap de −12,5 p.p. em água da rede geral (78,5% vs. 91,0% de Novo
  Oriente)** e −5,0 p.p. em lixo coletado.
- **Matriz prioridade:** 1) água da rede geral; 2) lixo coletado; 3) banheiro
  (consolidar). Renda/PIB não são alavancas (reforça R426).

## Verificação

- Suíte R427: 16 passed; subset R423+R425+R426+R427: **62 passed**.
- Limitações registradas: n=9 (IC95 amplos, incluem zero; ranqueamento exploratório);
  FINBRA/SICONFI e Censo Escolar (docentes, fluxo) indisponíveis via API no momento;
  Gini municipal 2022 não publicado no SIDRA.

## Lições

- A API SIDRA v3: `/variaveis` pode retornar 500; usar `/metadados` para descobrir
  variáveis/classificações e consultar dados com `localidades=N6[...]`.
- FINBRA/SICONFI via `apidatalake.tesouro.gov.br` está indisponível (404/0 items) —
  registrar como limitação, não bloquear a análise.
- Com n=9, o ranking exploratório (sinal + estabilidade de bootstrap) é mais
  informativo que significância pontual; declarar sempre.
- Separar "correlação com IDEB em níveis" (saneamento) de "alavanca de política"
  (requereria painel/experimento) evita overclaim.
