# SPEC_EVO14_ENG_codereviewer — CodeReviewer Skill

## Metadata
- **Evolução**: Round 14 (Agency Engineering)
- **Fonte**: agency-agents/engineering/engineering-code-reviewer.md
- **Categoria**: agency/engineering
- **Versão**: 1.0.0

## Descricao
Motor de revisao de codigo baseado em regras. Analisa codigo-fonte em texto para detectar code smells, violacoes de complexidade, padroes inseguros e problemas de estilo estrutural. Opera offline com stdlib Python 3.12.

## CTs (Criterios de Aceitacao)

### CT-01: Deteccao de Complexidade Ciclomatica
- **Dado**: funcao com N branches (if/for/while/except)
- **Quando**: `engine.analyze_complexity(source_code)` e chamado
- **Entao**: retorna `CyclomaticComplexity` com `score > 0` e `violations` listando funcoes com score > 10

### CT-02: Deteccao de Code Smells
- **Dado**: codigo com god-function (>50 linhas), parametros excessivos (>5), nomes curtos (<3 chars)
- **Quando**: `engine.detect_smells(source_code)` e chamado
- **Entao**: retorna `SmellReport` com `smells` contendo entradas para cada categoria detectada

### CT-03: Deteccao de Padroes Inseguros
- **Dado**: codigo com `eval()`, `exec()`, `os.system()`, hardcoded secrets
- **Quando**: `engine.detect_security_issues(source_code)` e chamado
- **Entao**: retorna `SecurityIssues` com `issues` listando cada ocorrencia com `line`, `pattern`, `severity`

### CT-04: Analise de Duplicacao
- **Dado**: codigo com blocos repetidos (>= 5 linhas identicas)
- **Quando**: `engine.detect_duplication(source_code)` e chamado
- **Entao**: retorna `DuplicationReport` com `duplicates` contendo pares de intervalos de linha e similaridade

## API Contract

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CyclomaticComplexity:
    total_score: int
    violations: list[dict]  # [{name, line, score, threshold}]
    available: bool = True

@dataclass
class SmellReport:
    smells: list[dict]  # [{type, name, line, message}]
    count: int
    available: bool = True

@dataclass
class SecurityIssues:
    issues: list[dict]  # [{line, pattern, severity, snippet}]
    critical_count: int
    available: bool = True

@dataclass
class DuplicationReport:
    duplicates: list[dict]  # [{block_a, block_b, similarity, lines}]
    duplicated_line_count: int
    available: bool = True

class CodeReviewer:
    @property
    def available(self) -> bool: ...

    def analyze_complexity(self, source: str) -> CyclomaticComplexity: ...
    def detect_smells(self, source: str) -> SmellReport: ...
    def detect_security_issues(self, source: str) -> SecurityIssues: ...
    def detect_duplication(self, source: str) -> DuplicationReport: ...
```
