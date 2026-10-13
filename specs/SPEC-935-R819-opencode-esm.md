---
spec_id: SPEC-935-R819
title: Configuração ESM e checagem integral dos plugins e ferramentas OpenCode
component: .opencode/package.json
status: implemented
round_id: R819
test_file: tests/test_r816_opencode_argument_transport.py
---

# SPEC-935-R819 — Módulos OpenCode compiláveis

## Problema

A checagem TypeScript integral retorna TS1470 em deploy-guards.ts:22:
import.meta está presente em um arquivo classificado como CommonJS pelo
NodeNext. A pasta .opencode não declarava o formato ESM de seus módulos.

## Requisitos e aceite

- Declarar o formato ESM na pasta dos plugins e ferramentas locais.
- Preservar o código e a política fail-closed dos guards.
- Incluir plugins e tools na checagem de tipos. `npm run typecheck` deve
  concluir sem erro e ambos os módulos devem carregar no runtime real.
- Reexecutar as provas R816 de entrada literal e ciclo de vida dos processos.
- Registrar separadamente a auditoria de dependências. Ausência de avisos
  no registro npm não constitui uma garantia geral de segurança.

## Evidência

RED: outputs/core-r817/typecheck-red.txt contém TS1470. Logs GREEN, imports
reais e auditoria ficam em outputs/core-r819. Não há publicação ou alteração
do ambiente global de plugins.

GREEN: typecheck integral passou; imports reais de deploy-guards.ts e
core_command.ts passaram em Node. OpenCode reconectou os 16 MCPs. A auditoria
npm da pasta .opencode registrou zero vulnerabilidades conhecidas.

## Complemento SPEC-979 — 11/10/2026

A inclusão do plugin `acesso-aberto-auditoria.ts` revelou TS2322: sua factory
retornava um objeto convertido para `Plugin`, em vez de Hooks. A correção usa
`tool()` e schemas Zod do SDK 1.18.4, sem cast para ocultar incompatibilidade.
`execute` valida o objeto inteiro, canonicaliza o DOI e retorna string JSON.
O schema pode ser publicado em JSON Schema; nenhuma transformação Zod
irrepresentável é usada. A função continua sendo orientação local: rede,
criação de arquivos e execução do pipeline são explicitamente falsas.

Os cinco testes R979 anteriores foram preservados e o gate final aprovou
30 testes, com imports, execução e schemas reais, sem efeitos externos.
Typecheck integral final aprovado; o RED anterior foi preservado em
`outputs/core-r820/typecheck-plugin-red.txt`. Evidências runtime e schema
em `outputs/core-r820/plugin-sdk-*`. A checagem não afirma inferência real
de provedores nem conclusão de fichamentos.
