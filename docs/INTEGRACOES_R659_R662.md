# Integrações de agentes, hooks, MCPs, CLI, plugins e skills

As correções R659–R662 conectam os contratos locais ao orquestrador
`MarceloClaroOrchestrator`. O relatório de diagnóstico distingue configuração,
descoberta, emissão de arquivos e execução concluída.

## Uso

Na raiz do projeto, use o ambiente Python do projeto:

```bash
.venv/bin/python -m marceloclaro.cli integracoes status
.venv/bin/python -m marceloclaro.cli integracoes verificar
.venv/bin/python -m marceloclaro.cli integracoes skill core-hooks
.venv/bin/python -m marceloclaro.cli integracoes handoff <artifact_id>
```

`status` e `verificar` inspecionam arquivos e metadados; não iniciam os servidores
MCP nem modelos. O comando retorna erro quando encontra referências quebradas.
Um iniciador ausente aparece como aviso. A existência do iniciador não comprova
que o servidor ou o modelo consiga executar uma solicitação.

O comando OpenCode `/integracoes` usa o agente primário `marceloclaro`. O servidor
`ecosystem-network` oferece três ferramentas de consulta:

| Ferramenta | Resultado |
| --- | --- |
| `ecosystem_integration_status` | Configuração dos seis componentes e inconsistências locais |
| `ecosystem_skill_plan` | Documento local, hash atual e forma de handoff |
| `ecosystem_artifact_handoff` | Fonte registrada, política, integridade e plano de leitura |

As três interfaces retornam `executed=false` e `execution_verified=false`.
Para obter IDs de artefatos, consulte `.venv/bin/python -m marceloclaro.cli harness inventory`
e o ranking de `harness route "descrição da tarefa"`. As ferramentas já existentes
da rede, dos workflows e da biblioteca continuam disponíveis.

## Correções

**Hooks e SDK (R659).** O SDK aplica `PreToolUse`, `PostToolUse`, `SessionStart`
e `SessionEnd`, incluindo a configuração legada `matchers`. Uma exceção no
corpo de um hook não provoca sua execução novamente. O histórico de ferramentas
inclui a mensagem do assistente com `tool_calls` antes das respostas das
ferramentas. Argumentos e schemas são validados antes de chamar os handlers,
inclusive depois de um hook que altere os argumentos. Ferramentas proibidas não
são anunciadas ao modelo. Falhas e esgotamento do orçamento produzem código de
saída não zero na CLI. A auditoria de comandos registra hash e tamanho, sem
armazenar o comando completo. A política de comandos continua sendo uma lista
de bloqueio; ela não implementa um isolamento do sistema operacional.

**MCPs (R660).** A validação compartilhada respeita o dialeto JSON Schema,
campos obrigatórios, tipos, itens, limites, alternativas e propriedades extras.
Schemas inválidos, números não finitos e referências externas são recusados
sem resolver documentos pela rede. MCI e Synthetic University validam antes de
alterar estado ou executar handlers. Scanner e Colibri usam o contrato anunciado
em `tools/list`. O adaptador Colibri chama `complete` e propaga falhas do provedor.
Os schemas de ferramentas são parte do contrato MCP. Veja a
[especificação de ferramentas MCP](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
e a [validação JSON Schema](https://json-schema.org/draft/2020-12/json-schema-validation).

**Plugins e skills (R661).** A descoberta inclui as árvores modernas do Codex.
Skills homônimas de origens diferentes mantêm identidades e destinos distintos;
mirrors idênticos podem ser deduplicados. A emissão conserva as restrições de
invocação e os arquivos de apoio contidos na origem. Scripts copiados são dados:
a emissão não os executa. A preparação de handoff confere fonte, hash e políticas.
Uma exportação de plugin que declara `./skills` produz essa árvore. Exportação
local não comprova instalação no aplicativo ou aprovação do plugin.

**CLI e orquestrador (R662).** As consultas CLI e MCP usam o mesmo serviço
central, sem delegação direta aos especialistas do catálogo. As entradas Python
dos MCPs gerados usam `.venv/bin/python`; o iniciador `uvx` é resolvido também nas
instalações do usuário fora do caminho de busca habitual. Isso evita depender de
bibliotecas Python diferentes entre o terminal e o OpenCode.

## Evidência e reprodução

As especificações ficam em `specs/SPEC-935-R659-*` até `SPEC-935-R662-*`, com
testes próprios em `tests/test_r659_*` até `test_r662_*`. Os registros finais
ficam em `docs/evidence/`:

- `R659_SDK_HOOKS_LIVE.json`: síntese de duas provas locais complementares do
  mesmo modelo, com links e hashes dos registros originais. A fase de soma e
  resposta final está em `R659_SDK_HOOKS_LLAMA_PARTIAL.json`; o veto explícito
  está em `R659_SDK_HOOKS_LLAMA_DENY.json`. A tentativa Qwen que falhou permanece
  em `R659_SDK_HOOKS_QWEN_FAILED.json`. A captura de request da tentativa parcial
  tinha uma referência mutável; respostas, hooks e execução nativa foram
  preservados. O script foi corrigido antes da prova de veto.
- `R660_MCP_STDIO.json`: comunicação MCP real e entradas negativas, com memória
  de teste isolada. Não comprova inferência de todos os provedores.
- `R662_CORE_INTEGRATIONS_REAL.json`: configuração reproduzida, emissão isolada
  de uma skill existente e equivalência entre CLI e MCP pelo orquestrador.
- `R659_R662_RELEASE_GATE.json`: testes, análises locais, hashes, diagnóstico e
  resultados de cada prova, sem alegação de auditoria externa.
- `R659_R662_MUTATIONS.json`: três defeitos injetados em processos de teste,
  para confirmar que perda de hooks, validação e política é detectada. Essa
  evidência usa testes de contrato; não corresponde a inferência real.

Reprodução das provas:

```bash
.venv/bin/python scripts/probe_mcp_contracts.py
.venv/bin/python scripts/probe_core_integrations.py
.venv/bin/python scripts/probe_sdk_hooks_live.py --model llama3.2:latest
.venv/bin/python -m integrations.opencode_cli
.venv/bin/python -m marceloclaro.cli doctor
```

As provas com modelo exigem memória disponível e um provedor local ativo.
Erros, limites e indisponibilidade devem permanecer nos registros. Os testes
de contrato usam fixtures isoladas; somente os arquivos de prova identificados
como execução real sustentam afirmações sobre comunicação ou inferência real.
