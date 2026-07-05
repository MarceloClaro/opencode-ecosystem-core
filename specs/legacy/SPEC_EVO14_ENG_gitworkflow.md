# SPEC_EVO14_ENG_gitworkflow — GitWorkflowMaster Skill

## Metadata
- **Evolucao**: Round 14 (Agency Engineering)
- **Fonte**: agency-agents/engineering/engineering-git-workflow-master.md
- **Categoria**: agency/engineering
- **Versao**: 1.0.0

## Descricao
Motor de validacao de fluxo de trabalho Git. Analisa nomes de branches, mensagens de commit (Conventional Commits), estrategias de merge e atomicidade de commits. Opera offline com stdlib Python 3.12.

## CTs (Criterios de Aceitacao)

### CT-01: Validacao de Nome de Branch
- **Dado**: nome de branch como `feat/SCRUM-123-add-login`
- **Quando**: `engine.validate_branch_name(branch_name)` e chamado
- **Entao**: retorna `BranchValidation` com `valid=True`, `category="feat"`, `ticket="SCRUM-123"`

### CT-02: Validacao de Conventional Commits
- **Dado**: mensagem `fix(auth): resolve token expiry on refresh`
- **Quando**: `engine.validate_commit_message(message)` e chamado
- **Entao**: retorna `CommitValidation` com `valid=True`, `type="fix"`, `scope="auth"`, `breaking=False`

### CT-03: Deteccao de Commits Nao-Atomicos
- **Dado**: 5 commits onde 3 tocam multiplos dominios (>3 arquivos em modulos distintos)
- **Quando**: `engine.detect_non_atomic(commits)` e chamado
- **Entao**: retorna `AtomicityReport` com `non_atomic` contendo commits suspeitos e `score` (0-1)

### CT-04: Analise de Estrategia de Merge
- **Dado**: historico com merge commits e fast-forwards
- **Quando**: `engine.analyze_merge_strategy(git_log)` e chamado
- **Entao**: retorna `MergeStrategyReport` com `strategy_detected`, `recommendation` e `issues`

## API Contract

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BranchValidation:
    valid: bool
    category: str  # feat, fix, chore, docs, refactor, test, etc.
    ticket: str
    errors: list[str]
    available: bool = True

@dataclass
class CommitValidation:
    valid: bool
    type: str
    scope: str
    breaking: bool
    description: str
    errors: list[str]
    available: bool = True

@dataclass
class AtomicityReport:
    non_atomic: list[dict]  # [{hash, files_count, domains, reason}]
    score: float  # 0.0-1.0, 1.0 = all atomic
    available: bool = True

@dataclass
class MergeStrategyReport:
    strategy_detected: str  # merge, squash, rebase, mixed
    recommendation: str
    issues: list[str]
    available: bool = True

class GitWorkflowEngine:
    @property
    def available(self) -> bool: ...

    def validate_branch_name(self, branch_name: str) -> BranchValidation: ...
    def validate_commit_message(self, message: str) -> CommitValidation: ...
    def detect_non_atomic(self, commits: list[dict]) -> AtomicityReport: ...
    def analyze_merge_strategy(self, git_log: str) -> MergeStrategyReport: ...
```
