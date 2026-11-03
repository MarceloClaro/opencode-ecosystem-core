---
spec_id: SPEC-935-R1004
title: Porte dos plugins locais para a API de plugins do OpenCode V2
component: .opencode/plugins
status: implemented
test_file: tests/test_r1004_opencode_v2_plugins.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    contrato:
      - "tests/test_r1004_opencode_v2_plugins.py::test_cada_plugin_exporta_definicao_v2"
      - "tests/test_r1004_opencode_v2_plugins.py::test_plugins_nao_usam_api_v1"
      - "tests/test_r1004_opencode_v2_plugins.py::test_dependencia_v2_declarada"
    acesso:
      - "tests/test_r1004_opencode_v2_plugins.py::test_acesso_registra_ferramenta_com_json_schema"
      - "tests/test_r1004_opencode_v2_plugins.py::test_acesso_orienta_doi_valido"
      - "tests/test_r1004_opencode_v2_plugins.py::test_acesso_recusa_doi_invalido"
      - "tests/test_r1004_opencode_v2_plugins.py::test_acesso_bloqueia_fonte_nao_autorizada"
    deploy:
      - "tests/test_r1004_opencode_v2_plugins.py::test_deploy_registra_hook_execute_before"
      - "tests/test_r1004_opencode_v2_plugins.py::test_deploy_nega_write_html_com_bug_r580"
      - "tests/test_r1004_opencode_v2_plugins.py::test_deploy_aprova_write_html_limpo"
      - "tests/test_r1004_opencode_v2_plugins.py::test_deploy_le_campos_v1_e_v2"
    litert:
      - "tests/test_r1004_opencode_v2_plugins.py::test_litert_registra_provider_sem_duplicar"
      - "tests/test_r1004_opencode_v2_plugins.py::test_litert_preserva_modelos_obrigatorios"
---

# SPEC-935-R1004 — Porte dos plugins locais para a API de plugins do OpenCode V2

**Status:** Implementado (RED → GREEN)
**Versão:** 1.0.0
**Data:** 2026-11-01
**Agente:** marceloclaro (Orquestrador Central Metacognitivo)

## 1. Contexto e problema

O runtime instalado é `@opencode/cli@2.2.5`. A V2 substituiu a API de plugins:
o carregador valida o export default contra `{ id, effect }` ou `{ id, setup }`
e **não executa implementações V1**. Os três plugins locais exportavam funções
(V1) e foram rejeitados no carregamento:

| Plugin | ref do log | consequência |
|---|---|---|
| `acesso-aberto-auditoria.ts` | `err_78be5241` | ferramenta de orientação ausente |
| `deploy-guards.ts` | `err_daad7223` | gate fail-closed de deploy inativo |
| `litert-lm-provider.ts` | `err_d37a68be` | bootstrap do supervisor LiteRT-LM não dispara |

O `typecheck` e os testes R979/R582/R210 passavam porque validavam o contrato V1.

## 2. Objetivo

Portar os três plugins para a API V2 preservando comportamento observável,
e substituir os testes que certificavam o contrato antigo por testes que
exercitam o contrato que o host realmente impõe.

## 3. Não-objetivos

- Migrar `.opencode/tools/core_command.ts` (fora do escopo desta spec).
- Alterar `opencode.json` ou o servidor LiteRT-LM.
- Publicar pacote npm; os plugins continuam locais.

## 4. Requisitos

- R1. Cada arquivo em `.opencode/plugins/*.ts` deve exportar por padrão um
  objeto com `id: string` e `setup: (ctx) => Promise<Cleanup|void> | Cleanup | void`.
- R2. Nenhum plugin importa `@opencode-ai/plugin` (SDK V1) nem retorna mapa
  `tool`/`provider`/`"tool.execute.before"`.
- R3. `@opencode/plugin@2.2.5` declarado em `.opencode/package.json`.
- R4. `deploy-guards` registra `ctx.tool.hook("execute.before", …)`, aceita
  `path` (V2) e `filePath` (V1), e reconhece `shell` e `bash`.
- R5. `acesso-aberto-auditoria` registra a ferramenta via `ctx.tool.transform`
  com JSON Schema; validação semântica de DOI e bloqueio de fonte ocorrem em
  `execute` (JSON Schema não expressa `refine`).
- R6. `litert-lm-provider` registra o provider de forma idempotente: não
  duplica provider/modelos já declarados em `opencode.json`, e dispara o
  bootstrap do supervisor uma única vez no `setup`.
- R7. Os testes R979, R582 e R210 passam a exercitar o contrato V2.

## 5. Critérios de aceitação

| ID | Critério | Verificação |
|---|---|---|
| CA1 | Os três plugins exportam `{id, setup}` | `test_cada_plugin_exporta_definicao_v2` |
| CA2 | Nenhum vestígio da API V1 nos plugins | `test_plugins_nao_usam_api_v1` |
| CA3 | Dependência V2 declarada | `test_dependencia_v2_declarada` |
| CA4 | Ferramenta de acesso aberto registrada com JSON Schema | `test_acesso_registra_ferramenta_com_json_schema` |
| CA5 | Orientação canônica para DOI válido | `test_acesso_orienta_doi_valido` |
| CA6 | DOI inválido recusado antes de qualquer rede | `test_acesso_recusa_doi_invalido` |
| CA7 | Fonte Sci-Hub bloqueada | `test_acesso_bloqueia_fonte_nao_autorizada` |
| CA8 | Guard de deploy registra `execute.before` | `test_deploy_registra_hook_execute_before` |
| CA9 | Bug R580 negado; HTML limpo aprovado | `test_deploy_nega_write_html_com_bug_r580`, `test_deploy_aprova_write_html_limpo` |
| CA10 | Guard aceita nomes de campo V1 e V2 | `test_deploy_le_campos_v1_e_v2` |
| CA11 | Provider LiteRT-LM idempotente | `test_litert_registra_provider_sem_duplicar` |
| CA12 | Os quatro modelos obrigatórios preservados | `test_litert_preserva_modelos_obrigatorios` |

## 6. Evidência de carga real

Além dos testes, o aceite exige log do servidor sem `failed to load plugin`
para os três alvos após o reload, com `loading plugin` presente.

## 7. Limites

O porte não prova que o host executará cada hook em produção; prova que o
módulo satisfaz o schema do carregador e que os callbacks registrados têm o
comportamento esperado quando invocados com o evento documentado.
