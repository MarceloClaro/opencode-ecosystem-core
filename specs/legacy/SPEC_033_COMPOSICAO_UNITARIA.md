# SPEC-033: Composição Unitária do Conhecimento (Refinado)

**Status:** Implementado (Stage 1 + Stage 3 concluídos)
**Autor:** Marcelo Claro Laranjeira (2026)
**Data:** 2026-06-10
**CTs:** 13/13 PASS (SPEC-033) + 6/6 PASS (SPEC-035)
**Integração:** SPEC-028, SPEC-029, SPEC-030, SPEC-031, SPEC-032, SPEC-035

---

## 1. Problema

O pipeline evolutivo atual responde duas perguntas:

| Camada | Pergunta | SPEC |
|--------|----------|------|
| Scanner Teleológico | "O que precisará existir?" | 029 |
| Sequenciamento Evolutivo | "Em que ordem construir?" | 030 |

Mas não responde: **"Do que cada capacidade é feita?"**

Uma capacidade cognitiva não é um átomo indivisível. Ela é composta por insumos: conceitos, métodos, bases de conhecimento, ferramentas, domínios externos e critérios de validação. Sem essa decomposição, o MCSP (SPEC-032) minimiza |C| (número de capacidades), mas ignora que capacidades diferentes têm custos de construção radicalmente diferentes.

---

## 2. Conceito

**Composição Unitária do Conhecimento** é a camada que decompõe cada capacidade futura em seus insumos cognitivos fundamentais, transformando "capacidades abstratas" em "planos de construção concretos".

```
Estado Futuro
    ↓
[SPEC-029] Scanner Teleológico → Capacidades Requeridas
    ↓
[SPEC-033] COMPOSIÇÃO UNITÁRIA → Decomposição em Insumos   ← ESTA SPEC
    ↓
[SPEC-030] CrossValidationEngine → Grafo de Dependências (enriquecido)
    ↓
[SPEC-032] MCSP → Conjunto Mínimo (com custo de construção real)
    ↓
[SPEC-031] TimelineEstimator → Roadmap com insumos por fase
```

---

## 3. Refinamentos sobre a Proposta Original

### 3.1 Bootstrap — De onde vêm os insumos iniciais?

**Problema:** Não podemos curar manualmente composições para cada capacidade possível.

**Solução:** Extrair seed data de artefatos já existentes no ecossistema:

| Fonte | O que extrai | Quantidade estimada |
|-------|-------------|-------------------|
| 16 `evo-*.md` | Ferramentas, métodos, conceitos usados em ciclos reais | ~30 inputs |
| 31 `SKILL.md` | Skills como tools, dependências como conceitos | ~40 inputs |
| 64 `DEPENDENCY_RULES` | Relações requires/enables/co_occurs → conceitos subjacentes | ~20 inputs |
| 80 `POLYMATHIC_MAPPINGS` | Domínios externos + princípios transferíveis | ~25 inputs |

**Total estimado:** 50-80 insumos iniciais sem curadoria manual.

### 3.2 Dois Grafos Paralelos

Existem DOIS grafos que coexistem e se relacionam:

**Grafo A — Capacidades (existente, CrossValidationEngine):**
```
CapabilityNode → requires/enables/co_occurs → CapabilityNode
Ex: "raciocinio.Probabilistico" → requires → "raciocinio.Dedutivo"
```

**Grafo B — Insumos (novo, CapabilityComposer):**
```
CapabilityUnit → composed_of → CognitiveInput
CognitiveInput → shared_by → [CapabilityUnit, CapabilityUnit, ...]
```

**Interseção crítica:** um `CognitiveInput` do tipo `tool` PODE referenciar uma `CapabilityNode` existente. Exemplo: "Scanner Reverso" requer a ferramenta "NoologicalScanner" — que já é uma capability no grafo A. Isso cria uma ponte natural entre os dois grafos.

### 3.3 Integração com MCSP — Custo Real

O MCSP atual minimiza |C| (número de capacidades). Com composição unitária:

1. Cada capacidade tem `construction_cost` baseado em quantos inputs faltam
2. Inputs são **compartilhados** entre capacidades — construí-los uma vez reduz o custo de todas
3. A heurística gulosa prioriza `cascade_impact / construction_cost`

**Mudança no `CapabilitySet.cost`:**
```python
# Antes: cost = len(required)  # mera contagem
# Depois:
cost = sum(c.construction_cost for c in required)  # custo real
# com desconto para inputs compartilhados entre múltiplas capabilities
```

### 3.4 Critérios de Validação — 4 Níveis Testáveis

