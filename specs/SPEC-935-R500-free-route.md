# SPEC-935-R500 — Roteamento Automático Tarefa→Modelo Free (curadoria R499)

**Status**: Em implementação
**Autor**: marceloclaro (orquestrador primário)
**Data**: 2026-09-13
**Pré-requisitos**: R499 (benchmark LLMs free reais + raio-x)

## 1. Objetivo

Tornar o **benchmark real do R499** uma fonte de decisão automática no
`ModelRouter`: tarefas científicas/acadêmicas com `prefer_free=True` devem ser
roteadas para o **melhor modelo free do ranking** (mimo-v2.5-free, score
0.987), com fallback para big-pickle (0.923), e o **big-pickle deve estar
visível** no catálogo de modelos do ecossistema (list_all_models) — era usado
via CLI mas invisível ao roteamento (gap mapeado no R499).

## 2. Implementação

1. `integrations/free_model_catalog.py` (novo):
   - `FREE_BENCHMARK`: lista curada com modelo, score, latência, acurácia,
     acessibilidade (free-ok / saldo / erro).
   - `BEST_FREE_BY_TASK`: map task_type → [modelos em ordem de preferência]
     (academic/math/reasoning → mimo → big-pickle → nemotron; muse spark
     rebaixado por acurácia 0 no R499).
   - CatalogProvider virtual (`list_models()`), para o router enxergar.
2. `integrations/model_router.py` (patch cirúrgico):
   - `list_all_models()` inclui o catálogo free + big-pickle.
   - `route(... prefer_free=True)` consulta o catálogo e retorna o melhor
     modelo por task_type; `reason` documenta a fonte ("curadoria R499").
3. Testes: `tests/test_r500_free_route.py`.

## 3. Critérios de aceitação

1. `route("academic", prefer_free=True)` → model_id `opencode/mimo-v2.5-free`
   com reason contendo "R499".
2. `list_all_models()` contém `opencode/big-pickle` e `muse-spark-1.3-contributor-free`.
3. Fallback determinístico: se mimo ausente do catálogo, rota → big-pickle.
4. Muse Spark nunca é escolhido antes dos corretos (acurácia 0).
5. Regressão: perfis existentes (coding/reasoning) inalterados sem prefer_free.
6. Anti-overclaim: nenhuma alegação de superioridade; reason cita score real.

## 4. Riscos

- Catálogo free pode mudar (saldo/erro): o roteamento usa score + flag de
  acessibilidade; nova falha degrada para o próximo por ordem, sem perda.
- Big-pickle é modelo deste orquestrador: incluí-lo é metadado de curadoria,
  não autopromoção (score medido R499: 0.923, 2º lugar legítimo).