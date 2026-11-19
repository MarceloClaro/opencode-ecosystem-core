---
spec_id: SPEC-935-R1228
title: Expor observabilidade MCP no status do túnel ChatGPT
status: draft
validation_scope: local_runtime
component: integrations/chatgpt_tunnel_full_mcp.py
test_file: tests/test_r1228_chatgpt_tunnel_health_mcp.py
---

# SPEC-935-R1228 — Expor observabilidade MCP no status do túnel ChatGPT

- **Origem:** autorização explícita do operador para as melhorias de integração, após diagnóstico que separou o polling do túnel da descoberta MCP pelo cliente.
- **Objetivo:** fazer `status()` consultar `/health/mcp` no listener local do túnel e expor um resumo sanitizado da observação, sem misturar esse sinal com `readyz` ou polling do control plane.
- **Escopo:** somente leitura local do endpoint, projeção de campos de descoberta e testes automatizados; não alterar a configuração nem o ciclo de vida do túnel.

## Problema

O status atual usa `/readyz` e `/health/control-plane`, permitindo confirmar readiness/polling. Esses sinais não demonstram que o runtime observou `initialize` ou `tools/list` do cliente MCP. O runtime v0.0.21 dispõe de `/health/mcp`, que pode reportar `state=not_observed` sem invalidar o polling.

## Contrato

1. `status()` consulta `/health/mcp` somente quando há PID gerenciado ativo e `health-url` local válido; a consulta é GET read-only.
2. O resultado acrescenta `mcp_discovery`, separado dos campos históricos `tunel`, `mcp`, `ultimo_poll_utc`, `readyz` e `http`.
3. `mcp_discovery` contém `available`, `status`, `state`, `initialize_epoch`, `initialize` e `tools_list`. `initialize` e `tools_list` são projeções limitadas dos campos homônimos do endpoint; não incluir credenciais, conteúdo bruto, caminho de chave ou conteúdo de headers.
4. Uma resposta válida com `state=not_observed` deve permanecer explicitamente `not_observed`, com os estados de initialize/tools observados, sem rebaixar ou promover o estado do polling.
5. Endpoint ausente, resposta HTTP não-2xx, JSON inválido ou schema incompatível deve resultar em observabilidade indisponível/unknown, sem exceção e sem ser confundida com descoberta bem-sucedida.
6. O status continua sem iniciar, parar ou reiniciar processos, alterar arquivos de configuração/credenciais ou contatar a interface ChatGPT externa.

## Não-objetivos

- Não iniciar/reiniciar o túnel nem o processo MCP.
- Não alterar credenciais, permissões, configuração OpenCode/ChatGPT ou serviços externos.
- Não alegar que o ChatGPT descobriu ou invocou ferramentas sem evidência de uma chamada observada no cliente externo.
- Não alterar os critérios de `polling_confirmado`, `/readyz` ou control plane além do necessário para manter compatibilidade de leitura.

## Critérios de aceitação executáveis

- `R1228-STATUS-COMPAT` O status mantém os campos e valores históricos de polling/readiness; `mcp_discovery` é aditivo e independente.
- `R1228-MCP-NOT-OBSERVED` Uma resposta válida `state=not_observed` é exposta como tal, incluindo `initialize_epoch` e flags/lista de tools, sem inferir descoberta.
- `R1228-MCP-OBSERVED` Estados positivos de `initialize` e `tools/list` e nomes de ferramentas são projetados do endpoint, sem expor o corpo bruto.
- `R1228-MCP-FAIL-CLOSED` Endpoint ausente, HTTP não-2xx, resposta malformada ou incompatível produz estado indisponível/unknown e não altera a conclusão independente de polling.
- `R1228-READONLY` A consulta não inicia processos nem acessa o arquivo de chave; o teste verifica que o status apenas consulta os endpoints de saúde esperados.

## Verificação e limites

- Executar primeiro os testes novos e registrar RED antes da implementação.
- Depois executar a suíte focal do túnel, regressões do ciclo de vida gerenciado, `SpecVerifier`/`TDDRunner` e `git diff --check`.
- A resposta do endpoint é evidência de observação pelo runtime local, não comprovação de visibilidade/invocação na interface externa do ChatGPT.