A proposta original mencionava "coerência das capacidades identificadas" como validação. Refinamos para 4 níveis operacionalizáveis via CTs:

| Nível | Nome | CT Associado | Exemplo |
|-------|------|-------------|---------|
| N1 | Sintático | Composição bem-formada (todos os campos preenchidos, referências válidas) | CT-COMP-001 |
| N2 | Semântico | Inputs são relevantes para o domínio (cross-check com DOMAIN_WEIGHTS) | CT-COMP-004 |
| N3 | Pragmático | A capability construída passa em seus próprios CTs | CT-COMP-007 |
| N4 | Evolutivo | Após X ciclos, a capability foi usada em produção | CT-COMP-008 |

Cada `CognitiveInput.validation` referencia um ou mais CT-IDs que, quando aprovados, comprovam a construção.

### 3.5 Motor de Inferência — 3 Estratégias em Cascata

Para uma capacidade nunca antes decomposta:

| Ordem | Estratégia | Custo | Confiabilidade |
|-------|-----------|-------|---------------|
| 1 | **Template por Categoria** — 10 templates predefinidos (um por dimensão do NoologicalScanner) | O(1) | Média |
| 2 | **Analogia Polimática** — `PolymathicConvergence.find_analogies()` existente | O(n) | Alta |
| 3 | **Decomposição Generativa** — LLM com prompt estruturado (futuro) | Alta | Baixa (requer validação) |
| Fallback | **Frontier** — `construction_cost=1.0`, `frontier=True`, requer decomposição manual | O(1) | N/A |

### 3.6 Casos de Borda

| Caso | Comportamento |
|------|--------------|
| Capacidade sem composição conhecida | `frontier=True`, `construction_cost=1.0` |
| Input não existe na biblioteca | Adicionado como `maturity="emerging"`, `source="inferred"` |
| Dependência circular entre inputs | Detectada e quebrada (similar a `TopologicalCycleError`) |
| Capacidade já construída vs inferida | `validate_against_actual()` — compara composição inferida com a registrada |
| Input tool referencia capability que não existe | `missing_inputs` inclui a capability referenciada |

---

## 4. Estrutura de Dados

### 4.1 CognitiveInput

```python
@dataclass(frozen=True)
class CognitiveInput:
    """Insumo cognitivo imutável — unidade atômica da composição."""
    input_id: str              # "metodo.engenharia_reversa"
    name: str                  # "Engenharia Reversa"
    input_type: str            # "concept" | "method" | "knowledge_base" | "tool" | "external_domain" | "validation"
    description: str
    maturity: str              # "established" | "emerging" | "speculative"
    references: list[str]      # DOIs, paths, ou URLs
    source: str                # "curated" | "extracted:evo-N" | "extracted:skill-X" | "inferred"
    validation_cts: list[str]  # CT-IDs que validam este input (ex.: ["CT-COMP-001"])
```

### 4.2 CapabilityUnit

```python
@dataclass(frozen=True)
class CapabilityUnit:
    """Decomposição completa de uma capacidade em insumos construtíveis."""
    capability_id: str         # "metodos.Quantitativo experimental"
    capability_name: str       # nome legível
    concepts: list[str]        # input_ids do tipo "concept"
    methods: list[str]         # input_ids do tipo "method"
    knowledge_bases: list[str] # input_ids do tipo "knowledge_base"
    tools: list[str]           # input_ids do tipo "tool" (podem referenciar capabilities)
    external_domains: list[str]# input_ids do tipo "external_domain"
    validations: list[str]     # input_ids do tipo "validation"
    internal_deps: dict[str, list[str]]  # input_id → [input_ids que dependem dele]
    missing_inputs: list[str]  # input_ids que não existem na biblioteca
    construction_cost: float   # 0-1, proporção de inputs faltantes
    frontier: bool             # True se sem composição conhecida
```

### 4.3 InputNode (Grafo de Insumos)

```python
@dataclass
class InputNode:
    """Nó no grafo de insumos compartilhados."""
    input_id: str
    input_type: str
    shared_by: set[str]        # capability_ids que usam este input
    build_cost: float          # custo de construir este input (0-1)
    exists: bool               # True se já existe no ecossistema
```

---

## 5. Interface com Módulos Existentes

### 5.1 Modificações em cross_validation_engine.py

```python
@dataclass
class CapabilityNode:
    # ... campos existentes mantidos ...
    composition: Any | None = None  # NOVO: CapabilityUnit opcional
```

### 5.2 Modificações em evolutionary_pipeline.py

