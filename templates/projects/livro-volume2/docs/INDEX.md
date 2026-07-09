# Documentação Técnica — Livro Volume 2

> **Gêmeos Digitais na Odontologia: Framework SUS-Twin**
> Autor: Marcelo Claro Laranjeira
> Ecossistema: OpenCode v5.4.0

## Estrutura da Documentação

| Documento | Descrição |
|-----------|-----------|
| [`SDD_SUS_TWIN_FRAMEWORK.md`](SDD_SUS_TWIN_FRAMEWORK.md) | System Design Document — especificação formal do framework SUS-Twin |
| [`ADR-001-open-source-plataformas.md`](ADR-001-open-source-plataformas.md) | Decisão arquitetural: adoção de plataformas open-source |
| [`ADR-002-zkp-audit.md`](ADR-002-zkp-audit.md) | Decisão arquitetural: auditoria ZKP para privacidade LGPD |
| [`ADR-003-kfold-validation.md`](ADR-003-kfold-validation.md) | Decisão arquitetural: validação cruzada K-Fold para precisão preditiva |

## Referências Cruzadas

| Componente | Documento Relacionado |
|------------|----------------------|
| `sus_twin_framework.py` | SDD, ADR-002 |
| `test_sus_twin_framework.py` | SDD (Seção 5) |
| `dashboard.py` | SDD (Seção 6) |
| `generate_plots.py` | SDD (Seção 4) |
| `clinical_validation_dataset.json` | SDD (Seção 4.2) |
