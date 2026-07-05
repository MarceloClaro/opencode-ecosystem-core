# SPEC-R43 — Active MCP Discovery & Ecosystem Autonomy

**Ciclo:** R43  
**Versao:** 1.0.0  
**Status:** SDD (Spec-Driven Development)  
**Fundamentacao:** MCP-Zero (arXiv:2506.01056), Aletheia (DeepMind 2026), MCP-Universe (arXiv:2508.14704), ANX Protocol (arXiv:2604.04820)  
**CTs Planejados:** 16  
**Total Ecossistema apos R43:** 459 CTs (443 + 16)

---

## Sumario Executivo

O ecossistema possui **42 MCPs configurados**, dos quais apenas **19 estao ativos** (45%) e **23 inativos** (55%). Baseado no framework **MCP-Zero** (Fei et al., 2025) — que propoe Active Tool Discovery com 98% de reducao de tokens — e na arquitetura **Aletheia** (Google DeepMind, 2026) — Generator → Verifier → Reviser com raciocinio metacognitivo — este ciclo ativa, integra e cria casos de uso reais para os MCPs ociosos, transformando-os em capacidade ecossistemica autonomamente descoberta.

### Referencias Academicas

| Paper | arXiv | Contribuicao |
|-------|-------|--------------|
| MCP-Zero | 2506.01056 | Active Tool Discovery, Hierarchical Semantic Routing, Iterative Capability Extension |
| MCP-Universe | 2508.14704 | Benchmark 6 dominios × 11 MCPs, execution-based evaluators |
| MCP Tool Descriptions | 2602.14878 | 97.1% descricoes com smells; augmentation melhora 5.85pp |
| ANX Protocol | 2604.04820 | Protocol-first, 3EX decoupled architecture, 47-66% reducao tokens |
| Agent Interoperability | 2505.02279 | MCP + A2A + ANP survey, phased adoption roadmap |
| Aletheia (DeepMind) | — | Generator→Verifier→Reviser loop, scaling laws, 95.1% IMO-Proof |

---

## Estrutura em 4 Camadas

### Camada 1: MCP Inventory & Health Audit (CT-01 a CT-04)

Diagnostico completo do ecossistema MCP:

| MCP | Status Atual | Categoria | Decisao R43 |
|-----|-------------|-----------|-------------|
| filesystem | ✅ ativo | Core | Manter |
| code-runner | ✅ ativo | Core | Manter |
| mcp-python-interpreter | ✅ ativo | Core | Manter |
| sqlite | ✅ ativo | Core | Manter |
| sequential-thinking | ✅ ativo | Core | Manter |
| websearch | ✅ ativo | Busca | Manter |
| fetch | ✅ ativo | Busca | Manter |
| context7 | ✅ ativo | Busca | Manter |
| gh_grep | ✅ ativo | Codigo | Manter |
| eslint | ✅ ativo | Codigo | Manter |
| diff | ✅ ativo | Codigo | Manter |
| node-sandbox | ✅ ativo | Codigo | Manter |
| playwright | ✅ ativo | Browser | Manter |
| memory | ✅ ativo | Sistema | Manter |
| time | ✅ ativo | Sistema | Manter |
| decisionnode | ✅ ativo | Ecossistema | Manter |
| pdf | ✅ ativo | Documentos | Manter |
| scihub | ✅ ativo | Academico | Manter |
| **github** | ❌ erro | Colaboracao | **Fix: GITHUB_TOKEN** |
| **wikipedia** | ⏹️ inativo | Busca | **Ativar** |
| **hacker-news** | ⏹️ inativo | Noticias | **Ativar** |
| **flowzap-mcp** | ⏹️ inativo | Diagramas | **Ativar** |
| **antigravity-mcp** | ⏹️ inativo | Orquestracao | **Ativar** |
| **cora-verifier** | ⏹️ inativo | Verificacao | **Ativar** |
| **self-healer** | ⏹️ inativo | Auto-cura | **Ativar** |
| **maswos-mcp** | ⏹️ inativo | Academico | **Ativar** |
| **maswos-rag** | ⏹️ inativo | RAG | **Ativar** |
| puppeteer | ⏹️ inativo | Browser | Arquivar (overlap playwright) |
| chrome-devtools | ⏹️ inativo | Browser | Arquivar (overlap playwright) |
| desktop-commander | ⏹️ inativo | Desktop | Arquivar (escopo limitado) |
| shell-server | ⏹️ inativo | Shell | Arquivar (overlap bash) |
| run-python | ⏹️ inativo | Python | Arquivar (overlap mcp-python-interpreter) |
| mcp-server-commands | ⏹️ inativo | Comandos | Arquivar (overlap shell) |
| mermaid | ⏹️ inativo | Diagramas | Arquivar (overlap flowzap) |
| mem0-mcp | ⏹️ inativo | Memoria | Arquivar (overlap memory) |
| biomcp | ⏹️ inativo | Bioinfo | Manter inativo (domain-specific) |
| biothings | ⏹️ inativo | Bioinfo | Manter inativo (domain-specific) |
| gget | ⏹️ inativo | Bioinfo | Manter inativo (domain-specific) |
| opengenes | ⏹️ inativo | Bioinfo | Manter inativo (domain-specific) |
| youtube-transcript | ⏹️ inativo | Midia | Manter inativo (instavel) |
| astronomy-oracle | ⏹️ inativo | Astronomia | Manter inativo (domain-specific) |
| maswos-juridico | ⏹️ inativo | Juridico | Manter inativo (domain-specific) |

