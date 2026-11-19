# SPEC-935-R1224 — Clareza entre configuração e prontidão operacional de integrações

- **Status:** implementada; testes locais verdes; limitações de prontidão externa preservadas
- **Data:** 2026-11-19
- **Componente:** `marceloclaro/integration_service.py` e superfície MCP R662
- **Contexto:** diagnóstico `SPEC-935-R662` pode retornar `config_checked` e `issues=[]`, enquanto transporte, descoberta e invocação não foram sondados.

## Objetivo

Mitigar a leitura equivocada de um inventário/configuração válida como prova de
que integrações MCP, plugins de cliente, WSL ou Desktop estejam conectados e
operacionais. Preservar compatibilidade do status R662, mas publicar escopo de
verificação e lacunas operacionais explicitamente.

## Escopo

- Acrescentar ao resultado do status R662 um campo de prontidão que fique em
  `CONFIG_ONLY` quando a configuração não tem erros e em `CONFIG_INVALID`
  quando há erro de configuração.
- Descrever em campos distintos o que foi verificado (configuração/inventário)
  e o que não foi sondado (transporte, descoberta de ferramentas, invocação e
  execução de tarefa).
- Declarar que clientes/plugins externos não são observáveis por esse diagnóstico.
- Manter `status`, `executed`, `execution_verified` e `issues` compatíveis com
  consumidores existentes; zero issues significa somente ausência de achados
  de configuração.

## Não objetivos / limites

- Não iniciar, autenticar, reiniciar ou modificar MCPs, plugins, WSL, Desktop,
  túnel ou serviços externos.
- Não executar os comandos MCP configurados nem fazer sondas de rede.
- Não provar tool discovery/invocação nem transformar dados fornecidos pelo
  operador em validação independente.
- Não ler nem alterar credenciais ou configurações do ChatGPT/Codex.

## Critérios de aceitação

1. Configuração válida retorna `status=config_checked` por compatibilidade e
   prontidão explícita `CONFIG_ONLY`.
2. Configuração inválida retorna prontidão `CONFIG_INVALID`.
3. O recibo diferencia `checked` de `not_probed` para cada estágio operacional.
4. `issues=[]` não promove transporte, descoberta, invocação ou execução.
5. O diagnóstico continua read-only e não executa nenhum processo configurado.
6. Testes R662 e superfície MCP existente continuam passando.

## Plano de verificação

- RED: adicionar teste da nova semântica e observar falha antes da implementação.
- GREEN: acrescentar somente metadados de prontidão ao retorno R662.
- Regressão: executar os testes R662, fachada MCP/Chat e doctor disponível no
  ambiente; informar bloqueios de dependências sem ocultá-los.

## Evidência observada

- RED: os dois novos testes falharam por `KeyError: 'readiness'` antes da alteração.
- GREEN/regressão: `.venv/bin/python -B -m pytest -q tests/test_r662_integration_surface.py tests/test_r640_ecosystem_surface.py tests/test_r1090_chatgpt_status_mcp.py tests/test_r1222_mcp_discovery_bridge.py` → `40 passed`.
- `git diff --check` → sem erros de whitespace.
- Doctor via `.venv/bin/python -m marceloclaro.cli doctor` → `overall=degraded`, `0` falhas, `6` avisos; chaves/provedores e CLIs opcionais ausentes. `python3` do sistema não importa `whoosh`; o runtime `.venv` do projeto funciona.
- Sonda read-only do runner `integrations.chatgpt_tunnel_full_mcp status` → `polling_confirmado`, PID `719476`, último poll `2026-11-19T08:47:23.297932449Z`. Isso comprova health/polling do control plane observado, não catálogo MCP no cliente nem execução de tarefa.
- A chamada MCP `ecosystem_integration_status` retorna `config_checked`, `executed=false`, `execution_verified=false`; com R1224, `readiness.state=CONFIG_ONLY`. O diagnóstico não ativa nem sonda os plugins externos.
- A chamada pela ferramenta MCP de longa duração nesta sessão ainda retornou o schema anterior, sem `readiness`, embora a CLI local já retorne o novo campo. O arquivo-fonte e os testes estão atualizados; o processo MCP consumidor ainda precisa ser recarregado para propagar a alteração. Não foi reiniciado automaticamente para evitar interromper sessões/transporte.
- `opencode mcp list` mostrou 33 conexões configuradas; `ecosystem-network`, `desktop-operator` e outras locais relevantes ao OpenCode aparecem conectadas, enquanto `metacognitive-interconnect`, `arxiv-mcp`, `artigo-academico-mcp` e `fetch` reportaram timeout. Esses estados pertencem ao OpenCode local e não validam plugins homônimos em ChatGPT/Desktop.
- Permanecem não verificados: catálogo completo visível no Chat, executor WSL independente, plugins Desktop/Core Local em seus clientes próprios e execução de ferramenta exclusiva por cada transporte.
