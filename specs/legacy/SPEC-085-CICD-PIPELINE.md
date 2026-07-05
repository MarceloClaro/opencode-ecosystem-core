# SPEC-085: CI/CD Pipeline — GitHub Actions + Pre-Commit Validation

| Campo | Valor |
|-------|------|
| **SPEC ID** | SPEC-085 |
| **Ciclo** | R42 |
| **Status** | `active` |
| **Prioridade** | Alta |
| **Dependências** | SPEC-083 (Self-Repair), SPEC-084 (Health Monitor), `tests/ci_validate.py`, `hooks/cora_eval_integration.py` |
| **Suítes TDD** | `tests/test_r42_cicd_pipeline.py` |
| **Componentes** | `.github/workflows/ecosystem-ci.yml`, `.github/workflows/cora-eval-nightly.yml`, `hooks/pre-commit`, `tests/ci_validate.py` |

---

## 1. Problema

O ecossistema OpenCode possui **443 CTs** distribuídos em múltiplas suítes de teste, porém:

| Problema | Impacto |
|:---------|:--------|
| Sem GitHub Actions | Nenhuma validação automática em push/PR |
| `ci_validate.py` desatualizado | Não cobre R41 (Health Background) |
| Pre-commit hook apenas CORA-Eval | R39/R41 podem ser pulados |
| Sem matrix de teste | Único ambiente Python, sem cobertura multiplataforma |
| Sem badge de status | Sem visibilidade externa da saúde do projeto |

## 2. Solução

Implementar pipeline CI/CD com 3 gateways:

```
┌──────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                              │
├──────────────────────────────────────────────────────────────┤
│  Push/PR to main                                              │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────┐     ┌──────────────────┐                │
│  │ ecosystem-ci.yml │     │ cora-eval-       │                │
│  │ (rápido, <5min)  │     │ nightly.yml      │                │
│  │                  │     │ (completo, <15m)  │                │
│  ├─────────────────┤     ├──────────────────┤                │
│  │ 1. Setup Python │     │ 1. Matrix D1-D26  │                │
│  │ 2. Cache pip    │     │ 2. Testes por     │                │
│  │ 3. Testes core  │     │    domínio        │                │
│  │ 4. ci_validate  │     │ 3. Relatório      │                │
│  │ 5. Badge/status │     │ 4. Artefato .md   │                │
│  └─────────────────┘     └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
         │                            │
         ▼                            ▼
┌──────────────────┐      ┌──────────────────────┐
│ PRE-COMMIT HOOK  │      │ RELATÓRIO SEMANAL     │
│ (local, rápido)  │      │ (cron, análise lenta) │
│ R39+R41+R42      │      │ tendências + gaps     │
└──────────────────┘      └──────────────────────┘
```

### 2.1 Gateway 1 — GitHub Actions (`ecosystem-ci.yml`)

Executado em **push e pull request para main**:

| Passo | Ação | Tempo Esperado |
|:------|:-----|:--------------:|
| 1 | `actions/checkout@v4` | ~2s |
| 2 | `actions/setup-python@v5` (3.12) | ~10s |
| 3 | Cache pip (`requirements.txt` ou `pip list`) | ~5s |
| 4 | `pip install pytest numpy scipy` | ~30s |
| 5 | `python -m pytest tests/test_r*_*.py -v --tb=short` | ~120s |
| 6 | `python tests/ci_validate.py --no-diversity` | ~30s |
| 7 | Badge generation (JSON) | ~5s |

**Falha**: qualquer passo falha → workflow vermelho.

### 2.2 Gateway 2 — GitHub Actions (`cora-eval-nightly.yml`)

Executado em **agendamento (cron)** ou **manual dispatch**:

- Matrix de domínios D1-D26
- Relatório markdown como artefato
- Cache de dependências entre execuções

### 2.3 Gateway 3 — Pre-Commit Hook (local)

Atualizado para incluir **todas as suítes de teste de ciclo** (R31 a R41):

```bash
pytest tests/test_r*_*.py -q --tb=short --no-header
python tests/ci_validate.py --no-diversity
```

### 2.4 Atualização do `ci_validate.py`

Adicionar verificações para:

| Módulo | Verificação |
|:-------|:------------|
| R39 Self-Repair | 14 CTs registrados |
| R41 Health Background | 23 CTs registrados |
| R42 CI/CD | 12 CTs registrados |
| health_history.jsonl | Arquivo existe |
| HealthBackgroundService | Pode ser importado |
| WebhookConfig | Dataclass funcional |

## 3. Arquivos do Pipeline

```
.github/workflows/
├── ecosystem-ci.yml          # CI principal (push/PR)
└── cora-eval-nightly.yml     # CORA-Eval completo (cron)

hooks/
├── pre-commit-cora-eval.sh   # Hook existente (atualizado)
└── pre-commit               # Link simbólico ou fallback

tests/
├── ci_validate.py            # Script de validação (atualizado)
└── test_r42_cicd_pipeline.py # Testes do pipeline
```

## 4. CTs (12 Testes)

### 4.1 GitHub Actions Workflow (4 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-01 | `test_ecosystem_ci_yml_exists` | `.github/workflows/ecosystem-ci.yml` existe |
| CT-02 | `test_ecosystem_ci_yml_syntax` | YAML do workflow é sintaticamente válido |
| CT-03 | `test_cora_eval_nightly_exists` | `.github/workflows/cora-eval-nightly.yml` existe |
| CT-04 | `test_cora_eval_nightly_cron` | Workflow tem cron schedule definido |

### 4.2 Pre-Commit Hook (2 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-05 | `test_pre_commit_exists` | `hooks/pre-commit-cora-eval.sh` existe e é executável |
| CT-06 | `test_pre_commit_includes_r41` | Script menciona test_r41 ou padrão r* |

### 4.3 ci_validate.py (4 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-07 | `test_ci_validate_imports` | `ci_validate.py` pode ser importado sem erros |
| CT-08 | `test_ci_validate_r39_registered` | R39 CTs (14) estão registrados |
| CT-09 | `test_ci_validate_r41_registered` | R41 CTs (23) estão registrados |
| CT-10 | `test_ci_validate_health_background_import` | HealthBackgroundService importável |

### 4.4 Integração (2 CTs)

| CT | Nome | Descrição |
|:--:|:-----|:----------|
| CT-11 | `test_all_test_files_exist` | Todos os `test_r*_*.py` referenciados existem |
| CT-12 | `test_total_cts_match` | Soma dos CTs por suite coincide com `ecosystem-state.json` |

## 5. Critérios de Aceitação

1. Todos os 12 CTs passam (`pytest tests/test_r42_cicd_pipeline.py -v`)
2. `.github/workflows/ecosystem-ci.yml` é YAML válido
3. `ci_validate.py` reconhece R39 (14) e R41 (23) CTs
4. Pre-commit hook executa todas as suites `test_r*_*.py`
5. Workflows podem ser acionados manualmente (workflow_dispatch)
6. ecossistema-state.json v6.9.0 com R42=100

## 6. KPIs

| Métrica | Antes (R41) | Depois (R42) |
|:--------|:-----------:|:-------------:|
| GitHub Actions | 0 workflows | 2 workflows |
| Cobertura CI | Manual | Automática (push/PR) |
| Pre-commit coverage | Apenas CORA-Eval | Ciclos R31-R41 |
| CTs totais | 443 | 455 |
| ci_validate checks | 3 categorias | 5 categorias |

---

*Fim da SPEC-085*
