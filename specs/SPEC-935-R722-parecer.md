# SPEC-935-R722 — Parecer técnico das minutas sem decidir

**Status:** `em implementação`
**Ciclo:** R722→R723
**Data:** 2026-10-07
**Base:** R721 (`minuta_r621.json` 2 propostas: pgmpy, prisma)

## 1. Problema

A minuta propõe artefatos, mas o titular não tem parecer técnico local para
ratificar: maturidade da documentação, sinais de manutenção por arquivos,
riscos de licença/escopo e pendências antes de qualquer federação. Parecer
precisa derivar só de leitura local, sem executar código e sem decidir.

## 2. Objetivo

Módulo `integrations/polymath_parecer.py` 100% local com `parecer(url, clone,
minuta, inventario)` que pontua maturidade 0–10 por marcos (README, LICENSE,
pyproject/setup, tests, docs, examples, CITATION) e emite `recomendacao_tecnica`
(`ratificar_com_ressalvas|aguardar_evidencia|nao_ratificar`) como opinião,
mais `emitir_pareceres` em `pareceres.json`. Decisão permanece humana.

## 3. Critérios de aceitação

- [ ] AC1 — Maturidade determinística: +2 README, +2 LICENSE, +2 tests/, +1 pyproject/setup, +1 docs, +1 examples, +1 CITATION, teto 10; sem README zera descrição e recomenda `aguardar_evidencia`.
- [ ] AC2 — Riscos declarados: licença ausente, sem tests, sem docs, README < 200 chars, total_arquivos < 10 ou > 5000; cada risco vira pendência de ratificação.
- [ ] AC3 — `emitir_pareceres` lê minuta+inventário+clones e escreve `pareceres.json` com `spec_id, gerador, total, pareceres[]`.
- [ ] AC4 — Sem rede/subprocesso/escrita fora do destino; grep proíbe `urlopen, subprocess, os.system, Popen, harness_federation`.
- [ ] AC5 — Testes herméticos `tests/test_r722_parecer.py`: maduro recomenda ratificar_com_ressalvas, mínimo recomenda aguardar, schema em tmp.
- [ ] AC6 — Anti-decisão: parecer nunca contém `aprovada|federado|verificado`; contém `opiniao_tecnica, ratificacao_titular_pendente=true`.

## 4. Fora de escopo (declarado)

- Decisão, federação, rede, execução, clone novo.

## 5. Verificação

- `pytest tests/test_r722_parecer.py -q` verde.
- Pareceres reais das 2 minutas em `/tmp/polymath_intencoes_piloto/pareceres.json`.
- `doctor` sem novos falhos.
