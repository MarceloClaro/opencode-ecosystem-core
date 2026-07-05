# Specs: Plugins do Ecossistema OpenCode

**Total:** 5 plugins principais + 3 bibliotecas | **Revisao:** 2026-05-27

---

## Plugins Principais (5)

### ecosystem-sync (v3.5)
**Transformer Cross-Validation Engine.** Sincroniza MCPs, Skills, Agentes, Plugins e Corretores com precisao estatistica.
Pipeline: VALIDATE → CROSS-CHECK → CORRECT → SCORE → SYNC → EVOLVE
- [ ] Cross-validation entre componentes
- [ ] Correcao automatica de inconsistencias
- [ ] Score de afinidade atualizado

### manus-evolve (v2.2)
**PlanAct Autonomous Evolution Engine.** Pipeline: PLAN → ACT → CORRECT → REFLECT → EXTRACT → EVOLVE → NEXUS
- [ ] SENSE: detecta necessidade de evolucao
- [ ] DISCOVER: encontra novas skills/MCPs
- [ ] INSTALL: instala com rollback
- [ ] VERIFY: valida com testes
- [ ] EVOLVE: atualiza estado do ecossistema
- [ ] LEARN: registra aprendizado

### bernstein-sync (v1.0)
**Multi-Agent Orchestration.** Pipeline: DECOMPOSE → SELECT → EXECUTE → VALIDATE → FIX → COMMIT
- [ ] Decomposicao de tarefas complexas
- [ ] Selecao de agentes por expertise
- [ ] Validacao e correcao em ciclo

### antigravity-bridge (v1.0)
**Ponte OpenCode ↔ Antigravity.** Delegacao de tarefas e eventos sincronos.
- [ ] Delegacao: geracao de imagens, browser, pesquisa web
- [ ] Eventos sincronos no pipeline de agentes

### cora-qscore (v1.0)
**Algoritmo UCB1 para selecao adaptativa de debatedores** no Cora-Debate.
- [ ] Q-Score atualizado por performance
- [ ] Selecao balanceada (exploracao vs exploracao)

---

## Biblioteca de Suporte (lib/)

### lib/health.ts (v1.0)
Plugin Health Check Runtime. Endpoint de health check para plugins.
- [ ] Verifica se plugin responde
- [ ] Metricas: uptime, memoria, latencia

### lib/interfaces.ts
Shared type definitions. PluginManifest, ComponentHealth, HealthStatus, interfaces comuns.
- [ ] Tipos compartilhados entre plugins
- [ ] Compatibilidade EcosystemSync ↔ ManusEvolve

### lib/plugin.test.ts
Testes unitarios para plugins (Bun test runner).
- [ ] Cobre todos os plugins principais
- [ ] Mock de dependencias externas

---

## Infraestrutura de Comandos

### command/dispatcher.ts (v1.0)
Unified slash command dispatcher. Carrega metadados de comandos markdown, roteamento por nome.
- [ ] Registro centralizado de comandos
- [ ] Roteamento por nome

### command/command.test.ts
Testes para o CommandDispatcher (Bun test runner).
- [ ] Cobre todos os 27 comandos slash
