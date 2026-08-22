---
spec_id: SPEC-935-R439
component: academic.rigorous_board
title: Banca Rigorosa Simulada Multi-Periódico com Correção e Limpeza de Gaps
version: 1.0.0
status: green
test_file: tests/test_r439_rigorous_board.py
---

# SPEC-935-R439 — Banca Rigorosa Simulada Multi-Periódico com Correção e Limpeza de Gaps

## Meta
- **Ciclo**: R439
- **Alvo**: 10.0 / 100 — banca rigorosa que simula CAPES Qualis A1 + Nature/Science/IEEE/Lancet antes de qualquer entrega, com loop obrigatório de revisão→correção→limpeza→re-verificação
- **Componente**: `academic/rigorous_board.py` + integração em `academic/maswos.py` e `marceloclaro/orchestrator.py`

## Diagnóstico
- `31_agente_blind_peer_review_emulado` simula apenas 3 revisores genéricos (metodologista, teórico, nitpicking) sem rubricas específicas por periódico; não há ponderação por venue (Nature exige novidade disruptiva, IEEE exige reprodutibilidade de código, Lancet exige CONSORT/PRISMA).
- `MaswosPipeline` termina em `qa_qualis_a1` (AUTO_SCORE heurístico) sem **banca externa simulada** antes de `integracao_editorial`; gaps detectados não são limpos automaticamente antes da entrega — violates a diretiva do usuário de "sempre revise e corrija antes de entregar".
- `CORRIGENDUM.md` registra overclaims corrigidos, mas não há **circuito fechado** que impeça a entrega de manuscrito com `gap_critical` (ex. p-hacking, falta de baseline, ética ausente).

## Arquitetura

```
[Manuscrito + Referências + Artefatos]
        │
        ▼
RigorousBoard.review(manuscript, venue="auto" | "capes_qualis_a1" | "nature" | "ieee" | "lancet")
  ├── BoardCriteria (pesos por venue: 8 dimensões Qualis A1 + 5 específicas Nature/IEEE/Lancet)
  ├── 3 Reviewers (R1: Metodologista/Estatístico, R2: Teórico de escopo, R3: Formal/Ético)
  │     └── cada reviewer: scan heurístico (falácias, vieses, p-hacking, baseline, ética, ABNT, reprodutibilidade) → gaps + score 0-10
  ├── Agregação: gaps únicos por dimensão, severidade (critical/major/minor), recomendações priorizadas
  └── BoardDecision: status ∈ {accept, minor_revision, major_revision, reject} + overall_score + gaps + recommendations
        │
        ▼
GapCleaningEngine.clean(manuscript, gaps) — aplica correções determinísticas:
  ├── limpa TODO/FIXME, remove segredos hardcoded → .env
  ├── completa ABNT faltante (formata via ReferenceAuditor)
  ├── adiciona seção faltante (limitações/testes/ética) quando gap = missing_docs
  ├── marca p-hacking suspeito com nota de cautela metodológica
  └── re-ranqueia referências (dedup + temporal)
        │
        ▼
Re-verificação: Board.review(manuscrito corrigido) → se ainda major/reject e iteração <3, loop; senão entrega
        │
        ▼
[Manuscrito Pronto + Relatório de Banca + Carta de Submissão/Rebuttal] → Entrega bloqueada se ainda `critical`
```

### C1 — BoardCriteria (`academic/rigorous_board.py`)
```python
@dataclass
class BoardCriteria:
    venue: str  # capes_qualis_a1 | nature | science | ieee | lancet | auto
    weights: Dict[str, float]  # 8-13 dimensões, soma 1.0
    thresholds: Dict[str, float]  # accept≥8.5, minor≥7.0, major≥5.0, else reject (ajustado por venue)
```
- CAPES Qualis A1: pesos MASWOS/RUBRIC (10 critérios, peso total 1.0, gate 8.0)
- Nature/Science: `originalidade` 0.25, `novidade disruptiva` 0.20, `so-what` 0.15
- IEEE: `reprodutibilidade de código` 0.20, `baseline` 0.20, `ablation` 0.15
- Lancet: `CONSORT/PRISMA` 0.25, `ética/CAAE` 0.20, `registro de protocolo` 0.15

### C2 — RigorousBoard
| Método | Contrato |
|---|---|
| `review(manuscript, venue, references)` | Retorna `BoardDecision` com `overall_score 0-10`, `status`, `gaps: List[Gap]`, `recommendations: List[str]`, `reviewers: List[ReviewerReport]` |
| `decide(gaps, score)` | `critical` gap → `reject`; `major` → `major_revision`; `minor` → `minor_revision`; senão `accept` |
| `correction_loop(manuscript, venue, max_iter=3)` | Loop revisão→clean→re-review até `accept/minor` ou `max_iter`; retorna `{final_manuscript, history, final_decision, gaps_cleaned}` |

### C3 — GapCleaningEngine
| Método | Contrato |
|---|---|
| `clean(manuscript, gaps)` | Aplica correções determinísticas para `missing_docs`, `todo_fixme`, `hardcoded_secret`, `abnt_incomplete`, `p_hacking_suspect`, `missing_baseline` |
| `metrics` | `{gaps_in, gaps_out, gaps_closed, remaining}` |

### C4 — Integração
- `MaswosPipeline.run(..., rigorous_board=True)` — após `integracao_editorial`, invoca `RigorousBoard.correction_loop` e só aprova se `final_decision.status ∈ {accept, minor_revision}`; caso contrário `approved=False` com `board_report` anexado
- `marceloclaro/orchestrator.py:academic_pipeline_with_rigorous_board(topic, venue, max_iter)` — wrapper que orquestra `maswos_pipeline` + `RigorousBoard` com reflexão no MetaBus e registro em `evolution/cycles.json`

## Critérios de Aceitação
1. AC1 — SPEC-935-R439 `green`
2. AC2 — `BoardCriteria` para `capes_qualis_a1`, `nature`, `ieee`, `lancet` com pesos somando 1.0 e thresholds coerentes
3. AC3 — `RigorousBoard.review` com manuscrito fraco (sem metodologia, sem referências) retorna `major_revision` ou `reject` com gaps `critical`/`major`
4. AC4 — `review` com manuscrito forte (com metodologia, estatística, referências ABNT) retorna `accept` ou `minor_revision` com score ≥7.0
5. AC5 — `GapCleaningEngine.clean` remove `TODO` e completa `ABNT` faltante
6. AC6 — `correction_loop` com manuscrito fraco melhora `overall_score` na 2ª iteração e reduz `gaps` (monotonicamente não-pior)
7. AC7 — `MaswosPipeline` com `rigorous_board=True` só aprova se `board_decision` não for `reject`/`major_revision` persistente
8. AC8 — `orchestrator.academic_pipeline_with_rigorous_board` expõe `board_history` e reflete no MetaBus
9. AC9 — `CORRIGENDUM.md` não é sobrescrito; novas entradas são acrescentadas com timestamp e `board_decision`
10. AC10 — `doctor` com 102 specs e 257 ciclos

## Não Objetivos
- Não substitui banca humana real; simulação é determinística e heurística, não LLM com conhecimento externo
- Não bloqueia entrega quando `venue=auto` e humano explicitamente solicita `force_delivery=True` (com aviso)
- Não fabrica dados ou experimentos — apenas limpa gaps estruturais e sinaliza os que exigem coleta adicional
