# SPEC-030: EVOLUTIONARY TRAJECTORIES SCANNER — Scanner de Trajetórias Evolutivas

**Versão:** 1.0.0  
**Data:** 2026-06-08  
**Dependências:** SPEC-028 (NoologicalScanner v3.0), SPEC-029 (TeleologicalReverseScanner)

---

## 1. Conceito

O **Scanner de Trajetórias Evolutivas** transforma ausências e capacidades futuras em **caminhos de evolução estruturados**. Ele atua **após** o Scanner Noológico, adicionando 4 camadas:

```
Estado Atual
    │
    ▼
[M1] Scanner Noológico (SPEC-028) ──→ Ausências, pontos cegos
    │
    ▼
[M2] Scanner Reverso (SPEC-029) ──→ Capacidades futuras necessárias
    │
    ▼
[M3] Validação Cruzada ──→ Dependências ocultas, efeitos cascata
    │
    ▼
[M4] Convergência Polimática ──→ Soluções análogas em outros domínios
    │
    ▼
[M5] Mapa de Trajetórias ──→ Cenários, rotas, prioridades
    │
    ▼
Roadmap Evolutivo
```

### Diferença Conceitual dos 4 scanners

| Scanner | Pergunta | Natureza |
|---------|----------|----------|
| Noológico | "O que não existe?" | Descritiva |
| Teleológico | "O que deveria existir?" | Prescritiva |
| Validação Cruzada | "O que sustenta o quê?" | Estrutural |
| Convergência Polimática | "Quem já resolveu isso?" | Comparativa |
| Mapa de Trajetórias | "Qual o melhor caminho?" | Preditiva |

---

## 2. Módulo 3 — Validação Cruzada Evolutiva (CrossValidationEngine)

### Objetivo
Identificar dependências ocultas entre capacidades e modelar efeitos cascata.

### Data Structures

```python
@dataclass
class CapabilityNode:
    name: str           # "Raciocínio probabilístico"
    domain: str         # "raciocinio"
    provides: list[str]  # capacidades que habilita
    requires: list[str]  # capacidades das quais depende
    influence_score: float  # 0-1, impacto em cascata

@dataclass  
class DependencyGraph:
    nodes: dict[str, CapabilityNode]
    edges: list[tuple[str, str, float]]  # (from, to, weight)
```

### Regras de Inferência

| Regra | Descrição |
|-------|-----------|
| R1: Prerequisite | Se A requer B e B está ausente → A é inviável |
| R2: Cascade | Se A habilita B, C, D e A está ausente → B, C, D em risco |
| R3: Co-occurrence | A e B aparecem juntos em >80% dos sistemas bem-sucedidos → alta afinidade |
| R4: Bottleneck | Se A é prerequisite de >3 capacidades → bottleneck crítico |

### Algoritmo

1. Construir grafo de dependências a partir das 10 dimensões × 92 categorias
2. Para cada categoria ausente, calcular cascade_impact = soma dos pesos das capacidades que dependem dela
3. Identificar bottlenecks (top 5 cascade_impact)
4. Gerar matriz de co-ocorrência (quais categorias tendem a aparecer juntas)

---

## 3. Módulo 4 — Convergência Polimática (PolymathicConvergence)

### Objetivo
Descobrir soluções em domínios externos que resolveram problemas análogos.

### Domínios de Referência

| Domínio | Problema Análogo | Categoria Relacionada |
|---------|-----------------|----------------------|
| Neurociência | Memória, aprendizado, consolidação | temporalidade.longitudinal, raciocinio.indutivo |
| Sistemas Distribuídos | Consistência, replicação, consenso | teoria_jogos.cooperativo, raciocinio.sistemico |
| Cognição Humana | Heurísticas, vieses, metacognição | raciocinio.metacognitivo, raciocinio.probabilistico |
| Biologia Evolutiva | Adaptação, seleção, fitness landscape | teoria_jogos.evolutivo, paradigmas.complexo |
| Ecossistemas | Coevolução, nichos, resiliência | niveis_analise.sistemico, dominios.multiplos |
| Linguística | Gramática generativa, aquisição | raciocinio.dedutivo, raciocinio.indutivo |
| Música | Harmonia, contraponto, improvisação | raciocinio.abdutivo, paradigmas.construtivista |
| Organizações | Coordenação, cultura, inovação | niveis_analise.organizacional, teoria_jogos.cooperativo |
| Física | Leis de conservação, simetria, entropia | raciocinio.dedutivo, paradigmas.positivista |
| Matemática | Prova, abstração, estruturas | raciocinio.dedutivo, raciocinio.abdutivo |

### Algoritmo

1. Para cada gap teleológico, consultar `POLYMATHIC_MAPPINGS`
2. Retornar domínios externos que resolveram problemas análogos
3. Para cada domínio, retornar princípios transferíveis
4. Calcular `transferability_score` = similaridade do problema × maturidade da solução no domínio externo

---

## 4. Módulo 5 — Mapa de Trajetórias Evolutivas (TrajectoryMapper)

### Objetivo
Transformar ausências + capacidades futuras + dependências + convergências em cenários de evolução.

### Tipos de Cenário

