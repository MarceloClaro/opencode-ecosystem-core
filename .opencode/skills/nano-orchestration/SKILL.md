---
name: nano-orchestration
description: >
  Use ONLY when the user wants to produce a large-scale manuscript (30–500 pages)
  using LiteRT-LM models (Gemma4, Qwen3) via nanogranular decomposition and
  3-pass coherence fusion. Trigger keywords: nano, orchestration, manuscript,
  500 pages, thesis, dissertation, book, large-scale writing, nano-orchestration,
  nano_orchestration, SPEC-935-R53. Do NOT activate for single-query writing,
  small documents (< 30 pages), or general Q&A.
---

# Nano-Orchestration Skill

Produces large-scale academic manuscripts (up to **500 pages / 5,000+ nanoblocks**)
using LiteRT-LM on-device models (Qwen3 0.6B, Gemma4 2B E2B, Gemma4 4B E4B)
with a 20K-token context window, overcoming the context limitation via
nanogranular decomposition + 3-pass coherence fusion.

## Architecture (7-Phase Pipeline)

```
[Input: title + sections + pages]
        │
        ▼
┌──────────────────────────────────────┐
│ 1. NanoPlanner                       │  specs/SPEC-935-R53.md
│    pages → nanoblocks (10/page)      │  nano_orchestration/planner.py
│    dependency graph, token estimates  │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ 2. NanoSDD Engine                    │  nano_orchestration/nano_sdd.py
│    3–7 criteria per nanoblock        │
│    prompts with type/tone/length     │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ 3. ContextWindowManager              │  nano_orchestration/context_window.py
│    minimal context (~300 tok/block)  │
│    neighbors + citations             │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ 4. NanoWriter Pool (parallel)        │  nano_orchestration/writer.py
│   ┌─────────┬──────────┬──────────┐  │
│   │Qwen3 0.6│Gemma4 2B │Gemma4 4B │  │
│   │ descr.  │ argument.│ analít.  │  │
│   │ ~3s     │ ~8s      │ ~20s     │  │
│   └─────────┴──────────┴──────────┘  │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ 5. Quality Checker                   │  nano_orchestration/quality_checker.py
│    validates against mini-SDD        │
│    fail → rewrite with model scale   │
│    max 3 attempts                    │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ 6. CoherenceEngine (3 passes)        │  nano_orchestration/coherence.py
│    Pass 1: local (bi-neighbor)       │
│    Pass 2: global (per section)      │
│    Pass 3: fluency (full text)       │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ 7. CrossValidator                    │  nano_orchestration/cross_validator.py
│    transitions, terminology,         │
│    contradictions, cohesion score    │
└──────────────────────────────────────┘
        │
        ▼
[Coherent manuscript up to 500 pages]
```

## SDD — Specification-Driven Development

Every feature in this skill is gated by **SPEC-935-R53** (47 acceptance criteria).
Never modify nano_orchestration/ code without updating the spec first.

**Validation command:**
```bash
python3 scripts/validate_spec_r53.py --scale 500 --output /tmp/validacao.json
```

## TDD — Test-Driven Development

**Test suite:** `tests/test_nano_orchestration.py` (76 tests, coverage > 95%)

**RED → GREEN → REFACTOR cycle:**
```bash
# Before implementing any change:
python3 -m pytest tests/test_nano_orchestration.py -q

# After implementing:
# 1. Verify all existing tests still pass
# 2. Add new test(s) for the new behavior
# 3. Run full suite
python3 -m pytest tests/test_nano_orchestration.py -v --tb=short
```

## Model Routing

| Block Type | Model | Avg Time | Timeout |
|---|---|---|---|
| Descritivo | Qwen3 0.6B | ~3s | 30s |
| Transição | Qwen3 0.6B | ~2s | 20s |
| Citação | Qwen3 0.6B | ~3s | 25s |
| Argumentativo | Gemma4 2B | ~8s | 60s |
| Metodologia | Gemma4 2B | ~10s | 60s |
| Resultado | Gemma4 2B | ~6s | 45s |
| Analítico | Gemma4 4B | ~20s | 120s |
| Discussão | Gemma4 4B | ~15s | 120s |
| Conclusão | Gemma4 2B | ~8s | 90s |

## Quality Gates

| Gate | Metric | Target |
|---|---|---|
| SDD Gate | Criteria coverage | 100% |
| Quality Gate | Checker score | ≥ 9.5/10 |
| Coherence Gate | Composite score | ≥ 9.5/10 |
| Cross-Validation Gate | Cohesion score | ≥ 9.5/10 |
| Success Gate | Blocks written | > 98% |

## Failover Strategy

```
Attempt 1: Ideal model (routed by block type)
    ↓ fail
Attempt 2: Fallback to next-lower model
    ↓ fail
Attempt 3: Fallback to Qwen3 0.6B (last resort)
    ↓ fail
Block marked for manual review (status="failed")
```

## References

- **Spec:** `specs/SPEC-935-R53-nano-orchestration.md`
- **Source:** `nano_orchestration/` (9 modules)
- **Tests:** `tests/test_nano_orchestration.py` (76 tests)
- **Validator:** `scripts/validate_spec_r53.py` (34 CAs)
- **Manual:** `docs/MANUAL_NANO_ORCHESTRATION.md`
- **Server:** `scripts/litert-lm-serve.sh`
- **Provider spec:** `specs/SPEC-935-R210-litertlm-plugin-provider.md`
