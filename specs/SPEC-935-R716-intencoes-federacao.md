# SPEC-935-R716 — Intenções de federação polímata sem auto-federar

**Status:** `em implementação`
**Ciclo:** R716→R717
**Data:** 2026-10-07
**Base:** R715 (`federacao_proposta.json` 16 propostos/5 retidos + overrides com sha)

## 1. Problema

A proposta R715 decide `proposto|retido`, mas não existe ponte auditável para a
rede do ecossistema: sem registro de intenções pendentes, a decisão humana por
lab se perde e a federação automática se torna tentadora. A federação real de
harness (R621) exige artefato local legível; labs externos nunca são artefatos
federados automaticamente.

## 2. Objetivo

Módulo `integrations/polymath_intencoes.py` que importa `federacao_proposta.json`
como intenções `aguardando_humano`, permite `aprovar|rejeitar` por lab apenas com
`humano=true + motivo + responsável`, emite `intencoes.json` e `decisoes_humanas.jsonl`,
sem escrever em `harness_federation`, sem instalar ou executar.

## 3. Critérios de aceitação

- [ ] AC1 — `importar(proposta_path, destino_dir)` lê proposta R715, importa apenas `proposto`, cria uma intenção por lab com `intencao_id INT-xxxx, url, classe, motivo_proposta, licenca, status=aguardando_humano`; `retido` vira registro informativo, nunca intenção.
- [ ] AC2 — `decidir(intencoes_dir, url, decisao, humano, motivo, responsavel)` fail-closed: `humano is not True` recusa; `decisao` só `aprovada|rejeitada`; URL fora das intenções recusa; decisão grava `decisoes_humanas.jsonl` append com `quando, responsavel, motivo` e atualiza `intencoes.json`; `aprovada` não federa — marca `pronta_para_federacao=false` até rotina R621 com artefato local.
- [ ] AC3 — `resumo(intencoes_dir)` retorna `total, aguardando, aprovadas, rejeitadas, retidas_informativas`; nenhuma escrita colateral.
- [ ] AC4 — Anti-auto-federação: nenhum código escreve em `integrations/harness_federation`, `opencode.json` ou executa `clone/install`; grep do módulo não contém `harness_federation`, `os.system`, `Popen`, `requests`.
- [ ] AC5 — Testes herméticos `tests/test_r716_intencoes.py`: importação de proposta sintética, decisão sem humano recusada, aprovação com humano, rejeição, resumo, retido nunca vira intenção, schema em tmp.
- [ ] AC6 — Anti-overclaim: status só `aguardando_humano|aprovada|rejeitada`; `aprovada` exige `pronta_para_federacao=false + exige_artefato_local=true`; nenhum `federado|verificado|Qualis`.

## 4. Fora de escopo (declarado)

- Federação efetiva, escrita em catálogo, instalação, clone, build, token.

## 5. Verificação

- `pytest tests/test_r716_intencoes.py tests/test_r715_federacao_classes.py -q` verde.
- Importação seca da proposta real `/tmp/polymath_federacao/federacao_proposta.json` para `/tmp/polymath_intencoes` sem rede.
- `doctor` sem novos falhos.
