# SPEC-935-R718 — Readiness R621 do piloto sem federar

**Status:** `em implementação`
**Ciclo:** R718→R719
**Data:** 2026-10-07
**Base:** R717 (piloto 3 aprovadas + 1 rejeitada + 12 aguardando em cópia)

## 1. Problema

As 3 intenções aprovadas no piloto não estão prontas para a federação R621,
que exige artefato local legível com hash e origem. Sem diagnóstico explícito
do que falta por lab (intenção, pin, licença, artefato local), o operador não
sabe o próximo passo físico e a tentação de federar URL remota cresce.

## 2. Objetivo

Módulo `integrations/polymath_readiness.py` com `avaliar(dir_intencoes, pins,
clones_base)` que cruza intenção aprovada + pin federável + licença + presença
de clone `org__repo` com `.git/HEAD` legível, emitindo `readiness.json` com
`pronto_para_R621: true|false + pendencias[]` por lab, sem clonar, instalar ou
escrever em harness.

## 3. Critérios de aceitação

- [ ] AC1 — Avalia apenas `aprovada`; `aguardando|rejeitada` viram `avaliado=false, motivo` sem falhar o lote.
- [ ] AC2 — `pronto_para_R621=true` sse intenção aprovada + pin federável + licença (viva ou override) + clone presente com HEAD; qualquer ausência lista `pendencias[]` explícitas.
- [ ] AC3 — `emitir(dir, relatorio)` escreve `readiness.json` com `spec_id, gerador, total_avaliadas, prontas, pendentes`.
- [ ] AC4 — Sem rede, sem subprocesso, sem escrita fora do diretório; grep proíbe `harness_federation, urlopen, Popen, os.system`.
- [ ] AC5 — Testes herméticos `tests/test_r718_readiness.py`: aprovada completa pronta; sem clone pendente; sem pin pendente; aguardando não avaliada; schema em tmp.
- [ ] AC6 — Anti-overclaim: `pronto_para_R621` nunca afirma `federado|verificado`; rótulo `candidato_a_inspecao` preservado.

## 4. Fora de escopo (declarado)

- Clone, federação, decisão das 12 restantes.

## 5. Verificação

- `pytest tests/test_r718_readiness.py tests/test_r717_lote_piloto.py -q` verde.
- Readiness da cópia piloto com `clones_base=/tmp/vazio`, relatando 0 prontas com pendências.
- `doctor` sem novos falhos.
