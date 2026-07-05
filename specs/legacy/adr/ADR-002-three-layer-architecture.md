# ADR-002: Arquitetura em 3 Camadas (MCP → Skill → Agent)

**Status:** active
**Data:** 2026-05-27
**Autor:** ecosystem (baseado no Cap. 4 — Desenvolvimento em Camadas)
**Inspirado por:** Livro "Engenharia de Software com Agentes Inteligentes" (Sandeco, 2026)

## Contexto

O ecossistema OpenCode integra 600+ componentes de 4 tipos: MCPs (infraestrutura), Skills (capacidades), Agentes (comportamentos) e Plugins (extensoes). Sem uma arquitetura em camadas clara, o acoplamento entre esses componentes geraria dependencias circulares, dificuldade de manutencao e fragilidade a mudancas (conforme Cap. 4: "Uma decisao de arquitetura ruim nao custa nada agora, mas pode custar semanas quando o sistema precisar crescer").

## Decisao

Organizar o ecossistema em 3 camadas com dependencia unidirecional:

```
┌──────────────────────────────┐
│  Agentes (125)               │  ← Comportamento autonômo
│  NAO acessam MCPs diretamente│
├──────────────────────────────┤
│  Skills (104)                │  ← Capacidades especializadas
│  NAO acessam MCPs diretamente│
├──────────────────────────────┤
│  MCPs (40) + Plugins (15)    │  ← Infraestrutura e ferramentas
│  NAO conhecem camadas acima  │
└──────────────────────────────┘
```

Regra de ouro: uma camada so conhece a camada imediatamente inferior.
- Agentes → usam Skills (nunca MCPs diretamente)
- Skills → usam MCPs (nunca Agentes)
- MCPs → sao autocontidos (nunca referenciam Skills ou Agentes)

## Alternativas Consideradas

| Alternativa | Rejeitada porque |
|-------------|-----------------|
| Mesh architecture (todos com todos) | Dependencias circulares, manutencao impossivel |
| Agentes acessam MCPs diretamente | Viola separacao de responsabilidades, dificulta auditoria |
| Camada unica (flat) | 600+ componentes sem organizacao hierarquica = caos |

## Consequencias

- **Positivas**: Substituir um MCP nao quebra Skills. Substituir uma Skill nao quebra Agentes. Isolamento de falhas.
- **Negativas**: Overhead de intermediacao (Skill precisa wrappear MCP). Latencia adicional minima.
- **Riscos**: Se uma Skill intermediaria falhar, o Agente perde acesso ao MCP. Mitigado com health checks.

## Referencias

- `AGENTS.md` — diagrama de arquitetura v4.2
- Cap. 4 do livro — Secao 4.7: Desenvolvimento em Camadas
- `core/agent_manager.py` — implementacao
