# SPEC-935-R717 — Lote piloto de decisões humanas com trilha para R621

**Status:** `em implementação`
**Ciclo:** R717→R718
**Data:** 2026-10-07
**Base:** R716 (`/tmp/polymath_intencoes` 16 aguardando + 5 retidas)

## 1. Problema

Dezesseis intenções aguardam sem exemplo executado de decisão com motivo e
responsável. Decidir as 16 de uma vez fabricaria aprovação sem exame por lab.
Falta lote piloto mínimo que demonstre `aprovar|rejeitar` com trilha completa
para a rotina R621, mantendo as demais aguardando e exigindo ratificação do
titular antes de qualquer federação.

## 2. Objetivo

Módulo `integrations/polymath_lote.py` com `decidir_lote(dir, itens, humano,
responsavel)` que aplica `polymath_intencoes.decidir` em sequência, aborta
na primeira falha (atomicidade por lote), emite `lote_piloto.json` com resumo
e preserva `decisoes_humanas.jsonl`. Piloto 3+1: aprovar `pgmpy, sympy, prisma`
com motivos técnicos e rejeitar `reasonkit-core` por licença a confirmar,
mantendo 12 aguardando como exemplo ratificável.

## 3. Critérios de aceitação

- [ ] AC1 — `decidir_lote` fail-closed sem `humano is True`; cada item exige `url, decisao aprovada|rejeitada, motivo` não vazios; URL sem intenção ou já decidida aborta o lote com `ValueError` sem aplicar restante.
- [ ] AC2 — Emite `lote_piloto.json` com `spec_id, gerador, quando, responsavel, piloto=true, aplicadas[], resumo` após sucesso; falha não escreve lote.
- [ ] AC3 — Decisões piloto documentadas: pgmpy núcleo causal fresco MIT; sympy formal BSD com override; prisma síntese fresca MIT; reasonkit-core rejeitado por licença a confirmar e origem menos auditada.
- [ ] AC4 — Nenhuma escrita fora do diretório de intenções; nenhum `federado|verificado|Qualis`; `aprovada` mantém `pronta_para_federacao=false`.
- [ ] AC5 — Testes herméticos `tests/test_r717_lote_piloto.py`: lote sintético 2+1, falha aborta restante, sem humano recusa, schema do lote em tmp.
- [ ] AC6 — Skill registra piloto como exemplo ratificável, não como aprovação definitiva.

## 4. Fora de escopo (declarado)

- Federação, instalação, clone, decisão das 12 restantes sem exame individual.

## 5. Verificação

- `pytest tests/test_r717_lote_piloto.py tests/test_r716_intencoes.py -q` verde.
- Piloto real em cópia `/tmp/polymath_intencoes_piloto` (original preservado) com 3+1 e relatório.
- `doctor` sem novos falhos.
