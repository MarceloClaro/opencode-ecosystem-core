# SPEC-979 — Agente + Skill + Plugin + MCP do Acesso Aberto com Auditoria Obrigatória

```yaml
spec_id: SPEC-979
title: Expor auditoria SPEC-977/978 e orientação explícita por plugin
status: green
component: agents/catalog/54_agente_acesso_aberto_auditoria_fichamento.md + .opencode/skills/acesso-aberto-auditoria/SKILL.md + .opencode/plugins/acesso-aberto-auditoria.ts + integrations/acesso_aberto_auditoria_mcp.py
test_file: tests/test_r979_agente_skill_plugin_mcp.py
validation_scope: local_runtime
```

## Contexto

SPEC-977 (gate OA) e SPEC-978 (pasta de auditoria + fichamento ABNT) estão verdes, mas acessíveis só via Python direto. O usuário exige os mesmos contratos como superfícies canônicas do ecossistema: agente, skill, plugin e MCP.

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-979.1 | Agente catalogado | `agents/catalog/54_agente_acesso_aberto_auditoria_fichamento.md` com frontmatter `name, description, version, tags, type, category` e seções Missão/Entradas/Saídas/Workflow/Nunca Faça/Critérios/Handoff; proíbe Sci-Hub e exige pasta de auditoria por DOI |
| R-979.2 | Skill invocável pelo orquestrador | `.opencode/skills/acesso-aberto-auditoria/SKILL.md` com `disable-model-invocation: true`, pipeline em 5 passos e exemplo via orquestrador; leitura do SKILL.md executa no contexto atual sem subagente por nome |
| R-979.3 | Plugin OpenCode de orientação | `.opencode/plugins/acesso-aberto-auditoria.ts` exporta factory `Plugin` que retorna Hooks com `tool()` do SDK real; schemas Zod admitem publicação em JSON Schema, entrada inteira é validada também na execute direta, e a saída é string JSON; sem rede nem escrita |
| R-979.4 | MCP FastMCP | `integrations/acesso_aberto_auditoria_mcp.py` expõe `mcp = FastMCP("acesso-aberto-auditoria")` com tools `resolver_doi`, `verificar_oa`, `criar_pasta_auditoria`, `adicionar_recorte`, `auditar_pasta`; cada tool valida DOI, bloqueia sci-hub e retorna proveniência + hash |
| R-979.5 | Escopo e paridade de contratos | Agente/skill orientam o fluxo e MCP expõe as funções `research/legal_oa_pipeline.py` + `research/auditoria_fichamento.py`; o plugin faz somente validação e orientação, sem executar o fluxo ou duplicar decisões de licença; teste cruza 1 DOI OA e 1 fechado no núcleo |
| R-979.6 | Anti-overclaim | Nenhuma superfície promete Qualis, nota ou aceite; skill e agente declaram revisão humana obrigatória |

## Invariantes

- INV-979.1: Nenhuma superfície contata Sci-Hub; bloqueio testado em MCP e plugin.
- INV-979.2: Pasta de auditoria permanece obrigatória; MCP sem `auditar_pasta` é incompleto.
- INV-979.3: Stdlib no núcleo; `mcp` e `pydantic` só na borda MCP; `typescript` só no plugin.
- INV-979.4: O plugin normaliza um DOI canônico, rejeita entradas ausentes,
  tipos indevidos e campos desconhecidos e bloqueia fontes proibidas sem
  diferença de caixa. Sua resposta declara `guidance_only=true`,
  `file_creation=false`, `pipeline_executed=false`, `network_performed=false`
  e `evidence_eligible=false`; a pasta é uma sugestão, sem fichamento criado.

## Fora de escopo

- Registro em `opencode.json` e `agents/catalog/README` automatizado; instalação de pacotes PyPI; download integral em testes.

## Validação

`tests/test_r979_agente_skill_plugin_mcp.py` preserva existência, frontmatter,
objeto FastMCP e paridade OA/fechado com doubles. Também importa o plugin e
o SDK 1.18.4 em Node real, executa sua ferramenta e schemas e publica o
JSON Schema. Instrumentação bloqueia rede e escrita durante todas as provas.

Em 11/10/2026, o cast da factory ocultava schemas JSON incompatíveis e
retorno de objeto fora do contrato. RED: 13 falhas/16 aprovações, além de
TS2322 integral. Um RED adicional identificou transform DOI incompatível com
JSON Schema; a canonicalização passou para a execute. GREEN final:
30 aprovações (10,01 s), incluindo cinco testes anteriores preservados;
typecheck integral sem erros. Registros em `outputs/core-r820/plugin-sdk-*`
e `typecheck-plugin-red.txt`/`typecheck-final.txt`. Isso comprova execução
local da orientação, sem inferência de agente externo ou execução do pipeline.
