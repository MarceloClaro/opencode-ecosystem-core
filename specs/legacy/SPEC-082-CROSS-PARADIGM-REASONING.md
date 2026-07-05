# SPEC-082: Cross-Paradigm Reasoning Engine

**Ciclo:** R38  
**Status:** Proposto  
**Prioridade:** Alta  
**Dependências:** SPEC-080 (Capability Registration), SPEC-081 (Research Skills), motores Z3/SymPy/Kanren/Critical  

## Objetivo
Criar um motor de raciocínio cross-paradigma que integre os 4 motores formais (Z3, SymPy, Kanren, Critical) com as 4 research skills (game_theory, temporal_population, theoretical_empirical, logical_multiscale), permitindo que problemas acadêmicos e de engenharia sejam resolvidos combinando múltiplos paradigmas de raciocínio.

## Arquitetura

```
Problema → ReasoningOrchestrator → Roteamento Inteligente
  ├→ Z3Engine (formal/restrições)
  ├→ SymPyEngine (simbólico)
  ├→ KanrenEngine (lógico/relacional)
  └→ CriticalEngine (falácias/vieses)
         ↓
  CrossParadigmSynthesizer → Resultado Multi-Paradigma
         ↓
  AutonomousSelfRepair → Validação e Correção
```

## Componentes

### 1. ReasoningOrchestrator
- Analisa o problema e determina quais motores acionar
- Suporta 4 modos: `auto` (detecção automática), `formal`, `symbolic`, `logic`, `critical`, `all`
- Para cada modo, roteia para o motor apropriado

### 2. CrossParadigmSynthesizer
- Combina resultados de múltiplos motores
- Detecta contradições entre paradigmas
- Atribui peso de confiança por motor
- Gera relatório consolidado

### 3. AutonomousSelfRepair (fundação)
- Detecta inconsistências entre saídas de diferentes motores
- Tenta resolver conflitos automaticamente
- Registra reparos para auditoria

### 4. ParadigmBridge
- Traduz problemas entre formalismos: lógica proposicional ↔ equações simbólicas ↔ fatos relacionais ↔ análise de argumentos
- Permite que um motor alimente outro

## Casos de Uso

| Caso | Motores | Descrição |
|------|---------|-----------|
| Validação de teorema | Z3 + SymPy | Prova formal + verificação simbólica |
| Análise de argumento | Critical + Kanren | Detecção de falácias + consistência lógica |
| Modelagem de jogo | GameTheory + Z3 | Equilíbrio Nash com restrições formais |
| Análise temporal | TemporalPopulation + SymPy | Séries temporais com modelagem simbólica |

## Critérios de Aceitação (14 CTs)

1. `test_cpr_import` — Módulo importa sem erros
2. `test_orchestrator_auto_detect` — Auto-detecção escolhe motores corretos para problema dado
3. `test_orchestrator_formal` — Modo formal aciona Z3Engine
4. `test_orchestrator_symbolic` — Modo symbolic aciona SymPyEngine
5. `test_orchestrator_logic` — Modo logic aciona KanrenEngine
6. `test_orchestrator_critical` — Modo critical aciona CriticalEngine
7. `test_synthesizer_combine` — Combinador mescla resultados de 2+ motores
8. `test_synthesizer_contradiction` — Detecta contradição entre motores
9. `test_self_repair_detect` — Detecta inconsistência
10. `test_self_repair_resolve` — Tenta resolver conflito
11. `test_paradigm_bridge_formal_to_symbolic` — Traduz restrição formal para equação simbólica
12. `test_paradigm_bridge_logic_to_critical` — Traduz fato lógico para análise crítica
13. `test_end_to_end_theorem` — Pipeline completo: problema → orquestração → síntese → validação
14. `test_cross_paradigm_confidence` — Pesos de confiança são calculados corretamente
