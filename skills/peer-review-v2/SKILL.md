# Peer-Review-V2 Skill

**Revisão por Pares com Auditagem em Grafo — R103 Agentic Peer Review**

Baseado em REVIEWGROUNDER + DeepReviewer 2.0, este skill implementa
revisão multi-agente com 4 especialistas, rubrica 8-dimensões, e auditoria rastreável.

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/review-v2 <manuscript>` | Revisão completa (4 especialistas + grafo) |
| `/review-rubric <paper>` | Gera rubrica 8-dimensões customizada |
| `/review-ledger` | Extrai claim–evidence–risk ledger |
| `/review-audit` | Auditoria de rastreabilidade |

## Uso

```
/review-v2 "We present a novel approach to..."
/review-rubric "Our method achieves SOTA on..."
/review-ledger
/review-audit
```

## Exemplo de saída

```
Revisão completa:
  Methodology: 72/100 — Sólido, mas falta análise de robustez
  Results: 68/100 — Métricas adequadas, faltam baselines
  Literature: 75/100 — Boa contextualização
  Ethics: 80/100 — Conforme

ReviewLedger: 8 claims, 2 alto risco, 3 médio, 3 baixo
Audit: Rastreabilidade 85% — 2 claims sem evidência âncora
```

## Dependências

- Python ≥ 3.10
- `agentic_science_v2` (core OpenCode Ecosystem)
