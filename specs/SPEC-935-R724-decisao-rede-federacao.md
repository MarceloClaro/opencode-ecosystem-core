# SPEC-935-R724 — Decisão titular, rede polímata e federação de escopo próprio

**Status:** `em implementação`
**Ciclo:** R724→R725
**Data:** 2026-10-07
**Base:** R722 (pareceres 8 e 10) + ordem titular `decida, adicione a rede e federe`

## 1. Problema

As minutas `pgmpy` e `prisma` têm inventário, parecer e minuta, mas seguem como
`candidato_a_inspecao` fora da rede. A ordem titular autoriza decidir e federar,
porém a federação R621 de harness não aceita repos externos como skills/agents.
Falta decisão registrada + rede polímata própria + federação de escopo polímata,
sem tocar em `harness_federation`, `opencode.json` ou código de terceiros.

## 2. Objetivo

Módulo `integrations/polymath_federar.py` que, somente com `humano is True` e
`ordem` explícita, aprova as 2 minutas no diretório de intenções original,
registra nodos em `workbench/rede_polimata/nodos.json` (roteáveis pelo
orquestrador, `execution_verified=false, instruction_only=true`) e federa em
`workbench/rede_polimata/federados.json` com `federado_no_escopo_polimata`,
cadeia de hashes e vedação de execução.

## 3. Critérios de aceitação

- [ ] AC1 — `decidir_titular(dir, ordem)` exige `humano is True` e `ordem` com `decida|federe`; aprova só urls com minuta+parecer+readiness pronto; cada decisão com `motivo` do parecer e `responsavel=titular`; demais seguem aguardando.
- [ ] AC2 — `adicionar_rede(dir, rede_dir)` cria nodos só de `aprovada` com `minuta+parecer`; nodo com `agent_id polymath:lab:slug, capabilities do tipo, confidence 0.6, load 0, license, source_path do clone, execution_verified false`.
- [ ] AC3 — `federar(rede_dir)` emite `federados.json` com `federado_no_escopo_polimata=true, escopo=polimata (não harness R621), quando, cadeia{intencao,minuta,parecer,inventario}`; nunca escreve em harness, opencode.json, nem instala/executa.
- [ ] AC4 — Testes herméticos `tests/test_r724_federar.py`: sem humano recusa, sem minuta recusa, rede só de aprovadas, federados com cadeia, grep proíbe `harness_federation, Popen, os.system, pip install`.
- [ ] AC5 — Anti-overclaim: `federado_no_escopo_polimata` nunca afirma qualidade; rótulo `candidato_federado_exige_supervisao`.

## 4. Fora de escopo (declarado)

- Federação R621, instalação, build, execução de testes do lab, decisão das 14 restantes.

## 5. Verificação

- `pytest tests/test_r724_federar.py -q` verde.
- Decisão real no original `/tmp/polymath_intencoes` (2 aprovadas, 14 aguardando) + rede + federados em `workbench/rede_polimata/`.
- `doctor` sem novos falhos.