| Cenário | Descrição | Critério |
|---------|-----------|----------|
| `quick_win` | Baixo custo, alto impacto | cascade_impact > 0.7, apenas 1 prerequisite |
| `foundation` | Habilita múltiplas outras capacidades | é bottleneck (prerequisite de >3) |
| `frontier` | Inovação, requer múltiplas novas capacidades | >3 prerequisites ausentes |
| `convergent` | Já resolvido em outro domínio | transferability_score > 0.8 |

### Algoritmo de Priorização

```
priority_score = (cascade_impact × 0.35) 
               + (transferability_score × 0.25) 
               + (goal_alignment × 0.25) 
               + (feasibility × 0.15)
```

Onde:
- `cascade_impact`: quantas capacidades são desbloqueadas
- `transferability_score`: quão transferível é de outro domínio
- `goal_alignment`: quão alinhado está com os objetivos teleológicos
- `feasibility`: 1 / (1 + número de prerequisites ausentes)

### Rotas

Cada trajetória é uma sequência ordenada de capacidades a adquirir:
```
Rota A: [fundação] → [quick_win] → [frontier]
Rota B: [convergent] → [fundação] → [quick_win]
Rota C: [quick_win] → [quick_win] → [foundation] → [frontier]
```

---

## 5. Pipeline Orquestrador

```python
class EvolutionaryScannerPipeline:
    def __init__(self):
        self.noological = NoologicalScanner()
        self.teleological = TeleologicalReverseScanner()
        self.cross_validator = CrossValidationEngine()
        self.polymathic = PolymathicConvergence()
        self.trajectory_mapper = TrajectoryMapper()
    
    def scan(self, audit_trail, goals, domain="") -> EvolutionaryRoadmap:
        # M1: Scan noológico
        nool_scan = self.noological.scan(audit_trail, domain)
        
        # M2: Scan teleológico reverso
        self.teleological.set_goals(goals)
        tel_gaps = self.teleological.compare_with_scan(nool_scan)
        
        # M3: Validação cruzada
        dep_graph = self.cross_validator.build_graph(nool_scan)
        bottlenecks = self.cross_validator.find_bottlenecks(dep_graph)
        cascade = self.cross_validator.cascade_impact(dep_graph, nool_scan)
        
        # M4: Convergência polimática
        analogies = self.polymathic.find_analogies(tel_gaps)
        
        # M5: Mapa de trajetórias
        trajectories = self.trajectory_mapper.generate(
            gaps=tel_gaps,
            bottlenecks=bottlenecks,
            analogies=analogies,
            cascade=cascade
        )
        
        return EvolutionaryRoadmap(
            noological=nool_scan,
            teleological_gaps=tel_gaps,
            bottlenecks=bottlenecks,
            analogies=analogies,
            trajectories=trajectories,
        )
```

---

## 6. Testes (TDD)

> Suite: `specs/test_evolutionary_scanner.py`

### Módulo 3 — Validação Cruzada (6 CTs)

| CT | Descrição |
|----|-----------|
| EVO-001 | CrossValidationEngine constrói grafo com 92 nós (10 dims × categorias) |
| EVO-002 | `find_bottlenecks` identifica categorias que são prerequisite de >3 outras |
| EVO-003 | `cascade_impact` calcula impacto: se A ausente, quantas dependem de A |
| EVO-004 | Dependency graph detecta ciclo (A→B→A) e reporta warning |
| EVO-005 | `co_occurrence_matrix` calcula afinidade entre pares de categorias |
| EVO-006 | Bottlenecks ordenados por cascade_impact decrescente |

### Módulo 4 — Convergência Polimática (4 CTs)

| CT | Descrição |
|----|-----------|
| EVO-007 | `find_analogies` para gap "raciocinio.probabilistico" retorna neurociência, economia |
| EVO-008 | `transferability_score` calculado entre 0-1 para cada analogia |
| EVO-009 | Domínio sem mapeamento retorna lista vazia (sem erro) |
| EVO-010 | Múltiplos gaps geram analogias agregadas sem duplicatas |

### Módulo 5 — Mapa de Trajetórias (4 CTs)

| CT | Descrição |
|----|-----------|
| EVO-011 | `classify_scenario`: cascade_impact>0.7 + 1 prereq → "quick_win" |
| EVO-012 | `classify_scenario`: prerequisite de >3 → "foundation" |
| EVO-013 | `priority_score` entre 0-1 para cada capacidade |
| EVO-014 | `generate_routes` produz ao menos 2 rotas com ordenação topológica |

### Pipeline (2 CTs)

| CT | Descrição |
|----|-----------|
| EVO-015 | Pipeline completo: Noological → Teleological → CrossVal → Polymathic → Trajectory |
| EVO-016 | Pipeline gera EvolutionaryRoadmap com todos os 5 módulos preenchidos |

---

## 7. Métricas

| Métrica | Meta |
|---------|------|
| Módulos implementados | 5/5 (Noological, Teleological, CrossVal, Polymathic, Trajectory) |
| CTs TDD | 16/16 PASS |
| Nós no grafo de dependências | 92 (10 dims × categorias) |
| Domínios polimáticos mapeados | 10 |
| Cenários de trajetória | 4 tipos (quick_win, foundation, frontier, convergent) |
