# SPEC-AGE-008: GitWorkflowEngine
Version: 1.0.0 | Status: verified | TDD: verified | Domain: engineering

## Objective
Motor de validacao de fluxo Git. Validar nomes de branches, mensagens de commit (Conventional Commits), atomicidade de commits e estrategias de merge. Opera offline com Python 3.12 stdlib.

## Acceptance Criteria
- [x] CT-1: `test_ct01_branch_name_validation` — Valida `feat/SCRUM-123-add-login` (categoria feat, ticket SCRUM-123); rejeita sem categoria e sem ticket
- [x] CT-2: `test_ct02_commit_message_validation` — Valida `fix(auth): resolve token expiry`; detecta breaking change `!`; rejeita mensagem nao-Conventional
- [x] CT-3: `test_ct03_non_atomic_commits` — detect_non_atomic flagga commits com >5 arquivos multi-dominio; atomicos tem score=1.0
- [x] CT-4: `test_ct04_merge_strategy_analysis` — analyze_merge_strategy detecta `merge`, `squash`, `rebase_or_fast_forward` com recomendacao

## Engine
<scripts/gitworkflow_engine.py> -> GitWorkflowEngine

## Test Results
All CTs PASSED
