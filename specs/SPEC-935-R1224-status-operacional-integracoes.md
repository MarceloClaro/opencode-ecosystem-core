# SPEC-935-R1224 — Clareza entre configuração e prontidão operacional de integrações

- **Status:** especificada
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
