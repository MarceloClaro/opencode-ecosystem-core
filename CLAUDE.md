# System Instructions
Responda sempre em português brasileiro (pt-BR).

# OpenCode Ecosystem Core — Manual para o Claude Code

Este arquivo é lido automaticamente pelo Claude Code sempre que ele opera neste repositório. É o guia rápido do projeto: o que é, como rodar, onde procurar mais detalhe.

## O que é este projeto

Um ecossistema de orquestração multiagente (`marceloclaro/orchestrator.py::MarceloClaroOrchestrator`) que integra: MCI (MetaBus/Blackboard/Reflexion — memória metacognitiva compartilhada), Trust Engine, Token Economy, um pipeline científico agentivo (EvoSci → Deep Research → Peer Review → Revision → Paper Composer), SDD/TDD, Loop Engineering, e um catálogo de 160+ agentes especializados.

## Comandos essenciais

```bash
# CLI interativo do orquestrador (menu com ajuda e helpdesk)
python3 -m marceloclaro.cli

# Comandos diretos
python3 -m marceloclaro.cli status     # status geral do ecossistema
python3 -m marceloclaro.cli agents     # lista agentes registrados
python3 -m marceloclaro.cli doctor     # diagnóstico de saúde (specs, evolução, CLIs externas...)
python3 -m marceloclaro.cli helpdesk   # doctor + sugestões de correção em linguagem simples
python3 -m marceloclaro.cli ajuda      # resumo de ajuda + caminho do manual

# Regenerar a configuração do OpenCode CLI (opencode.json) após mudar agents/catalog/*.md
python3 -m integrations.opencode_cli

# Rodar a suíte de testes
python3 -m pytest tests/ -q
```

## Antes de editar código

1. Rode `python3 -m marceloclaro.cli doctor` — confirma que specs formais carregam, o registro de evolução não perdeu histórico, e as CLIs externas relevantes estão disponíveis.
2. Este projeto segue disciplina SDD/TDD real: toda mudança de peso ganha uma especificação em `specs/SPEC-935-R*.md` **antes** da implementação, e testes em `tests/test_r*.py` **antes** de considerar a tarefa concluída.
3. Nunca declare algo "superhuman", "verificado" ou "Qualis A1" sem validação externa explícita — ver `mci/metacognitive_evaluator.py::classify_metacognitive_tier()` (política já codificada) e `CORRIGENDUM.md` (histórico de alegações da própria documentação já corrigidas).

## Depois de mudanças relevantes

1. Registre um ciclo de evolução: `evolution_registry.record(...)` (ver `evolution/cycles.py`) — **cuidado**: `EvolutionRegistry.save()` reescreve `evolution/cycles.json` inteiro; se o arquivo tiver entradas com campos legados não modelados no dataclass `EvolutionCycle`, prefira anexar manualmente via `json.load`/`json.dump` para não perder conteúdo (ver histórico do R108 no CHANGELOG/evolution/evo-21).
2. Rode a suíte completa antes de commitar: `python3 -m pytest tests/ -q`.
3. Ao commitar, restrinja o `git commit` aos arquivos do ciclo atual (pathspec explícito) — este repositório costuma ter trabalho não relacionado pendente de outras frentes; não misture.

## Retomada de trabalho (checkpoints) — R129

Sessões do Claude Code podem terminar no meio (limite de sessão/tokens do plano). Para que o trabalho **nunca** se perca:

1. **Leia `PROGRESS.md` na raiz primeiro.** É o checkpoint vivo: estado atual, próximos passos resumíveis e como retomar. Complementa o histórico de `evolution/cycles.json`.
2. **Quebre trabalho longo em passos pequenos**, cada um commitável e verificável (spec → testes → implementação → ciclo → commit escopado). A perda máxima passa a ser o passo em andamento, não o trabalho inteiro.
3. **Atualize `PROGRESS.md` e commite a cada passo concluído** (ou quando pausar), para a próxima sessão retomar sem re-derivar contexto.
4. **Tarefas demoradas (suíte completa, downloads) rodam em background**; o estado fica persistido em commits + `PROGRESS.md`.

