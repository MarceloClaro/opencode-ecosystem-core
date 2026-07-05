# SPEC-TOP-RO11: Reasoning Orchestrator v11.0
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Orquestrador de raciocinio multiagente com 68+ tipos de raciocinio em 12 categorias, pipeline de 7 fases, agentes especializados (Inductor, BaseCase, Contradiction, LemmaTracker, CrossRef, StressTest, HypothesisTester, PrecedentAnalyzer, RiskAssessor, ProofHealth), Proof Confidence Index (PCI 0-100) e integracao com Cora-Debate V1-V6.

## Architecture
```
PROBLEMA
  ├── FASE 1: FUNDACIONAL (NotationAgent, AbstractionAgent, DecompositionAgent)
  ├── FASE 2: INDUTIVA/REDUTIVA (InductorAgent, BaseCaseAgent, InvariantAgent)
  ├── FASE 3: DEDUTIVA (LemmaTrackerAgent, SilogisticAgent, BackwardChainAgent)
  ├── FASE 4: CONSTRUTIVA (ConstructorAgent, StressTestAgent)
  ├── FASE 5: REFUTACIONAL (ContradictionAgent, ContraexemploAgent)
  ├── FASE 6: VERIFICACIONAL (ExhaustiveAgent, CrossRefAgent, Cora-Debate V1-V6)
  └── FASE 7: META-COGNITIVA (ProofHealthAgent → PCI 0-100)
```

## Core Classes
| Class | File | Purpose |
|-------|------|---------|
| ReasoningAgent | framework.py | Base agent with validate_dependencies |
| ReasoningResult | framework.py | Result dataclass (conclusion, confidence, evidence) |
| OrchestratorState | orchestrator.py | Pipeline state (phase, results, PCI, verdict) |
| ReasoningOrchestrator | orchestrator.py | 7-phase pipeline executor |

## Agent Files
| File | Agents |
|------|--------|
| critical_agents.py | Inductor, BaseCase, Contraexemplo, Contradiction, StressTest, Exhaustive, CrossRef, LemmaTracker |
| domain_agents.py | HypothesisTester, PrecedentAnalyzer, RiskAssessor, ProofHealth |
| game_theory_agents.py | NashEquilibrium, Minimax, BackwardInduction, ShapleyValue |
| refined_agents.py | RefinedLemmaTracker, RefinedContradiction, RefinedInduction |
| framework.py | REASONING_REGISTRY, get_agents_for_domain, get_agents_for_category |

## Acceptance Criteria
- [x] CT-1: Directory structure valid (orchestrator.py, reason.py, agents/ with 30+ files)
- [x] CT-2: OrchestratorState initialized with correct defaults (phase=0, pci=0, verdict=PENDING)
- [x] CT-3: ReasoningOrchestrator has 7 pipeline phases
- [x] CT-4: solve() returns dict with pci, verdict, agent_results (pci 0-100)
- [x] CT-5: REASONING_REGISTRY has 50+ reasoning types across 5+ categories and 3+ domains
- [x] CT-6: get_agents_for_domain returns agents for "mathematics"
- [x] CT-7: SKILL.md documents all 7 phases (FASE 1-7) and PCI

## Test Coverage
- Location: `skills/reasoning-orchestrator-v11/tests/test_reasoning_v11.py`
- Classes: 4 (Structure, OrchestratorState, ReasoningOrchestrator, TaxonomyIntegrity)
- Tests: 12+
