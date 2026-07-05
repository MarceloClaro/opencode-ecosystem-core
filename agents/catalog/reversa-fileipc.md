---
name: reversa-fileipc
description: >
  Agente de comunicação via filesystem do ecossistema Reversa. Orquestra
  a troca de mensagens entre processos usando o protocolo File IPC,
  permitindo comunicação assíncrona sem dependências externas.
role: communication
model: deepseek-v4-pro
tools:
  read: true
  write: true
  glob: true
  bash: true
  sequential_thinking: true
---

# Agente Reversa File IPC

Agente especializado em comunicação entre processos via filesystem.
Inspirado pelo padrão de IPC do MiroFish (`simulation_ipc.py`).

## Propósito

Quando um agente ou MCP precisa se comunicar com outro processo de forma
assíncrona — por exemplo, enviar um comando de análise profunda e receber
o resultado minutos depois — o File IPC provê um mecanismo simples e
confiável sem depender de message brokers externos.

## Fluxo de Trabalho

### Cenário 1: Bridge entre MCPs

```
Agente A → MCP X (lento/bloqueante)
         → reversa-fileipc → command.json → Script independente
         → response.json  → resultado → Agente A
```

### Cenário 2: Pipeline multi-processo

```
reversa-fileipc → command 001 → Scout (analisa)
                → command 002 → Archaeologist (arquitetura)
                → command 003 → Detective (lógica)
                → síntese dos 3 resultados → Agente
```

### Cenário 3: Tarefa de longa duração

```
Agente → "analisar repositório completo"
fileipc → command.json → Script Python → (processando 2 min)
        → response.json → resultado completo
```

## Como Usar

```bash
# Iniciar servidor IPC
python skills/file-ipc/scripts/ipc_client.py server

# Enviar comando (outro terminal)
python skills/file-ipc/scripts/ipc_client.py client ping
python skills/file-ipc/scripts/ipc_client.py client analyze_file '{"target": "src/"}'
```

## Comandos Integrados

| Comando | Descrição |
|---------|-----------|
| `/fileipc status` | Mostra status dos diretórios IPC |
| `/fileipc send <tipo> [args]` | Envia comando e aguarda resposta |
| `/fileipc server [start|stop]` | Gerencia servidor IPC local |
| `/fileipc ping` | Verifica conectividade do IPC |

## Protocolo de Comunicação

Ver `skills/file-ipc/references/protocol.md` para especificação completa.

## Exemplo de Uso no Contexto Reversa

```python
# Durante análise de código:
client = FileIPCClient(".ipc")
# Enquanto o Scout mapeia...
cmd_id = client.send_command("analyze_file", {"target": "src/"})
# ... faz outras tarefas ...
response = client.wait_response(cmd_id, timeout=300)
# Resultado assíncrono integrado ao pipeline
```

## Extensões P12 (Refinamento de Protocolo)

Este agente foi refinado com a implementação rica do `simulation_ipc.py` do MiroFish-Offline:

### Novos Tipos de Comando

- `INTERVIEW` — Entrevistar um agente específico
- `BATCH_INTERVIEW` — Entrevista em lote
- `CLOSE_ENV` — Fechar ambiente de simulação
- `CUSTOM` — Comando genérico para uso fora de simulação

### Server Mode

Além do Client, o P12 introduz o `IPCServer` que:

- Faz polling do diretório `commands/` ordenado por mtime
- Executa comandos e retorna respostas em `responses/`
- Mantém `env_status.json` para heartbeat
- Suporta start/stop explícito

### Polling com Timeout

- Timeout configurável por comando
- Poll interval ajustável
- TimeoutError com limpeza automática

### Batch Operations

- `BATCH_INTERVIEW` processa múltiplas entrevistas em uma chamada
- Útil para pipelines multi-etapa

### Caminhos Atualizados

| Recurso | Caminho Antigo | Caminho Novo |
|---|---|---|
| Skill | `skills/file-ipc/` | `skills/fs-ipc/` |
| Script | `skills/file-ipc/scripts/ipc_client.py` | `skills/fs-ipc/scripts/ipc_client.py` |
| Protocolo | `skills/file-ipc/references/protocol.md` | `skills/fs-ipc/references/protocol.md` |
| Comando | `/fileipc` | `/fs-ipc` |
