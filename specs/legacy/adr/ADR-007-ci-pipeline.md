# ADR-007: CI Pipeline com Spec Coverage Gate

**Status:** proposed
**Data:** 2026-05-27
**Autor:** ecosystem (baseado no Cap. 6 — Piramide de Testes)
**Inspirado por:** Livro "Engenharia de Software com Agentes Inteligentes" (Sandeco, 2026)

## Contexto

O ecossistema possui 100+ arquivos de teste e health checks manuais, mas nao possui pipeline de CI automatizado. O health.json mostra status "OK" mas seu timestamp e de 09/05/2026 (18 dias atras). Sem CI, regressoes podem passar despercebidas ate o proximo health check manual.

O Cap. 6 estabelece: "Tratar teste como etapa final e opcional e o equivalente a so verificar se os freios do carro funcionam depois de sair a 150 km/h."

## Decisao

Implementar pipeline CI com os seguintes gates:

1. **Lint Gate**: Todos os arquivos passam no linter (ruff para Python, eslint para TS)
2. **Unit Test Gate**: Todos os testes unitarios passam (`tests/core/`, `tests/nexus/`)
3. **Spec Coverage Gate**: Verifica se cada skill tem spec documentada (ADR-006)
4. **Integration Test Gate**: Testes de integracao do ecossistema passam (`tests/integration/`)
5. **Health Check Gate**: Health check automatico (agentes respondem, MCPs conectam, DB acessivel)

Execucao: a cada push ou PR, via GitHub Actions.

## Alternativas Consideradas

| Alternativa | Rejeitada porque |
|-------------|-----------------|
| CI apenas com lint | Nao detecta regressoes funcionais |
| CI manual (status quo) | Health check desatualizado, regressoes nao detectadas |
| CI apenas para editais-br | Ecossistema completo precisa de validacao |

## Metrica de Sucesso

- CI executado em < 10 minutos
- Cobertura de spec > 80% das skills ativas
- Zero regressoes entre health checks

## Referencias

- Cap. 6 do livro — Secao 6.13: A Piramide de Testes na Era das Specs
- `specs/integration/ci-pipeline.md`
