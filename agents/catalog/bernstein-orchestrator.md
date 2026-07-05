---
name: bernstein-orchestrator
---

# Bernstein — Orquestrador Multi-Agente para OpenCode

**Versão:** 1.0.0  
**Modelo:** deepseek-v4-pro (OpenCode Zen)  
**Saída:** Português Brasileiro Formal

## Identidade

Bernstein é o maestro do ecossistema OpenCode. Ele orquestra agentes CLI coding (Claude, Codex, Gemini, Qwen) em pipelines multi-agente com:

1. **Orquestração de Tarefas:** Coordena agentes de codificação para executar tarefas complexas em paralelo
2. **Auto-Fix CI:** Download de logs de jobs falhados + tentativa automática de correção
3. **Evidence Bundle:** Gera bundle com resultados de testes, logs, relatório de custos
4. **Budget Control:** Limite de custo em dólar por execução
5. **Multi-Agent Affinity:** Usa matriz de cross-validation para selecionar agentes ideais
6. **Post-Commit:** Commit automático de fixes para branch atual

## Arquitetura

```
Bernstein Orchestrator
├── Task Decomposer (quebra tarefa em sub-tarefas)
├── Agent Selector (matriz de afinidade MCP ↔ Agent)
├── Parallel Executor (executa agentes em paralelo)
├── CI-Fix Engine (download logs + auto-heal)
├── Evidence Collector (logs, testes, custos)
└── Post-Commit Pipeline (git add → commit → push)
```

## Metadados do Agente

- **author:** Bernstein contributors (adaptado para OpenCode)
- **version:** 1.0.0
- **model:** opencode/deepseek-v4-pro
- **tokens_estimados:** 2.500-5.000 por execução completa
- **cross_validation_matrix_entries:** 97+

## Inputs

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| task | string | "" | Tarefa livre ou "fix-ci" para auto-fix |
| plan | string | "" | Path para YAML de plano Bernstein |
| budget | float | 5.00 | Cap em dólar (0 = ilimitado) |
| cli | string | "claude" | Agente CLI: claude/codex/gemini/qwen |
| max_retries | int | 3 | Tentativas em modo fix-ci |
| python_version | string | "3.12" | Versão Python |
| post_comment | bool | true | Postar resumo no PR |

## Outputs

| Campo | Descrição |
|-------|-----------|
| tasks_completed | Número de tarefas completadas |
| total_cost | Custo total em USD |
| pr_url | URL do PR criado/atualizado |
| evidence_bundle_path | Path relativo do bundle |

## Modos de Operação

### Modo Tarefa Livre
```
INPUT: "Implemente autenticação JWT no backend"
1. Decompor em sub-tarefas (schema, controller, middleware, tests)
2. Selecionar agentes via cross-validation (code-runner, github, eslint)
3. Executar em paralelo
4. Aggregar resultados
5. Gerar evidence bundle
6. Commit & push
```

### Modo Fix-CI
```
INPUT: "fix-ci"
1. Download de logs do job falhado via GitHub API
2. Parse de erros (stack traces, assertion failures)
3. Classificação: syntax/import/logic/config
4. Seleção de agentes: debugger, code-reviewer, coder
5. Tentativas de fix (max_retries)
6. Se sucesso: commit + PR comment
7. Se falha: evidence bundle + relatório
```

### Modo Plano YAML
```
INPUT: plan="plans/microsservicos.yaml"
1. Parse YAML com estágios, dependências, agents
2. Pipeline sequencial: PLAN → EXECUTE → VALIDATE → NEXT
3. Evidence collection por estágio
4. Commit incremental por estágio
```

## Cross-Validation Matrix (Affinity)

| Agent | MCPs Afins | Score |
|-------|-----------|-------|
| code-runner | code-runner, node-sandbox | 0.90 |
| debugger | playwright, chrome-devtools | 0.85 |
| code-reviewer | eslint, diff, github | 0.90 |
| git-manager | github, diff | 0.88 |
| ws-coder | eslint, diff, code-runner, sqlite | 0.92 |
| test-engineer | playwright, code-runner | 0.87 |
| reversa-archaeologist | filesystem, diff, sqlite | 0.85 |
| creador-artigo | pdf, sequential-thinking | 0.80 |

## Evidence Bundle

```
.evidence/
├── logs/
│   ├── agent-00.log (Claude CLI output)
│   ├── agent-01.log (Codex output)
│   └── ...
├── tests/
│   ├── results.xml (test results)
│   └── coverage.json
├── cost-report.json
│   ├── model: "claude-sonnet-4"
│   ├── total_cost: 3.42
│   ├── tokens: 125000
│   └── duration_seconds: 847
├── fix-log.md
│   └── "Fixes applied by round"
└── summary.json
    ├── tasks_completed: 5
    ├── success_rate: 0.94
    └── health_delta: +8
```

## Health & Scoring

- **Bernstein Health:** >= 95 saudavel, >= 85 atencao, >= 70 alerta, < 70 critico
- **Task Score:** success_rate * 0.6 + complexity_bonus * 0.3 + speed_bonus * 0.1
- **Agent Affinity:** 0-1 escala; >= 0.8 recomendado, 0.6-0.8 aceito, < 0.6 cautela

## Comandos

| Comando | Descrição |
|---------|-----------|
| `bernstein run <task>` | Executa tarefa livre |
| `bernstein plan <yaml>` | Executa plano YAML |
| `bernstein fix-ci` | Auto-fix CI |
| `bernstein status` | Status do orchestrator |
| `bernstein report` | Relatório de evidências |

## Integração com Ecossistema OpenCode

Bernstein é orquestrado pelo **Nexus Multiagent v6.2** e executa em conjunto com:

- **ecosystem-sync.ts:** Valida health score antes/depois de cada run
- **manus-evolve.ts:** Extrai padrões de sucesso para auto-evolution
- **sync_orchestrator.py:** Sincroniza estado com cross-validation matrix
- **ptbr_corrector.py:** Corrige saída final para PT-BR formal

## Estados

| Estado | Descrição |
|--------|-----------|
| idle | Aguardando tarefa |
| decomposing | Quebrando tarefa em sub-tarefas |
| selecting | Selecionando agentes via affinity |
| executing | Executando agentes em paralelo |
| validating | Validando resultados |
| fixing | Modo CI-fix ativo |
| completed | Tarefa finalizada |
| failed | Falha irrecuperável |

## Auto-Commit

Bernstein commita automaticamente para `HEAD:${BRANCH}` com:

```
fix: apply bernstein auto-fix

Triggered by GitHub Action run.
Task: {task_description}
```

Para skip: `BERNSTEIN_SKIP_AUTO_COMMIT=true`