# Spec: Task Queue (core/task_queue.py)

**Versao:** 1.0.0 | **Status:** active | **SWEBOK:** evolutiva | **Revisao:** 2026-05-27

## 1. Comportamento
Fila assincrona de tarefas com prioridade e controle de concorrencia. Gerencia execucao de tarefas com estados PENDING→RUNNING→COMPLETED|FAILED. Suporta 4 niveis de prioridade (LOW, NORMAL, HIGH, CRITICAL), limite de concorrencia configuravel e integracao com IEventBus para notificacoes.

## 2. Usuarios
- Usuarios: agentes, evolucao, plugins que precisam enfileirar trabalho assincrono
- Volume: ate 100 tarefas simultaneas
- Ambiente: Python 3.11+, asyncio

## 3. Restricoes
- Concorrencia limitada (default: 10 tarefas simultaneas)
- Prioridades: CRITICAL > HIGH > NORMAL > LOW
- Tarefas sao executadas em ordem de prioridade (nao FIFO)
- Thread-safe para enfileiramento

## 4. Bordas
- Fila cheia (concorrencia maxima): tarefa aguarda em PENDING
- Tarefa falha: estado FAILED, nao bloqueia a fila
- Timeout: tarefa cancelada apos timeout configuravel
- Shutdown: tarefas PENDING sao canceladas, RUNNING aguardam conclusao

## 5. Criterios
- [ ] Enfileirar e executar tarefa com sucesso
- [ ] Tarefa CRITICAL executa antes de LOW
- [ ] Concorrencia maxima respeitada
- [ ] Falha em uma tarefa nao afeta outras
- [ ] Shutdown graceful (tarefas RUNNING concluem)
- [ ] EventBus notifica transicoes de estado
