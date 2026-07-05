# SPEC-040: Aletheia Superhuman Proof Validation — Integração OpenCode

**Status**: Draft → Implementação
**Autor**: OpenCode Ecosystem (2026)
**Data**: 2026-06-10
**Dependências**: SPEC-036 (Metacognition), SPEC-038 (TrustEngine)

---

## 1. Problema

O ecossistema OpenCode possui 4 motores de raciocínio (Z3, SymPy, miniKanren, Critical) e 42 tipos de raciocínio documentados, mas não possui validação formal de provas matemáticas com pipeline multi-agente. Aletheia preenche esta lacuna com 5 fases (A→B→C→D→E) e integração nativa com ReasoningOrchestrator e Cora-Debate.

## 2. Conceito

Integrar Aletheia como skill `/aletheia` com:
- Phase A: Problem evaluation (670 → 10 problems)
- Phase B: Proof generation with domain templates
- Phase C: Lean 4 verification
- Phase D: PhD Auditor (10 dimensions)
- Phase E: Reasoning-guided improvement

## 3. Estrutura de Dados

```python
@dataclass
class AletheiaProof:
    proof_id: str
    domain: str               # set_theory, number_theory, algebra...
    statement: str
    lean_code: str
    reasoning_phases: list[int]  # [1..7]
    sorry_count: int
    verification: dict           # Cora V1-V7 results
    audit_tier: str              # A, B, C, D
    audit_score: float           # 0-10
    decisions: list[str]         # DecisionNode IDs
```

## 4. Interface

- `/aletheia [problem]` — Generate + validate proof
- `/aletheia-audit [id]` — PhD Auditor on existing proof
- `/aletheia-benchmark` — Run 10-problem benchmark
- `/aletheia-decisions [id]` — DecisionNode trail

## 5. Critérios de Aceitação (8 CTs)

| CT | Descrição |
|----|-----------|
| AL-001 | AletheiaProof dataclass válido |
| AL-002 | Phase A: problem evaluation reduz escopo |
| AL-003 | Phase B: geração de prova com template |
| AL-004 | Phase D: PhD Auditor 10 dimensões |
| AL-005 | DecisionNode integração |
| AL-006 | Benchmark 10 problemas executável |
| AL-007 | Tier A para prova canônica (power set) |
| AL-008 | Pipeline A→B→D completo sem erro |
