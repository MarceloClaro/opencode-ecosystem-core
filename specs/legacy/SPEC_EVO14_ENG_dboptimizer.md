# SPEC_EVO14_ENG_dboptimizer — DatabaseOptimizer Skill

## Metadata
- **Evolucao**: Round 14 (Agency Engineering)
- **Fonte**: agency-agents/engineering/engineering-database-optimizer.md
- **Categoria**: agency/engineering
- **Versao**: 1.0.0

## Descricao
Motor de analise e otimizacao de banco de dados. Analisa schemas SQL, consultas e indices para detectar oportunidades de otimizacao, indices faltantes, problemas de normalizacao e anti-padroes de query. Opera offline com stdlib Python 3.12.

## CTs (Criterios de Aceitacao)

### CT-01: Analise de Schema
- **Dado**: CREATE TABLE statements com colunas sem indices, tipos subotimos (VARCHAR sem limite, TEXT para campos pequenos)
- **Quando**: `engine.analyze_schema(ddl_text)` e chamado
- **Entao**: retorna `SchemaAnalysis` com `tables`, `missing_indexes`, `type_warnings` e `score`

### CT-02: Deteccao de Queries N+1
- **Dado**: codigo com loop executando query dentro de iteracao
- **Quando**: `engine.detect_n_plus_one(source_code)` e chamado
- **Entao**: retorna `NPlusOneReport` com `occurrences` e `suggestions` para eager loading/batch

### CT-03: Sugestao de Indices Faltantes
- **Dado**: queries com WHERE/JOIN/ORDER BY em colunas sem indices declarados
- **Quando**: `engine.suggest_indexes(ddl_text, queries)` e chamado
- **Entao**: retorna `IndexSuggestions` com `suggestions` no formato `CREATE INDEX ... ON table(column)`

### CT-04: Deteccao de Anti-Padroes SQL
- **Dado**: queries com `SELECT *`, `%LIKE%` sem indice, funcoes em WHERE, cartesian joins
- **Quando**: `engine.detect_antipatterns(query_text)` e chamado
- **Entao**: retorna `AntipatternReport` com `antipatterns` e `severity` para cada um

## API Contract

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SchemaAnalysis:
    tables: list[dict]  # [{name, columns, indexes, warnings}]
    missing_indexes: list[str]  # sugestoes CREATE INDEX
    type_warnings: list[dict]
    score: int  # 0-100
    available: bool = True

@dataclass
class NPlusOneReport:
    occurrences: list[dict]  # [{line, loop_type, query, suggestion}]
    count: int
    available: bool = True

@dataclass
class IndexSuggestions:
    suggestions: list[dict]  # [{table, columns, ddl, reason}]
    count: int
    available: bool = True

@dataclass
class AntipatternReport:
    antipatterns: list[dict]  # [{line, pattern, severity, fix}]
    count: int
    available: bool = True

class DatabaseOptimizer:
    @property
    def available(self) -> bool: ...

    def analyze_schema(self, ddl_text: str) -> SchemaAnalysis: ...
    def detect_n_plus_one(self, source_code: str) -> NPlusOneReport: ...
    def suggest_indexes(self, ddl_text: str, queries: list[str]) -> IndexSuggestions: ...
    def detect_antipatterns(self, query_text: str) -> AntipatternReport: ...
```
