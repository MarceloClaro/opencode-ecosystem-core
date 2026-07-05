# SPEC-REA-CRI: Critical Reasoning
Version: 1.0.0 | Status: verified | TDD: required | Engine: CriticalEngine

## Objective
Analisar argumentos detectando falacias logicas e vieses cognitivos, comparar argumentos concorrentes e julgar debates com pontuacao de forca.

## Acceptance Criteria
- [x] CT-1: `analyze` detecta falacias (hasty_generalization para termos absolutos como "always"/"never")
- [x] CT-2: `analyze` retorna `ArgumentAnalysis` contendo `premises` e `conclusions` estruturados
- [x] CT-3: `strength` score entre 0-100 no resultado da analise
- [x] CT-4: `compare_arguments` retorna dict `winner` com argumento vencedor e score comparativo

## API Contract

### analyze(text: str) -> dict
```python
{
    "premises": [{"text": str, "type": "factual" | "normative" | "causal"}],
    "conclusions": [{"text": str, "confidence": float}],
    "fallacies": [
        {
            "type": "hasty_generalization" | "ad_hominem" | "straw_man" | "false_dichotomy" | "slippery_slope" | "appeal_to_authority" | "begging_the_question" | "post_hoc" | "bandwagon" | "red_herring" | "no_true_scotsman" | "appeal_to_emotion" | "tu_quoque" | "composition" | "division",
            "trigger": str,
            "explanation": str
        }
    ],
    "biases": [
        {
            "type": "confirmation_bias" | "anchoring" | "availability" | "framing" | "overconfidence",
            "trigger": str
        }
    ],
    "strength": int,  # 0-100
    "analysis_time_ms": float
}
```

### compare_arguments(arg1: str, arg2: str) -> dict
```python
{
    "winner": "arg1" | "arg2" | "tie",
    "arg1_strength": int,
    "arg2_strength": int,
    "rationale": str
}
```

### debate_judge(exchanges: list[dict]) -> dict
```python
{
    "winner": str,  # side identifier
    "score": {side_id: int},
    "fallacies_found": [{side: str, "fallacy": str}],
    "summary": str
}
```

## Engine
- Classe: `CriticalEngine`
- Localizacao: `skills/reasoning/critical-reasoning/scripts/critical_engine.py`
- Dependencias: sem dependencias externas (regex + logica pura)

## Falacias Detectaveis (15)
hasty_generalization, ad_hominem, straw_man, false_dichotomy, slippery_slope, appeal_to_authority, begging_the_question, post_hoc, bandwagon, red_herring, no_true_scotsman, appeal_to_emotion, tu_quoque, composition, division

## Vieses Cognitivos Detectaveis (5)
confirmation_bias, anchoring, availability, framing, overconfidence

## Dependencias da Skill
- `reasoning-orchestrator` (compativel com raciocinios: critical_analysis, fallacy_detection, argument_comparison, debate_evaluation)

## Test Results
- CT-1 to CT-4: PASSED
