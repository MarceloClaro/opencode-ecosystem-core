# SPEC-935-R1090 — Fachada de status para ChatGPT Chat

## Objetivo e escopo

Oferecer um processo MCP stdio separado para conexão autorizada por Secure
MCP Tunnel, expondo exclusivamente `ecosystem_integration_status`. A fachada
reutiliza a função existente de `integrations.ecosystem_mcp`, preservando o
primário MarceloClaro e o contrato de diagnóstico R662.

Esta mudança prepara a superfície local. Não cria túnel, endpoint público,
credencial, App nem associação de conta. O aceite no ChatGPT Chat depende de
conexão real ao plugin `opencode-ecosystem-core@created-by-me-remote`, descoberta
da ferramenta e chamada concluída naquela conversa; permanece pendente até
essa evidência existir.

## Contrato

- `integrations.chatgpt_status_mcp` inicia servidor MCP stdio independente.
- `tools/list` anuncia somente `ecosystem_integration_status`, sem argumentos
  obrigatórios e com `readOnlyHint=true`, `destructiveHint=false`,
  `idempotentHint=true` e `openWorldHint=false`.
- O registro reutiliza diretamente a função existente, sem copiar lógica,
  alterar a resposta ou remover ferramentas do servidor completo do Core.
- Não publicar recursos, prompts, ferramentas de execução ou de escrita.
- Chamadas a nomes fora dessa lista retornam erro MCP. Não há despachante
  genérico nem parâmetro de seleção de operação.
- Preservar `executed=false` e `execution_verified=false` do diagnóstico;
  configuração observada não comprova ativação, inferência ou autenticação.
- Os resultados enviados pelo túnel à conversa podem ser processados pelo
  ChatGPT; processo WSL local não significa inferência offline.

## Execução local

No Windows, usar vetor de argumentos equivalente a:

```powershell
wsl.exe -d Ubuntu --cd /home/marceloclaro/opencode-ecosystem-core --exec /home/marceloclaro/opencode-ecosystem-core/.venv/bin/python -m integrations.chatgpt_status_mcp
```

Este comando serve stdio e aguarda cliente MCP. Não publica um endereço web.

## Aceitação e validação

`tests/test_r1090_chatgpt_status_mcp.py` verifica a superfície mínima, a
preservação do registro completo e o protocolo em processo novo. A chamada
real usa o checkout local e confirma o contrato R662 sem exigir que o
inventário esteja livre de avisos. A negativa para `ecosystem_run` precisa
retornar `isError=true` e a sessão continua respondendo ao diagnóstico.

Registrar RED antes da implementação e GREEN após implementação; executar
regressões R662/R912/R640 e verificar diferenças. Validação local e conexão
efetiva no ChatGPT Chat devem permanecer separadas no relatório.