## Onde encontrar o quê

| Preciso de... | Onde está |
|---|---|
| Manual de uso em linguagem simples | `MANUAL.md` |
| Arquitetura técnica completa | `ARCHITECTURE.md` |
| Instalação (Windows/Linux/macOS) | `installer/README.md` |
| Instruções para agentes do OpenCode CLI | `AGENTS.md` |
| Histórico de correção de overclaims | `CORRIGENDUM.md` |
| Especificações formais (SDD) | `specs/SPEC-935-R*.md` |
| Registro de ciclos de evolução | `evolution/cycles.json` + `evolution/evo-*.md` |
| Orquestrador principal | `marceloclaro/orchestrator.py` |
| Diagnóstico/helpdesk | `marceloclaro/doctor.py` / `marceloclaro/helpdesk.py` |
| Skill Médico Virtual Supremo | `skills/medico_virtual_supremo/` |
| Hooks clínicos | `skills/medico_virtual_supremo/hooks/clinical_hooks.py` |
| Plugins de validação cruzada | `skills/medico_virtual_supremo/plugins/cross_validation.py` |
| Raciocínio científico (GRADE/PICO/Bayes) | `skills/medico_virtual_supremo/reasoning/` |
| Pipeline transformer de orquestração | `skills/medico_virtual_supremo/orchestration/transformer_pipeline.py` |
| Agentes especialistas | `agents/catalog/medico-{cardiologista,neurologista,radiologista,infectologista,clinico-geral}.md` |
| Integração CLI | `skills/medico_virtual_supremo/integration.py` |
| MCP Server para Antigravity | `integrations/antigravity/medico_mcp_server.py` |
| SPEC de integração | `specs/SPEC-935-R205.md` |
| Skill para ChatGPT | `Medicina/SKILL_CHATGPT.md` |

## Médico Virtual Supremo — Skill de Apoio Clínico

O repositório inclui uma skill completa de apoio à decisão clínica. Para usá-la
diretamente pelo Claude Code:

### Análise clínica rápida
```bash
python3 -m skills.medico_virtual_supremo.integration analisar patient_education "Estou com febre e tosse há 3 dias"
python3 -m skills.medico_virtual_supremo.integration analisar professional_cds "Paciente com IAM há 2h" --formato json
```

### Triagem de emergência
```bash
python3 -m skills.medico_virtual_supremo.integration urgencia "Paciente com dor no peito e falta de ar"
```

### Roteamento para especialista
```bash
python3 -c "from skills.medico_virtual_supremo.orchestration.transformer_pipeline import criar_pipeline_padrao; p=criar_pipeline_padrao(); r=p.processar({'request':'Paciente com AVC','clinical_summary':{'problem_representation':'Síndrome neurológica'},'safety':{'emergency_detected':True},'assessment':{'hypotheses':[]}}); print(f'Especialista: {r.especialista_principal.nome} - {r.justificativa}')"
```

### Raciocínio bayesiano (probabilidade diagnóstica)
```bash
python3 -c "from skills.medico_virtual_supremo.reasoning.diagnostic_reasoning import criar_raciocinio_padrao; m=criar_raciocinio_padrao(); r=m.avaliar_teste('ecg_para_iam',0.4,True,'IAM'); print(f'Pré: {r.prob_pre_teste:.1%} → Pós: {r.prob_pos_teste:.1%} (LR+={r.lr_aplicado}) (interpretação: {r.interpretacao})')"
```

### Gatilhos de segurança
- Nunca sugerir prescrição ou dose autônoma
- Emergência (SAMU 192) deve ser acionada imediatamente se detectada
- Revisão humana obrigatória para qualquer decisão clínica
- Não substitui avaliação presencial

### Testes da medical skill
```bash
python3 -m pytest tests/test_r205_medico_supremo_integration.py -v
```
