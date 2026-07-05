# SPEC-029: TELEOLOGICAL REVERSE SCANNER — Scanner Teleológico Reverso

**Versão:** 1.0.0  
**Data:** 2026-06-08  
**Status:** Em implementação  
**Dependências:** SPEC-028 (NoologicalScanner v3.0), academic-audit

---

## 1. Conceito

O **Scanner Teleológico Reverso** complementa o NoologicalScanner com uma camada prescritiva: enquanto o scanner original identifica **o que está presente** no espaço de conhecimento (descritivo), o teleológico infere **o que deveria estar presente** dados os objetivos da pesquisa (normativo).

### Princípio Teleológico

> "Se o objetivo da pesquisa é X, então por necessidade lógica as dimensões epistemológicas A, B, C devem estar cobertas. Se não estão, há um gap teleológico."

### Por que "Reverso"?

O scanner tradicional parte do corpus → detecta presenças/ausências. O teleológico parte dos **objetivos/finalidades** → infere requisitos → compara com o scan existente. A direção da inferência é invertida: vai do telos (fim) para os meios (dimensões), e não dos meios para os fins.

---

## 2. Arquitetura

```
Research Goals (input)
    │
    ▼
TELEOLOGICAL_MAPPINGS (goal_type → required_dimensions)
    │
    ▼
TeleologicalReverseScanner
    │
    ├── map_goals_to_dimensions(goals) → required dims with weights
    ├── compare_with_scan(noological_scan, required_dims) → gaps
    ├── gap_severity(gap, goal_weight) → critical/high/moderate/low
    ├── generate_teleological_report() → markdown
    └── teleological_score() → 0.0–1.0 completeness
```

### Integração com NoologicalScanner

```
NoologicalScanner.scan(corpus)  ──→  scan_results (o que EXISTE)
                                         │
TeleologicalReverseScanner              │
  .set_goals(questions)                 │
  .compare_with(scan_results)  ────────┘
  .report()  ──→  gaps entre o requerido e o existente
```

---

## 3. Tipos de Objetivo de Pesquisa (Goal Types)

| Goal Type | Descrição | Exemplos de Questões |
|-----------|-----------|---------------------|
| `causal` | Estabelecer relações de causa-efeito | "Qual o efeito de X sobre Y?" |
| `evaluative` | Avaliar eficácia/efetividade de intervenções | "A intervenção Z funciona?" |
| `exploratory` | Explorar fenômenos pouco compreendidos | "Como os participantes experienciam X?" |
| `strategic` | Modelar decisões e interações estratégicas | "Qual a estratégia ótima em contexto Y?" |
| `comparative` | Comparar grupos, culturas ou contextos | "Como X difere entre grupos A e B?" |
| `predictive` | Prever outcomes futuros | "Quais fatores predizem Y em 5 anos?" |
| `integrative` | Sintetizar conhecimento de múltiplos domínios | "Como A, B e C se articulam?" |
| `critical` | Questionar/transformar estruturas existentes | "Quais relações de poder sustentam X?" |

---

## 4. Mapeamento Teleológico (Goal → Required Dimensions)

| Goal Type | Dimensões Requeridas (peso 1.0 = essencial, 0.5 = desejável) |
|-----------|---------------------------------------------------------------|
| **causal** | `metodos.experimental`(1.0), `temporalidade.longitudinal`(0.8), `raciocinio.probabilistico`(0.7), `raciocinio.contrafactual`(0.6), `dados.longitudinais`(0.7) |
| **evaluative** | `metodos.misto`(1.0), `metodos.revisao_sistematica`(0.6), `paradigmas.pragmatista`(0.8), `populacao.contexto_clinico`(0.7), `dados.clinicos`(0.8) |
| **exploratory** | `paradigmas.fenomenologico`(1.0), `paradigmas.construtivista`(0.8), `metodos.qualitativo`(1.0), `dados.qualitativos`(1.0), `raciocinio.abdutivo`(0.6), `raciocinio.indutivo`(0.5) |
| **strategic** | `teoria_jogos.*`(1.0), `raciocinio.contrafactual`(0.8), `raciocinio.probabilistico`(0.7), `niveis_analise.sistemico`(0.6), `raciocinio.teleologico`(0.5) |
| **comparative** | `populacao.cross_cultural`(1.0), `dados.comparativos`(1.0), `dominios.multiplos`(0.7), `metodos.misto`(0.6), `temporalidade.transversal`(0.5) |
| **predictive** | `temporalidade.prospectivo`(1.0), `dados.longitudinais`(1.0), `raciocinio.probabilistico`(0.9), `metodos.correlacional`(0.7), `dados.epidemiologicos`(0.6) |
| **integrative** | `dominios.*`(1.0), `paradigmas.complexo`(0.8), `metodos.revisao_sistematica`(0.7), `raciocinio.sistemico`(0.7), `teoria_jogos.cooperativo`(0.5) |
| **critical** | `paradigmas.critico`(1.0), `paradigmas.pos_estruturalista`(0.8), `niveis_analise.sistemico`(0.7), `populacao.diversidade`(0.6), `dominios.sociologia`(0.6) |

