# Spec: Agent Manager (core/agent_manager.py)

**Versao:** 1.0.0
**Status:** active
**Manutencao SWEBOK:** evolutiva (frequencia: media)
**Ultima revisao:** 2026-05-27
**Spec baseada em:** codigo-fonte `ecosystem_backup/core/agent_manager.py`

---

## 1. Comportamento Esperado

Gerencia o ciclo de vida completo de agentes no ecossistema:
- Registro de tipos de agente (AgentTypeDef)
- Criacao de instancias (AgentInstance) com configuracao
- Execucao assincrona com contexto
- Health check periodico
- Destruicao limpa de recursos
- Maquina de estados: CREATED → INITIALIZING → READY → RUNNING → COMPLETED | FAILED → DESTROYED

## 2. Usuarios e Contexto

- **Usuarios:** Outros componentes do ecossistema (orquestradores, evolver, nexus)
- **Volume:** 118 agentes registrados, ate 10 execucoes simultaneas
- **Ambiente:** Python 3.11+, async/await
- **Dependencias:** core.errors (AgentError, NotFoundError), Container (DI)

## 3. Restricoes

- Agentes devem implementar Protocol `Agent` (initialize, execute, health_check, destroy)
- Cada agente tem ID unico (UUID)
- Execucao e assincrona (async/await)
- Suporta DI via Container (modo novo) e modo legado (sem DI)

## 4. Casos de Borda

- Agente nao registrado: levantar NotFoundError
- Agente falha durante execucao: capturar excecao, transicionar para FAILED, loggar
- Health check falha: reportar status unhealthy, nao destruir automaticamente
- Timeout de execucao: cancelar task, transicionar para FAILED
- Multiplas execucoes simultaneas: cada agente e isolado, sem compartilhamento de estado

## 5. Criterios de Aceitacao

- [ ] Registrar tipo de agente e criar instancia com sucesso
- [ ] Executar agente e receber resultado
- [ ] Agente que falha transiciona para FAILED (nao quebra o manager)
- [ ] Health check retorna status de cada agente ativo
- [ ] Destruir agente limpa recursos e remove do registro
- [ ] Modo legado (sem DI) funciona identico ao modo com DI
- [ ] 10 agentes executando simultaneamente sem interferencia

## 6. Testes

- `tests/core/test_agent_manager.py` (a verificar existencia)
- Cenario: registro → criacao → execucao → health_check → destroy
- Cenario: agente nao registrado → NotFoundError
- Cenario: execucao com falha → estado FAILED
