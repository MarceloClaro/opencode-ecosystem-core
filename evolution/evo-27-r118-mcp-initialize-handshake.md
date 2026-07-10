# R118 — Correção do Handshake MCP em metacognitive-interconnect

## Objetivo

Corrigir a falha real do servidor MCP `metacognitive-interconnect` reportada pelo usuário ("metacognitive-interconnect failed"): qualquer cliente MCP real reportava a conexão como falha porque o servidor não implementava o método `initialize`, obrigatório no início de toda sessão MCP.

## Mudanças Entregues

1. **Causa raiz confirmada por reprodução real** — enviado um `initialize` de verdade via stdin ao servidor antes de qualquer correção: resposta `{"isError": true, "content": [{"type": "text", "text": "Método não suportado"}]}`. `SimpleMCPServer.handle_request()` só tratava `tools/list` e `tools/call`, caindo no fallback de erro genérico para `initialize`.

2. **`mci/mcp_server.py::SimpleMCPServer.handle_request()`**
   - Implementado `initialize`: retorna `protocolVersion` (ecoando o que o cliente pediu), `capabilities: {"tools": {}}`, `serverInfo` com nome e versão
   - Implementado `ping`: responde vazio sem erro

3. **`mci/mcp_server.py::SimpleMCPServer.run_stdio()`**
   - Requisições sem `id` (notificações, ex. `notifications/initialized`) deixam de gerar resposta JSON-RPC — corrige uma violação da especificação que existia mesmo antes deste bug ser notado, e que poderia confundir clientes MCP estritos

4. **Verificação de escopo**: `integrations/antigravity/antigravity_mcp_server.py` já implementava `initialize`/`notifications/initialized` corretamente — não precisou de correção, mas vale o precedente de auditar servidores MCP do ecossistema por esse padrão de bug.

5. **Cobertura de testes**: `tests/test_r118_mcp_initialize_handshake.py` (6 testes) — handshake completo, eco de `protocolVersion`, `ping`, `tools/list` pós-handshake, supressão de resposta a notificação, não-supressão de resposta a requisição com `id`.

## Verificação

- Reprodução manual via stdin ANTES da correção: confirmado o erro exato relatado pelo usuário
- Reprodução manual via stdin DEPOIS da correção: sequência `initialize` → `notifications/initialized` → `tools/list` retorna exatamente as respostas esperadas (2 linhas de resposta para 2 requisições com `id`, zero para a notificação)
- `python3 -m pytest tests/test_r118_mcp_initialize_handshake.py -v` → 6 passed
- `python3 -m pytest tests/ -q` completo

## Lições

1. Um servidor MCP customizado que só trata `tools/list`/`tools/call` sem tratar `initialize` passa despercebido em testes que chamam os handlers diretamente (como os de `synthetic_university/mcp_server.py`) — só falha quando um cliente real de protocolo faz o handshake completo. Vale ter pelo menos um teste de handshake por servidor MCP do ecossistema.
2. Reproduzir o bug de verdade via stdin (não só ler o código) foi o que confirmou a causa raiz com certeza antes de escrever a correção — a mesma disciplina de "trust but verify" já aplicada em ciclos anteriores.
3. O outro servidor MCP do projeto já tratava `initialize` corretamente — um bom sinal de que o padrão correto já era conhecido no código, só não tinha sido replicado neste arquivo mais antigo.

## Score

**9.1/10**

- Corrige um bug real e reportado diretamente pelo usuário, com reprodução confirmada antes e depois
- Escopo contido e preciso (não tocou no servidor que já funcionava)
- Testes de regressão cobrindo exatamente o mecanismo do bug (handshake + notificações)
