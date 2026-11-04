# opencode-peer-review

**Agentic Peer Review with Rubric Engine, Review Ledger, and Graph-Anchored Auditing**

Parte do OpenCode Ecosystem Core

[Core](../../README.md) · [Documentação](../../docs/README.md) · [Pipeline científico R1054](../../docs/SCIENTIFIC_RESEARCH_PIPELINE_R1054.md) (R103 — Agentic Peer Review).

## Instalação

```bash
pip install opencode-peer-review
```

## Uso

```python
from opencode_peer_review import (
    RubricEngine, ReviewLedger, MultiCriticReviewer, OrchestratorReviewer
)

orchestrator = OrchestratorReviewer()
review_package = orchestrator.review("Your manuscript text here")
```

## Componentes

- **RubricEngine**: 8 meta-dimensões de qualidade (REVIEWGROUNDER-inspired)
- **ReviewLedger**: Rastreamento claim–evidence–risk (DeepReviewer 2.0-inspired)
- **AuditGraph**: Auditoria em grafo integrada com EvidenceGraph
- **MultiCriticReviewer**: 4 especialistas simultâneos
- **OrchestratorReviewer**: Pipeline drafting→grounding→synthesis com export gate

## Dependências

- Python ≥ 3.10
- `opencode-deep-research` (opcional, para AuditGraph)
