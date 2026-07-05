# SPEC-014 — Game Theory & 38 Tipos de Raciocínio

```yaml
spec_id: SPEC-014
title: Teoria dos Jogos e Catálogo de 38 Raciocínios
status: implemented
component: gametheory/
source: OpenCode_Ecosystem/skills/agent-forum (portado)
```

## Objetivo

Fornecer ao orquestrador e aos agentes um catálogo formal de **38 tipos de
raciocínio** (lógica clássica, dialética, crítica, Teoria dos Jogos,
probabilístico, sistêmico, criativo e metacognitivo) e ferramentas de Teoria
dos Jogos executáveis (matrizes de payoff, equilíbrio de Nash puro, valor de
Shapley, estratégias iteradas) para estruturar debates, decisões e auditorias.

## Requisitos

| ID | Requisito | Critério de aceitação |
|----|-----------|----------------------|
| R-014.1 | Catálogo completo | `len(list(ReasoningType)) == 38` |
| R-014.2 | Equilíbrio de Nash puro | `PayoffMatrix.prisoners_dilemma().find_nash_equilibria() == [("Trair", "Trair")]` |
| R-014.3 | Estratégias iteradas | `TitForTatStrategy`, `GenerousTitForTatStrategy`, `GrimTriggerStrategy` disponíveis |
| R-014.4 | Meta-seleção contextual | `MetaReasoner.select_for_context` inclui raciocínios de Teoria dos Jogos quando o tópico contém termos de conflito/negociação |
| R-014.5 | Auditoria PhD | `NashSolver`, `StatisticalRigor`, `QualisA1Auditor`, `SensitivityAnalyzer`, `IMRADFormatter` importáveis de `gametheory` |
| R-014.6 | Integração orquestrador | `orch.meta_reason(topic)` e `orch.nash_analysis(game)` registram reflexão na memória global |

## Invariantes

- INV-014.1: O catálogo de raciocínios é imutável em tempo de execução (Enum).
- INV-014.2: `find_nash_equilibria` retorna apenas perfis onde nenhum jogador
  tem incentivo unilateral de desvio (definição de Nash, 1950).
- INV-014.3: Toda análise via orquestrador gera reflexão metacognitiva no MetaBus.

## Referências

Nash (1950); Axelrod (1984); von Neumann & Morgenstern (1944); Shapley (1953);
Harsanyi (1967); Maynard Smith (1982); Kahneman & Tversky (1979); Myerson (1991).
