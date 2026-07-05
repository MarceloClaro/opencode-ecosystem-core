# SPEC-031: SCANNER REFINEMENT — Refinamento SDD+TDD do Ecossistema de Scanners

**Versão:** 1.0.0  
**Data:** 2026-06-08  
**Dependências:** SPEC-028, SPEC-029, SPEC-030

---

## 1. Objetivo

Refinar o ecossistema de 5 scanners em 4 eixos, cada um com SDD formal e TDD.

---

## 2. Eixo 1 — CrossValidationEngine v2.0

### SDD: Expansão de Regras

**Estado atual:** 36 arestas em DEPENDENCY_RULES.  
**Meta:** 64+ arestas com cobertura de todas as 10 dimensões.

**Novas regras de dependência (28 adicionais):**

| Categoria | Regra |
|-----------|-------|
| Regras de prerequisite (12 novas) | paradigmas.Critico requer raciocinio.Dialetico, dados.Neurobiologicos requer dominios.Neurociencias, metodos.Pesquisa-acao requer paradigmas.Pragmatista, raciocinio.Teleologico requer temporalidade.Prospectivo, teoria_jogos.Stackelberg requer teoria_jogos.Nash, teoria_jogos.Sinalizacao requer teoria_jogos.Bayesiano |
| Regras de enable (10 novas) | raciocinio.Dialetico habilita paradigmas.Critico, dados.Qualitativos habilita metodos.GroundedTheory, dominios.IA habilita dados.Comparativos, temporalidade.Historico habilita dados.Documentais, raciocinio.Metacognitivo habilita paradigmas.Construtivista |
| Regras de co-occurrence (6 novas) | paradigmas.PosEstruturalista co-ocorre com dominios.Sociologia, metodos.Misto co-ocorre com paradigmas.Pragmatista, raciocinio.Abdutivo co-ocorre com metodos.Qualitativo |

### TDD (4 novos CTs)
| CT | Descrição |
|----|-----------|
| REF-001 | Total de arestas >= 60 |
| REF-002 | Todas as 10 dimensões têm ao menos 2 arestas |
| REF-003 | `find_bottlenecks` com min_dependents=4 retorna >= 3 |
| REF-004 | Self-discovery: `learn_from_scan` detecta co-ocorrências implícitas |

---

## 3. Eixo 2 — PolymathicConvergence v2.0

### SDD: Expansão + Bidirecional

**Estado atual:** 12 domínios com mapeamentos unidirecionais.  
**Meta:** 22+ domínios com transferência bidirecional.

**Novos domínios (10 adicionais):**

| Domínio | Problema Análogo |
|---------|-----------------|
| Ciência da Computação | Algoritmos de busca, otimização, complexidade |
| Teoria da Informação | Entropia, compressão, canal de comunicação |
| Engenharia de Software | Arquitetura, design patterns, refatoração |
| Genética | Hereditariedade, mutação, expressão gênica |
| Climatologia | Modelagem de sistemas complexos, tipping points |
| História | Ciclos civilizacionais, colapso de sistemas |
| Literatura | Estruturas narrativas, arquétipos |
| Arquitetura | Design estrutural, padrões, materiais |
| Culinária | Combinação de ingredientes, receitas |
| Esportes | Treinamento, performance, estratégia |

### Transferência Bidirecional

Cada mapeamento agora inclui:
- `principle_from → domain` (o que aprendemos do domínio externo)
- `principle_to → domain` (o que o domínio externo pode aprender conosco)

### TDD (4 novos CTs)
| CT | Descrição |
|----|-----------|
| REF-005 | Total de domínios >= 22 |
| REF-006 | `find_analogies` para gap multi-domínio retorna >5 analogias |
| REF-007 | Transferência bidirecional: cada analogia tem `principle_from` e `principle_to` |
| REF-008 | `cross_domain_score`: similaridade entre dois domínios via analogias compartilhadas |

---

## 4. Eixo 3 — EvolutionTracker (NOVO)

### SDD: Tracking Temporal de Scans

```python
@dataclass
class ScanSnapshot:
    timestamp: str
    noological_coverage: float
    teleological_score: float
    total_gaps: int
    bottlenecks: list[str]
    dimensions: dict  # snapshot das 10 dimensões

class EvolutionTracker:
    def record_scan(snapshot: ScanSnapshot) -> None
    def compare_scans(t1, t2) -> DeltaReport  # o que MUDOU entre dois scans
    def trend_analysis() -> list[TrendLine]   # tendência de cada dimensão
    def velocity() -> float                   # taxa de melhoria (gaps/dia)
```

### TDD (4 novos CTs)
| CT | Descrição |
|----|-----------|
| REF-009 | `record_scan` persiste snapshot em memória |
| REF-010 | `compare_scans` detecta dimensões que melhoraram/pioraram |
| REF-011 | `trend_analysis` calcula slope de melhoria |
| REF-012 | `velocity` > 0 quando gaps diminuem entre scans |

---

## 5. Eixo 4 — TimelineEstimator + Roadmap v2.0

### SDD: Timeline e Fases

**Estado atual:** TrajectoryMapper gera rotas sem estimativa temporal.  
**Meta:** Cada rota inclui timeline com fases e deadlines estimados.

```python
@dataclass
class TimelinePhase:
    name: str
    duration_weeks: int
    scenarios: list[EvolutionaryScenario]
    dependencies: list[str]

@dataclass  
class EvolutionaryRouteV2(EvolutionaryRoute):
    timeline: list[TimelinePhase]
    total_weeks: int
    risk_level: str  # "low" | "medium" | "high"
```

### Estimativa de Duração

| Cenário | Semanas estimadas |
|---------|-------------------|
| quick_win | 1-2 semanas |
| foundation | 3-6 semanas |
| convergent | 2-4 semanas |
| frontier | 8-16 semanas |

### TDD (4 novos CTs)
| CT | Descrição |
|----|-----------|
| REF-013 | TimelineEstimator atribui duração correta por tipo de cenário |
| REF-014 | Rota V2 inclui timeline com ao menos 2 fases |
| REF-015 | `risk_level` calculado: >16 semanas → "high", 8-16 → "medium", <8 → "low" |
| REF-016 | Pipeline completo gera RoadmapV2 com timeline + risk |

---

## 6. Métricas de Refinamento

| Eixo | Antes | Depois |
|------|-------|--------|
| CrossVal arestas | 36 | 64+ |
| CrossVal dimensões cobertas | 8/10 | 10/10 |
| Polymathic domínios | 12 | 22+ |
| Evolution tracking | 0 | EvolutionTracker |
| Timeline no roadmap | 0 | TimelineEstimator |
| CTs totais SPEC-030 | 16 | 32 (16 base + 16 refinement) |
