# ADR-008: Component Registry com SWEBOK Maintenance Categories

**Status:** proposed
**Data:** 2026-05-27
**Autor:** ecosystem (baseado no Cap. 4 — Categorias de Manutencao SWEBOK)
**Inspirado por:** Livro "Engenharia de Software com Agentes Inteligentes" (Sandeco, 2026)

## Contexto

O ecossistema tem 118 agentes, 74 skills, 23 plugins, 20 MCPs — 235+ componentes. Nao ha registro centralizado que classifique cada componente por:
- Tipo de manutencao esperada (SWEBOK: evolutiva, adaptativa, corretiva, preventiva)
- Frequencia esperada de mudanca
- Dependencias de outros componentes
- Estado (active, deprecated, experimental)

Sem esse registro, planejar manutencao e impossivel. O Cap. 4 documenta que 67% do custo do ciclo de vida do software esta na manutencao, e a maior parte (50%) e evolutiva — features que o "cliente" (ecossistema) nao sabia que precisava quando o componente foi criado.

## Decisao

Criar `specs/component-registry.md` como fonte unica de verdade sobre todos os componentes do ecossistema. Cada entrada contem:

```yaml
- id: "skill-ai-engineering-harness"
  type: skill
  status: active
  version: "1.0.0"
  maintenance_category: evolutiva    # SWEBOK
  change_frequency: baixa             # alta|media|baixa
  dependencies: [using-git-worktrees, test-driven-development]
  dependents: []
  spec: "SPEC.md inline no SKILL.md"
  tests: "tests/superpowers/test_ai_engineering_harness.py"
  last_reviewed: "2026-05-27"
```

## Alternativas Consideradas

| Alternativa | Rejeitada porque |
|-------------|-----------------|
| Sem registro (status quo) | Impossivel planejar manutencao de 235+ componentes |
| Registro em planilha externa | Nao versionado, nao integrado ao codigo |
| Registro apenas no knowledge graph (memory MCP) | Memory MCP pode resetar. Precisa de fonte persistente em arquivo. |

## Consequencias

- **Positivas**: Planejamento de manutencao previsivel. Identificacao de componentes orfaos (sem dependents). Metricas de cobertura de teste por componente.
- **Negativas**: Manter registro atualizado requer disciplina (atualizar a cada nova skill/agente).
- **Riscos**: Registro desatualizado (mitigado: CI gate verifica consistencia).

## Referencias

- Cap. 4 do livro — Secao 4.2: Categorias de Manutencao (SWEBOK)
- `specs/component-registry.md`