### Categorias Específicas por Goal Type (keyword matching)

Cada goal type mapeia para categorias **específicas** dentro das 10 dimensões. O peso reflete quão crítica a categoria é para o objetivo.

---

## 5. Classes (SDD)

### 5.1 `TeleologicalGoal`

```python
@dataclass
class TeleologicalGoal:
    description: str          # "Avaliar eficácia da TCC para depressão em adolescentes"
    goal_type: str            # "evaluative"
    weight: float = 1.0       # peso relativo (múltiplos objetivos)
```

### 5.2 `DimensionRequirement`

```python
@dataclass
class DimensionRequirement:
    dim_key: str              # "metodos"
    category: str             # "Misto sequencial"
    weight: float             # 0.0–1.0 (quão essencial)
    rationale: str            # "Métodos mistos são necessários para avaliar eficácia"
```

### 5.3 `TeleologicalGap`

```python
@dataclass  
class TeleologicalGap:
    goal: str                 # objetivo que gerou o gap
    dim_key: str              # dimensão com gap
    category: str             # categoria requerida mas ausente
    required_weight: float    # peso da exigência teleológica
    severity: str             # "critical" | "high" | "moderate" | "low"
    rationale: str            # justificativa
```

### 5.4 `TeleologicalReverseScanner`

```python
class TeleologicalReverseScanner:
    def set_goals(goals: list[TeleologicalGoal]) -> None
    def infer_requirements() -> list[DimensionRequirement]
    def compare_with_scan(noological_results: dict) -> list[TeleologicalGap]
    def teleological_score() -> float  # 0.0–1.0
    def generate_report() -> str       # markdown
```

---

## 6. Testes (TDD)

> Suite: `specs/test_teleological_scanner.py`

### CT-TEL-001: Goal types carregam mapeamentos
- **Dado:** `TeleologicalReverseScanner` com goal_type="causal"
- **Quando:** `infer_requirements()`
- **Então:** requisitos incluem `metodos.experimental` (peso >= 0.8), `temporalidade.longitudinal`

### CT-TEL-002: Exploratory goal exige métodos qualitativos
- **Dado:** goal_type="exploratory"
- **Quando:** `infer_requirements()`
- **Então:** `metodos.qualitativo` com peso 1.0, `paradigmas.fenomenologico` com peso 1.0

### CT-TEL-003: Strategic goal exige teoria dos jogos
- **Dado:** goal_type="strategic"
- **Quando:** `infer_requirements()`
- **Então:** `teoria_jogos.*` com peso 1.0 (todas as categorias de teoria dos jogos)

### CT-TEL-004: Múltiplos objetivos agregam requisitos
- **Dado:** goals = [causal, comparative]
- **Quando:** `infer_requirements()`
- **Então:** requisitos incluem ambas as dimensões, sem duplicatas

### CT-TEL-005: compare_with_scan detecta gap crítico
- **Dado:** scan com 0% em `teoria_jogos`, goal="strategic"
- **Quando:** `compare_with_scan(scan, requirements)`
- **Então:** gap com severity="critical", dim_key="teoria_jogos"

### CT-TEL-006: compare_with_scan não reporta gap quando coberto
- **Dado:** scan com `metodos.experimental` presente, goal="causal"
- **Quando:** `compare_with_scan(scan, requirements)`
- **Então:** `metodos.experimental` NÃO aparece nos gaps

### CT-TEL-007: teleological_score 0% para scan vazio
- **Dado:** scan vazio (0% coverage), goal qualquer
- **Quando:** `teleological_score()`
- **Então:** score = 0.0

### CT-TEL-008: teleological_score 100% para scan completo
- **Dado:** scan com todas as categorias requeridas, goal qualquer
- **Quando:** `teleological_score()`
- **Então:** score = 1.0

### CT-TEL-009: Gap severity proporcional ao peso
- **Dado:** gap com required_weight=1.0 vs 0.3
- **Quando:** classificação de severity
- **Então:** 1.0 → "critical", 0.3 → "low"

### CT-TEL-010: Report markdown contém seções obrigatórias
- **Dado:** scanner com goals e scan
- **Quando:** `generate_report()`
- **Então:** contém "Objetivos", "Requisitos Teleológicos", "Gaps", "Score"

### CT-TEL-011: Goal type desconhecido gera warning
- **Dado:** goal_type="inexistente"
- **Quando:** `set_goals([TeleologicalGoal("teste", "inexistente")])`
- **Então:** não quebra; retorna lista vazia de requisitos

### CT-TEL-012: Integração com NoologicalScanner real
- **Dado:** corpus + NoologicalScanner.scan() + TeleologicalReverseScanner
- **Quando:** pipeline completo
- **Então:** teleological_score calculado, gaps identificados

---

## 7. Métricas

| Métrica | Meta |
|---------|------|
| Goal types mapeados | 8/8 (causal, evaluative, exploratory, strategic, comparative, predictive, integrative, critical) |
| CTs TDD | 12/12 PASS |
| Integração com NoologicalScanner | Pipeline completo funcional |
| Teleological score | 0.0–1.0 contínuo |
