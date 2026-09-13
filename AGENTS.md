# Instruções para Agentes (OpenCode CLI)

Este arquivo é lido automaticamente pelo OpenCode CLI (`opencode.json.instructions`) para orientar qualquer agente que opere neste repositório — incluindo o agente primário `marceloclaro`, os 205 agentes especialistas do catálogo (`agents/catalog/`), os 209 subagentes configurados no `opencode.json` e os 210 agentes registrados no Blackboard do orquestrador.

## Regras gerais

1. **Idioma**: responda sempre em português brasileiro formal.
2. **Ponto de entrada**: o orquestrador `marceloclaro` (`marceloclaro/orchestrator.py::MarceloClaroOrchestrator`) é o agente primário — ele coordena todos os demais via Blackboard (protocolo A2A) e MetaBus (memória metacognitiva compartilhada). Não delegue diretamente a subagentes do catálogo sem passar pelo orquestrador quando a tarefa envolver múltiplos passos.
3. **SDD/TDD**: toda funcionalidade nasce de uma especificação (`specs/SPEC-935-R*.md`) e é validada por testes (`tests/test_r*.py`) antes de ser considerada concluída. Ver `sdd/spec_engine.py`.
4. **Anti-overclaim**: nunca declare um resultado como "superhuman", "verificado" ou "Qualis A1" sem validação externa explícita — ver `mci/metacognitive_evaluator.py::classify_metacognitive_tier()` e `CORRIGENDUM.md` para o histórico de alegações já corrigidas.
5. **Antes de editar**: rode `python3 -m marceloclaro.cli doctor` para confirmar que o ambiente está saudável (specs carregando, registro de evolução íntegro, memória metacognitiva acessível).
6. **Depois de mudanças relevantes**: registre um ciclo de evolução (`evolution_registry.record(...)`, ver `evolution/cycles.py`) e, se aplicável, uma spec formal em `specs/SPEC-935-R*.md`.
7. **Invocação de skills e continuidade de pipelines**: quando uma skill filha estiver marcada com `disable-model-invocation: true` no `SKILL.md` ou `policy.allow_implicit_invocation: false` em `agents/openai.yaml`, **não** tente acioná-la implicitamente pelo Skill tool nem pelo mecanismo de subagente por nome. O orquestrador deve localizar e ler o `SKILL.md` correspondente e executar suas instruções no contexto atual. Se o usuário já respondeu `CONTINUAR` ao próximo passo sugerido, isso é consentimento explícito para esse handoff; não interrompa o pipeline exigindo que ele digite `/nome-da-skill`. Para resolução determinística, use `reversa_universal.skill_dispatch.ReversaSkillDispatcher` (SPEC-935-R471).

## Onde encontrar o quê

- Manual de uso (linguagem simples): `MANUAL.md`
- Arquitetura técnica completa: `ARCHITECTURE.md`
- Manual do Claude Code neste projeto: `CLAUDE.md`
- Diagnóstico de saúde: `python3 -m marceloclaro.cli doctor`
- Ajuda guiada (helpdesk): `python3 -m marceloclaro.cli helpdesk`
- Regenerar esta configuração do OpenCode CLI: `python3 -m integrations.opencode_cli`

## Regenerar `opencode.json`

Este arquivo de instruções, o catálogo de agentes e os comandos customizados são compilados automaticamente por `integrations/opencode_cli.py`. Após adicionar/editar um agente em `agents/catalog/*.md`, rode:

```bash
python3 -m integrations.opencode_cli
```