```python
@dataclass
class EvolutionaryScenario:
    # ... campos existentes mantidos ...
    required_inputs: list[str] = field(default_factory=list)  # NOVO

@dataclass
class EvolutionaryRoadmap:
    # ... campos existentes mantidos ...
    capability_units: list[Any] = field(default_factory=list)  # NOVO
    total_construction_cost: float = 0.0  # NOVO
```

### 5.3 Modificações em minimum_capability_solver.py

```python
@dataclass
class CapabilitySet:
    # ... campos existentes mantidos ...
    shared_inputs: dict[str, list[str]] = field(default_factory=dict)  # NOVO
    # cost agora é construction_cost, não |required|
```

---

## 6. Plano de Implementação (Concluído)

### Stage 1 — SPEC-033: Estrutura + Biblioteca Seed ✅

| CT | Nome | Status |
|----|------|--------|
| COMP-001 | Validação sintática de CognitiveInput | ✅ |
| COMP-001b | Rejeita input_id sem ponto | ✅ |
| COMP-001c | Todos os 6 tipos aceitos | ✅ |
| COMP-002 | CapabilityUnit vazia => frontier | ✅ |
| COMP-002b | all_inputs combina todos os tipos | ✅ |
| COMP-003 | Biblioteca carrega 85 inputs | ✅ |
| COMP-004 | Templates geram inputs para 3 categorias | ✅ |
| COMP-005 | Bootstrap extrai 15 inputs de evo-*.md | ✅ |
| COMP-006 | Bootstrap extrai 20 inputs de skills | ✅ |
| COMP-007 | add duplicado => ValueError | ✅ |
| COMP-007b | search + remove funcionam | ✅ |
| COMP-008 | Serialização idempotente | ✅ |
| COMP-008b | save_json => load_json roundtrip | ✅ |

### Stage 3 — SPEC-035: Integração ao Pipeline ✅

| CT | Nome | Status |
|----|------|--------|
| INT-001 | CapabilityNode.composition populado | ✅ |
| INT-002 | EvolutionaryScenario.required_inputs | ✅ |
| INT-003 | MCSP com construction_cost | ✅ |
| INT-004 | Desconto por inputs compartilhados | ✅ |
| INT-005 | Roadmap inclui capability_units | ✅ |
| INT-006 | Pipeline completo sem erro | ✅ |

---

## 7. Exemplo Concreto

### Entrada (do Scanner Teleológico)
```
Gap: "metodos.Quantitativo experimental" (severity=critical, weight=1.0)
Domínio: psicologia
```

### Saída (da Composição Unitária)
```json
{
  "capability_id": "metodos.Quantitativo experimental",
  "concepts": [
    "conceito.causalidade",
    "conceito.controle_experimental",
    "conceito.validacao_empirica"
  ],
  "methods": [
    "metodo.design_fatorial",
    "metodo.randomizacao",
    "metodo.analise_poder_estatistico"
  ],
  "tools": [
    "tool.raciocinio_probabilistico",
    "tool.analise_estatistica_inferencial"
  ],
  "external_domains": [
    "dominio.estatistica",
    "dominio.metodologia_cientifica"
  ],
  "validations": [
    "valid.CT_D3_001",
    "valid.CT_D9_003"
  ],
  "construction_cost": 0.42,
  "missing_inputs": ["conceito.controle_experimental", "metodo.analise_poder_estatistico"],
  "frontier": false
}
```

---

## 8. Resultado da Implementação

| Estágio | CTs | Status | Arquivos |
|---------|-----|--------|----------|
| SPEC-033 (Estrutura + Biblioteca) | 13 | ✅ 13/13 PASS | `capability_composer.py` (447 linhas), `cognitive_library.json` (85 inputs) |
| SPEC-035 (Integração) | 6 | ✅ 6/6 PASS | 3 arquivos modificados + `test_capability_integration.py` |
| Regressão (SPECs 025-032) | 76 | ✅ 76/76 PASS | Zero breakage |
| **Total** | **95** | **✅ 95/95 (100%)** | **7 suites** |

---

## 9. Referências

- SPEC-028: NoologicalScanner v3.0 — `skills/system/academic-audit/noological_scanner.py`
- SPEC-029: TeleologicalReverseScanner — `skills/system/academic-audit/teleological_scanner.py`
- SPEC-030: EvolutionaryScannerPipeline — `skills/system/academic-audit/evolutionary_pipeline.py`
- SPEC-031: ScannerRefinement — `skills/system/academic-audit/scanner_refinements.py`
- SPEC-032: MinimumCapabilitySolver — `skills/system/academic-audit/minimum_capability_solver.py`
- CrossValidationEngine — `skills/system/academic-audit/cross_validation_engine.py`
- Evolution artifacts — `evolution/evo-*.md` (16 arquivos)
