# SPEC-093: Refined Dependency Graph

## 1. Visão Geral
**Objetivo:** Estabelecer um grafo de dependências canônico, formal e verificável para todo o ecossistema, eliminando dependências circulares, duplicatas e acoplamentos ilegítimos, e integrando a verificação ao pipeline CI/CD.

**Motivação:** O diagnóstico revelou duplicatas (`evolution_loop.py`/`nexus_evolution_loop.py`, `self_healer.py`/`nexus_self_healer.py`), auto-import circular (`epistemic_injector.py`), e acoplamento direto em 85% dos módulos.

## 2. Arquitetura

### 2.1 Dependency Graph Canonical

```
ecosystem/deps/
├── __init__.py
├── analyzer.py              # Analisador de dependências Python
├── graph.py                 # Grafo canônico (networkx-like)
├── constraints.py           # Regras e constraints de dependência
├── validator.py             # Validador contra regras
├── visualizer.py            # Export para DOT/Mermaid
├── rules.yaml               # Regras de dependência declarativas
└── canonical_graph.json     # Grafo canônico serializado
```

### 2.2 Regras de Dependência (layers)

```
Layer 6: ecosystem/commands/     → Pode importar: adapters, contracts, schemas
Layer 5: ecosystem/adapters/     → Pode importar: contracts, schemas
Layer 4: ecosystem/schemas/      → Pode importar: contracts
Layer 3: ecosystem/contracts/    → Pode importar: (stdlib only)
Layer 2: ecosystem/deps/         → Pode importar: (stdlib only)
Layer 1: core/                   → Pode importar: contracts (futuro)
Layer 0: skills/, nexus/, etc.   → Deve importar via adapters/contracts
```

**Regra fundamental:** Módulos de camada superior podem importar de camadas inferiores. NUNCA o contrário. NUNCA imports circulares.

### 2.3 Dependency Analyzer

```python
# ecosystem/deps/analyzer.py

@dataclass
class Dependency:
    source: str          # Módulo origem
    target: str          # Módulo destino
    type: Literal["import", "adapter", "contract", "data"]
    line: int            # Linha onde ocorre

@dataclass
class Violation:
    source: str
    target: str
    rule: str            # Regra violada
    severity: Literal["error", "warning", "info"]
    fix: str | None      # Sugestão de correção

class DependencyAnalyzer:
    """Analisa e valida dependências do ecossistema."""
    
    def analyze_directory(self, path: str) -> list[Dependency]: ...
    def detect_circular(self) -> list[list[str]]: ...
    def find_duplicates(self) -> list[tuple[str, str]]: ...
    def validate_rules(self, deps: list[Dependency]) -> list[Violation]: ...
    def build_graph(self) -> dict: ...  # Para export
    def suggest_contract(self, dep: Dependency) -> str | None: ...
```

### 2.4 Duplicate Resolution Plan

| Duplicata | Ação | Canônico | Redirecionamento |
|-----------|------|----------|-----------------|
| `nexus/evolution_loop.py` ↔ `nexus/nexus_evolution_loop.py` | Remover duplicata | `nexus/evolution_loop.py` | `nexus_evolution_loop.py` → import re-export |
| `nexus/self_healer.py` ↔ `nexus/nexus_self_healer.py` | Mesclar + manutenção | `nexus/self_healer.py` | `nexus_self_healer.py` → import re-export |
| `criador-artigo/correction_loop.py` ↔ `criador-artigo/banca/iterative_correction_loop.py` | Refatorar para 1 canônico | `criador-artigo/correction_loop.py` | `banca/iterative_correction_loop.py` → adapter |

## 3. Requisitos TDD

| CT ID | Descrição | Critério |
|-------|-----------|----------|
| CT-9301 | DependencyAnalyzer analisa diretório | Retorna lista de Dependency |
| CT-9302 | Detecção de dependência circular | `detect_circular()` encontra ciclo |
| CT-9303 | Detecção de duplicatas | `find_duplicates()` encontra arquivos iguais |
| CT-9304 | Validação de regras de camada | `validate_rules()` reporta violações |
| CT-9305 | Construção de grafo canônico | `build_graph()` retorna dict com nós/arestas |
| CT-9306 | Sugestão de contrato para acoplamento direto | `suggest_contract()` retorna nome de interface |
| CT-9307 | Grafo canônico serializado em JSON | `canonical_graph.json` tem estrutura válida |
| CT-9308 | Rules YAML carregável e validável | `rules.yaml` é sintaticamente correto |
| CT-9309 | Visualizador gera saída Mermaid | `visualize_mermaid()` retorna string válida |
| CT-9310 | Validação integrada ao CI | `validate_all()` retorna 0 violações críticas |

## 4. Métricas de Sucesso
- **Zero dependências circulares**
- **Zero duplicatas funcionais**
- **100% dos módulos na camada correta**
- **CI bloqueia PRs com violações de dependência**

## 5. ADRs

### ADR-architectu-093-1: Análise Estática vs Runtime
**Decisão:** Usar análise estática (AST) em vez de runtime para detectar dependências. Motivo: não requer execução do código, detecta imports em tempo zero, cobre 100% dos arquivos.

### ADR-architectu-093-2: Grafo Canônico Versionado
**Decisão:** O `canonical_graph.json` é versionado no git e atualizado a cada ciclo evolutivo. Motivo: permite diff entre versões, auditoria histórica, e baseline para validação.
