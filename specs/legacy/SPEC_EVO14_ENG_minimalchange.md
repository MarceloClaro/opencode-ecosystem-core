# SPEC_EVO14_ENG_minimalchange — MinimalChangeEngineer Skill

## Metadata
- **Evolucao**: Round 14 (Agency Engineering)
- **Fonte**: agency-agents/engineering/engineering-minimal-change-engineer.md
- **Categoria**: agency/engineering
- **Versao**: 1.0.0

## Descricao
Motor de validacao de diffs minimos. Analisa patches/diffs para detectar scope creep, mudancas desnecessarias, refatoracoes prematuras e alteracoes fora do escopo declarado. Opera offline com stdlib Python 3.12.

## CTs (Criterios de Aceitacao)

### CT-01: Deteccao de Mudancas Fora de Escopo
- **Dado**: diff com arquivos modificados e escopo declarado (ex: ["src/auth.py"])
- **Quando**: `engine.check_scope(diff_text, scope_files)` e chamado
- **Entao**: retorna `ScopeCheck` com `out_of_scope` listando arquivos nao declarados e `violation` = True se houver violacoes

### CT-02: Deteccao de Refatoracao Prematura
- **Dado**: diff que renomeia variaveis/funcoes alem do necessario para o bugfix
- **Quando**: `engine.detect_premature_refactor(diff_text)` e chamado
- **Entao**: retorna `RefactorDetection` com `suspicious_renames` e `risk_score` > 0

### CT-03: Medicao de Entropia do Diff
- **Dado**: diff com multiplos hunks
- **Quando**: `engine.measure_entropy(diff_text)` e chamado
- **Entao**: retorna `DiffEntropy` com `files_changed`, `hunks_count`, `lines_added`, `lines_removed` e `entropy_score` (0-100)

### CT-04: Validacao de Proporcao Mudanca/Fix
- **Dado**: diff onde 80% das alteracoes sao formatacao/estilo
- **Quando**: `engine.validate_change_ratio(diff_text)` e chamado
- **Entao**: retorna `ChangeRatio` com `functional_changes`, `cosmetic_changes`, `ratio` e `warning` se ratio < 0.3

## API Contract

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ScopeCheck:
    in_scope: list[str]
    out_of_scope: list[str]
    violation: bool
    available: bool = True

@dataclass
class RefactorDetection:
    suspicious_renames: list[dict]  # [{old_name, new_name, line, reason}]
    risk_score: int  # 0-100
    available: bool = True

@dataclass
class DiffEntropy:
    files_changed: int
    hunks_count: int
    lines_added: int
    lines_removed: int
    entropy_score: int  # 0-100, higher = more scattered
    available: bool = True

@dataclass
class ChangeRatio:
    functional_changes: int
    cosmetic_changes: int
    ratio: float  # functional / total
    warning: bool  # True se muito cosmetico
    available: bool = True

class MinimalChangeEngine:
    @property
    def available(self) -> bool: ...

    def check_scope(self, diff_text: str, scope_files: list[str]) -> ScopeCheck: ...
    def detect_premature_refactor(self, diff_text: str) -> RefactorDetection: ...
    def measure_entropy(self, diff_text: str) -> DiffEntropy: ...
    def validate_change_ratio(self, diff_text: str) -> ChangeRatio: ...
```
