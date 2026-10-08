# SPEC-935-R723 — Dossiê consolidado do ciclo polímata sem decidir

**Status:** `em implementação`
**Ciclo:** R723→R724
**Data:** 2026-10-07
**Base:** R711→R722 (curadoria, pinagem, federação, intenções, lote, readiness, inventário, minuta, pareceres)

## 1. Problema

As evidências estão dispersas em 7 JSONs, 12 specs e 20+ testes: o titular não
ratifica em leitura única. Falta dossiê com cadeia de custódia (arquivo+hash),
contagens e pendências, sem nova decisão e sem reexecução de rede.

## 2. Objetivo

Módulo `integrations/polymath_dossie.py` 100% local com `emitir(piloto_dir,
destino)` que coleta `intencoes, lote_piloto, readiness, relatorio_autonomo,
minuta_r621, pareceres, decisoes_humanas` com `sha256` por arquivo, mais lista
de specs R711→R723 e resumo (16 intenções, 3+1 piloto, 2 prontas, 2 minutas,
2 pareceres), em `dossie_final.json`. Nada decidido, nada federado.

## 3. Critérios de aceitação

- [ ] AC1 — Coleta os 7 artefatos quando presentes; ausente vira `ausente=true` sem falhar.
- [ ] AC2 — Cada presente carrega `bytes, sha256, resumo{total/aprovadas/prontas}` extraído sem executar.
- [ ] AC3 — `emitir` escreve `dossie_final.json` com `spec_id, gerador, cadeia, artefatos[], pendencias_titular[]`.
- [ ] AC4 — Sem rede/subprocesso/escrita fora do destino; grep proíbe `urlopen, subprocess, os.system, Popen, harness_federation`.
- [ ] AC5 — Testes herméticos `tests/test_r723_dossie.py`: dossiê sintético com schema, ausente tolerado, hash 64.
- [ ] AC6 — Anti-decisão: contém `ratificacao_titular_pendente=true`; nunca `federado|verificado|aprovado_em_lote`.

## 4. Fora de escopo (declarado)

- Decisão, federação, rede, clone novo.

## 5. Verificação

- `pytest tests/test_r723_dossie.py -q` verde.
- Dossiê real em `/tmp/polymath_intencoes_piloto/dossie_final.json`.
- `doctor` sem novos falhos.
