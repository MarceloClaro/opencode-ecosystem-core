# SPEC-966: Validação Cruzada, Calibração e Audit Trail

**Round**: R53
**Data**: 2026-07-25
**Status**: Especificação
**Score**: 0.95

## Objetivo

Adicionar três camadas críticas de confiabilidade ao DataKnowledgeHub:

1. **CrossValidator** — valida dados entre múltiplas fontes independentes
2. **CalibrationLayer** — calcula confiança combinada (autoridade + frescor + consenso)
3. **AuditTrail** — log imutável e auditável de toda consulta usada em decisões

## Motivação

Sem validação cruzada, o ecossistema pode tomar decisões de orquestração
baseadas em dados incorretos de uma única fonte sem detecção. Sem calibração,
não há como distinguir uma fonte autoritativa de uma fonte genérica. Sem audit
trail, não há reprodutibilidade — ninguém consegue responder "por que o
orquestrador decidiu X?"

## Arquitetura

```
DataKnowledgeHub
    │
    ▼
CrossValidator ─── valida dados entre fontes (BCB vs IBGE, yfinance vs Alpha Vantage)
    │
    ▼
CalibrationLayer ─── calcula confiança (autoridade × frescor × consenso)
    │
    ▼
AuditTrail ─── registra (timestamp, query, fonte, raw_hash, confiança, decisão)
    │
    ▼
Orquestrador usa dados calibrados e auditáveis
```

### CrossValidator

| Métrica | Fontes | Normalização | Tolerância |
|---|---|---|---|
| IPCA | BCB SGS 433, IBGE SIDRA 7060 | % direto | 0.1 pp |
| SELIC | BCB SGS 4390, BCB SGS 1178 | % a.a. | 0.25 pp |
| PIB Brasil | BCB SGS 1207, World Bank NY.GDP.MKTP.CD | BRL ↔ USD (câmbio) | 5% |
| Câmbio USD/BRL | BCB SGS 1, yfinance USDBRL=X | BRL/USD | 1% |
| Ação PETR4 | yfinance PETR4.SA, Alpha Vantage PETR4.SA | BRL | 0.5% |
| População | IBGE, World Bank SP.POP.TOTL | pessoas | 2% |

### CalibrationLayer

```
confiança_final = peso_autoridade × peso_frescor × peso_consenso
```

- **peso_autoridade**: 0.3-1.0 por fonte (BCB/IPEA=1.0, Wikipedia=0.7, ConceptNet=0.5)
- **peso_frescor**: decay exponencial: e^(-λ × Δt), λ = 1/ttl_domain
- **peso_consenso**: 0.5 (sem pares) a 1.0 (consenso total entre fontes)

### AuditTrail

Cada entrada:
```json
{
  "id": "audit_20260725_001",
  "timestamp": "2026-07-25T14:30:00",
  "query": "IPCA 2024",
  "domain": "financeiro",
  "sources": ["bcb", "ibge"],
  "results_hash": "sha256:e3b0c44298fc1c...",
  "confidence": 0.95,
  "decision_context": "orchestrator:roster_agent",
  "cross_validated": true,
  "calibration": {
    "authority": 0.95,
    "freshness": 0.98,
    "consensus": 0.92,
    "final": 0.95
  }
}
```

## Critérios de Aceitação

- [ ] CrossValidator detecta discrepância > tolerância e rebaixa confiança
- [ ] CrossValidator aceita consenso quando fontes concordam dentro da tolerância
- [ ] CalibrationLayer combina autoridade + frescor + consenso em score único
- [ ] CalibrationLayer tem decay temporal (dados mais frescos = maior peso)
- [ ] AuditTrail é append-only (imutável após inserção)
- [ ] AuditTrail armazena hash SHA-256 do resultado bruto
- [ ] AuditTrail é exportável como JSON Lines
- [ ] Integração completa: DataKnowledgeHub.search() retorna confidence + audit_id
- [ ] Todas as 16 fontes têm score de autoridade mapeado

## Métricas

| Camada | Antes | Depois |
|---|---|---|
| Confiança por fonte | N/A (todas iguais) | 0.3-1.0 por fonte |
| Detecção de discrepância | Nenhuma | Tolerância por métrica |
| Decisões auditáveis | Nenhuma | Log imutável completo |
| Reprodutibilidade | N/A | Hash SHA-256 do resultado |
