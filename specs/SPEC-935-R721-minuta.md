# SPEC-935-R721 — Minuta R621 dos prontos sem federar

**Status:** `em implementação`
**Ciclo:** R721→R722
**Data:** 2026-10-07
**Base:** R720 (`relatorio_autonomo.json` 2 prontas: pgmpy 861 arq, prisma 50 arq)

## 1. Problema

O inventário descreve arquivos, mas não propõe o artefato mínimo que a rotina
R621 exigiria: `ecosystem/kind/name/description/source_path` legível com hash,
licença e capacidades do tipo R711. Sem minuta, o titular não visualiza o que
federaria e o trabalho autônomo estaciona antes da decisão.

## 2. Objetivo

Módulo `integrations/polymath_minuta.py` 100% local que lê `relatorio_autonomo.json`
+ clones e emite `minuta_r621.json` com, por pronto, proposta `polymath:spec:third_party:slug`
(`description` das 3 primeiras linhas não vazias do README até 240 chars,
`source_path` ao README do clone, `license` do override/pin, `capabilities` do
tipo R711, `content_sha256` do README). Nada escrito em harness, nada federado.

## 3. Critérios de aceitação

- [ ] AC1 — Só itens `pronto_para_analise_R621`; demais ignorados sem falhar.
- [ ] AC2 — `description` nunca vazia (fallback `uso_polimata` R711); `source_path` existe e é legível; `content_sha256` 64 hex do README.
- [ ] AC3 — `emitir` escreve `minuta_r621.json` com `spec_id, gerador, total, minutas[], rotulo candidato_a_inspecao`.
- [ ] AC4 — Sem rede/subprocesso/escrita fora do destino; grep proíbe `urlopen, subprocess, os.system, Popen, harness_federation`.
- [ ] AC5 — Testes herméticos `tests/test_r721_minuta.py`: clone sintético com README, minuta com schema, fallback sem README, determinismo do hash.
- [ ] AC6 — Anti-overclaim: `proposta_para_federacao`, nunca `federado|verificado`; exige `ratificacao_titular=true`.

## 4. Fora de escopo (declarado)

- Escrita em harness, federação, decisão nova, rede, execução.

## 5. Verificação

- `pytest tests/test_r721_minuta.py -q` verde.
- Minuta real das 2 prontas em `/tmp/polymath_intencoes_piloto/minuta_r621.json`.
- `doctor` sem novos falhos.