### Camada 2: Active Discovery Engine (CT-05 a CT-08)

Implementa o **Active Tool Request** do MCP-Zero com 3 mecanismos:

```
MCP-Zero Framework (Fei et al., 2025)
├── Active Tool Request
│   ├── Model requests tools on-demand
│   ├── Structured JSON-RPC schema
│   └── Capability gap detection
├── Hierarchical Semantic Routing
│   ├── Stage 1: Server-level matching
│   ├── Stage 2: Tool-level matching
│   └── Semantic alignment score
└── Iterative Capability Extension
    ├── Progressive toolchain building
    ├── Minimal context footprint
    └── 98% token reduction vs baseline
```

**Componentes do ActiveDiscoveryEngine:**

1. **CapabilityGapDetector** — Identifica lacunas entre requisicoes e MCPs disponiveis
2. **SemanticRouter** — Roteamento hierarquico servidor→ferramenta com score de alinhamento
3. **ToolchainBuilder** — Constroi cadeias de ferramentas incrementais
4. **ContextOptimizer** — Mantem pegada de contexto minima (inspirado no ANX Protocol)

### Camada 3: Metacognitive Integration (CT-09 a CT-11)

Integra o loop **Generator→Verifier→Reviser** do Aletheia com os MCPs ativados:

```
Fluxo Metacognitivo com MCPs:
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  PROBLEMA   │───▶│  GENERATOR   │───▶│   VERIFIER   │
│  (entrada)  │    │  (LLM +      │    │  (cora-      │
│             │    │   wikipedia, │    │   verifier,  │
│             │    │   hacker-    │    │   sequential-│
│             │    │   news,      │    │   thinking)  │
│             │    │   scihub)    │    │              │
└─────────────┘    └──────────────┘    └──────────────┘
                           ▲                  │
                           │    ┌──────────────┘
                           │    ▼
                        ┌──────────────┐
                        │   REVISER    │
                        │  (flowzap,   │
                        │   memory,    │
                        │   decision-  │
                        │   node)      │
                        └──────────────┘
```

**Padrao de Integracao:**
- **Generator** usa MCPs de busca (wikipedia, scihub, hacker-news) para reunir informacao
- **Verifier** usa MCPs de verificacao (cora-verifier, sequential-thinking) para validar
- **Reviser** usa MCPs de persistencia (memory, decisionnode) e diagramacao (flowzap)

### Camada 4: Casos de Uso Concretos (CT-12 a CT-16)

| MCP | Caso de Uso | Pipeline | Frequencia |
|-----|-------------|----------|------------|
| **wikipedia** | Background research rapido para SEEKER | SEEKER → wikipedia → resumo | On-demand |
| **hacker-news** | Monitoramento de tendencias tech para evolucao | HN → analyzer → ecosystem-state.json | Diario |
| **flowzap-mcp** | Diagramas de arquitetura para documentacao | SPEC → flowzap → SVG/MD | Por release |
| **antigravity-mcp** | Orquestracao externa de agentes (SPEC-046) | OpenCode → agy.exe → resultados | Por demanda |
| **cora-verifier** | Verificacao simbolica de provas/raciocinios | reasoning → cora-verifier → audit | Por operacao |
| **self-healer** | Auto-cura de componentes do ecossistema | heartbeat → diagnose → repair | Continuo |
| **maswos-mcp** | Pipeline academico multi-agente | problema → 49 agentes → artigo | Por projeto |
| **maswos-rag** | Retrieval-Augmented Generation para escrita | query → RAG → contexto enriquecido | Por artigo |

---

## Especificacao de Testes (16 CTs)

### Grupo A: Inventory & Audit (CT-01 a CT-04)
- CT-01: Inventory report gera categorizacao correta dos 42 MCPs
- CT-02: Health audit detecta 23 inativos e 1 com erro
- CT-03: Classificacao (manter/ativar/arquivar) completa
- CT-04: Relatorio de auditoria e exportavel como JSON

### Grupo B: Active Discovery (CT-05 a CT-08)
- CT-05: CapabilityGapDetector identifica lacuna entre requisicao e MCPs
- CT-06: SemanticRouter retorna score > 0.7 para match correto
- CT-07: ToolchainBuilder cria sequencia 3+ ferramentas
- CT-08: ContextOptimizer reduz tokens em pelo menos 50%

### Grupo C: Metacognitive Integration (CT-09 a CT-11)
- CT-09: Generator→Verifier→Reviser loop executa com MCPs reais
- CT-10: Verifier usa cora-verifier OU sequential-thinking como fallback
- CT-11: Reviser persiste resultado em memory + decisionnode

### Grupo D: Casos de Uso (CT-12 a CT-16)
- CT-12: wikipedia MCP responde com resumo de topico cientifico
- CT-13: hacker-news MCP retorna top stories formatadas
- CT-14: flowzap-mcp cria diagrama valido a partir de descricao
- CT-15: Comando `python nexus/mcp_active_discovery.py --scan` funciona sem erros
- CT-16: Comando `python nexus/mcp_active_discovery.py --use-cases` lista 8+ casos

---

## Criterios de Aceitacao

1. **16/16 CTs PASS** (GREEN)
2. Active Discovery Engine rodando sem erros
3. 8 MCPs ativados com casos de uso documentados
4. 1 MCP com erro corrigido (github: GITHUB_TOKEN)
5. MCPs arquivados documentados no catalogo
6. Compatibilidade retroativa: 443 CTs anteriores continuam PASS
