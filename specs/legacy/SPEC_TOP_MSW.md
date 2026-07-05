# SPEC-TOP-MSW: MASWOS V5 NEXUS Framework
Version: 1.0.0 | Domain: top-level | Status: active

## Objective
Framework multiagente com 130+ agentes orquestrados, 9 estrategias RAG, arquitetura Transformer Network e pipeline academico Qualis A1. Referencia canônica para o ecossistema MASWOS.

## Architecture
```
RAG-3E Routing → 9 Estrategias RAG → Transformer Network → 130+ Agentes
                     ↓
              Pipeline Qualis A1 + Juridico
```

## Reference Files
| File | Content |
|------|---------|
| architecture.md | Arquitetura Transformer Network + Antigravity Kit |
| rag-strategies.md | 9 estrategias RAG (Vanilla, Memory, Agentic, Graph, Hybrid, CRAG, Adaptive, Fusion, HyDE) |
| agents-and-skills.md | 21 agentes especialistas + 36 skills |
| audit-module.md | Pipeline de auditoria academica Qualis A1 |
| mcp-integration.md | Integracao MCP (academic, juridico, maswos-rag, pageindex) |

## Acceptance Criteria
- [x] CT-1: SKILL.md structure valid (frontmatter, version 5.0, tags)
- [x] CT-2: All 5 reference files present and have content (>50 chars each)
- [x] CT-3: RAG strategies enumerated (8+ strategies documented)
- [x] CT-4: Pipeline and audit module documented
- [x] CT-5: Repo reference: github.com/MarceloClaro/maswos-v5-nexus
- [x] CT-6: All references readable without errors
- [x] CT-7: SKILL.md > 200 chars (substantial content)

## RAG Strategies
1. Vanilla RAG
2. Memory RAG
3. Agentic RAG
4. Graph RAG
5. Hybrid RAG
6. CRAG (Corrective)
7. Adaptive RAG
8. Fusion RAG
9. HyDE (Hypothetical Document Embeddings)

## Test Coverage
- Location: `skills/maswos-v5-nexus/tests/test_maswos.py`
- Classes: 4 (Structure, References, Components, Available)
- Tests: 10+
