# Specs: MCPs — Model Context Protocol Servers

**Total:** 42 (27 ativos + 15 inativos/arquivados) | **Revisao:** 2026-07-04 (R43)

---

## MCPs Ativos (27)

### Core / Infraestrutura (5)
| MCP | Funcao | Comando |
|-----|--------|---------|
| **filesystem** | Acesso a filesystem local | `npx @modelcontextprotocol/server-filesystem` |
| **code-runner** | Execucao de codigo em sandbox | `mcp-server-code-runner` |
| **mcp-python-interpreter** | Interpretador Python com sessoes REPL | `mcp-python-interpreter` |
| **sqlite** | Banco SQLite para queries estruturadas | `mcp-server-sqlite` |
| **sequential-thinking** | Raciocinio multi-etapa com revisao | `node .../server-sequential-thinking` |

### Busca / Web (4)
| MCP | Funcao |
|-----|--------|
| **websearch** | DuckDuckGo search integrado |
| **fetch** | Fetch HTTP generico (HTML, JSON, Markdown) |
| **context7** | Documentacao de bibliotecas (Context7 API) — REMOTO |
| **wikipedia** ★ | Enciclopedia para background research (reativado R43) |

### Codigo / Qualidade (4)
| MCP | Funcao |
|-----|--------|
| **gh_grep** | Busca em codigo GitHub (grep.app) — REMOTO |
| **eslint** | Linting JavaScript/TypeScript |
| **diff** | Diff entre textos (unified diff) |
| **node-sandbox** | Sandbox Node.js isolado (Docker) |

### Browser / UI (1)
| MCP | Funcao |
|-----|--------|
| **playwright** | Automacao de browser (headless) |

### Sistema / Tempo (2)
| MCP | Funcao |
|-----|--------|
| **memory** | Knowledge graph persistente |
| **time** | Conversao de timezone, timestamps |

### Colaboracao (1)
| MCP | Funcao |
|-----|--------|
| **github** | GitHub API: repos, PRs, issues, commits (requer GITHUB_TOKEN) |

### Documentos (1)
| MCP | Funcao |
|-----|--------|
| **pdf** | Manipulacao de PDF: texto, watermark, header/footer |

### Academico (2)
| MCP | Funcao |
|-----|--------|
| **scihub** | Busca e download de artigos cientificos |
| **maswos-mcp** ★ | Orquestracao MASWOS (49 agentes akademico) |

### RAG / Contexto (1)
| MCP | Funcao |
|-----|--------|
| **maswos-rag** ★ | Retrieval-Augmented Generation para escrita academica |

### Ecossistema / Custom (3)
| MCP | Funcao |
|-----|--------|
| **decisionnode** | Memoria de decisoes entre ferramentas IA |
| **antigravity-mcp** ★ | Bridge Antigravity (Google DeepMind) — SPEC-046 |
| **self-healer** ★ | Auto-cura do ecossistema via heartbeat e reparo |

### Verificacao / Diagramas (2)
| MCP | Funcao |
|-----|--------|
| **cora-verifier** ★ | Verificacao simbolica de raciocinios e provas |
| **flowzap-mcp** ★ | Diagramas de arquitetura FlowZap |

### Noticias (1)
| MCP | Funcao |
|-----|--------|
| **hacker-news** ★ | Monitoramento de tendencias tech |

> ★ = Reativado no R43 com casos de uso documentados

---

## MCPs Inativos / Arquivados (15)

### Arquivados por sobreposicao (8)
| MCP | Funcao | Substituido por | Data Arquivamento |
|-----|--------|-----------------|:-----------------:|
| puppeteer | Browser automation | playwright | R43 |
| chrome-devtools | DevTools Chrome | playwright | R43 |
| desktop-commander | Automacao desktop | (escopo limitado) | R43 |
| shell-server | Shell remoto | bash tool | R43 |
| run-python | Python isolado | mcp-python-interpreter | R43 |
| mcp-server-commands | Comandos sistema | shell | R43 |
| mermaid | Diagramas Mermaid | flowzap-mcp | R43 |
| mem0-mcp | Memoria alternativa | memory | R43 |

### Mantidos inativos por dominio especifico (7)
| MCP | Funcao | Motivo |
|-----|--------|--------|
| biomcp | Bioinformatica | Dominio especifico — ativar sob demanda |
| biothings | Dados biologicos | Dominio especifico — ativar sob demanda |
| gget | Genomica | Dominio especifico — ativar sob demanda |
| opengenes | Genomica | Dominio especifico — ativar sob demanda |
| youtube-transcript | Transcricao YouTube | Manutencao instavel |
| astronomy-oracle | Astronomia | Dominio muito especifico |
| maswos-juridico | Juridico | Dominio especifico — ativar sob demanda |

---

## Criterios de Qualidade MCP

Todos os MCPs ativos devem satisfazer:
- [x] Health check responde em < 5s
- [x] Timeout configurado por operacao
- [x] Erros retornam mensagem descritiva (nao crasham)
- [x] Logging estruturado (JSON ou key=value)
- [x] Documentacao de ferramentas expostas

---

## Casos de Uso Ativos (R43)

| Caso de Uso | MCPs | Pipeline | Frequencia |
|-------------|------|----------|:----------:|
| Pesquisa Academica Rapida | wikipedia, scihub, seq-think | SEEKER → wikipedia → scihub → sintese | Por demanda |
| Monitoramento Tendencias | hacker-news, seq-think, memory | HN → analyzer → ecosystem-state | Diario |
| Diagramacao Arquitetura | flowzap, seq-think, memory | SPEC → flowzap → SVG/MD | Por release |
| Orquestracao Antigravity | antigravity, seq-think, decision | OpenCode → agy.exe → audit | Por demanda |
| Verificacao Simbolica | cora-verifier, seq-think, memory | raciocinio → verificacao → audit trail | Por operacao |
| Auto-Cura Ecossistema | self-healer, sqlite, decision | heartbeat → diagnose → repair | Continuo |
| Pipeline MASWOS | maswos-mcp, maswos-rag, cora, pdf | problema → RAG → MASWOS → qualis → pdf | Por projeto |
| Sintese G→V→R | wikipedia, HN, cora, seq-think, memory, flowzap | Generator → Verifier → Reviser | Por demanda |

---

## Referencias

- **MCP-Zero** (Fei et al., 2025): Active Tool Discovery — arXiv:2506.01056
- **MCP-Universe** (Luo et al., 2025): Benchmark 6 dominios — arXiv:2508.14704
- **ANX Protocol** (Mingze, 2026): Protocol-first design — arXiv:2604.04820
- **MCP Tool Descriptions** (Hasan et al., 2026): Qualidade de descricoes — arXiv:2602.14878
- **Agent Interoperability** (Ehtesham et al., 2025): MCP+A2A+ANP survey — arXiv:2505.02279
- **SPEC-R43**: Active MCP Discovery & Ecosystem Autonomy (`specs/SPEC-R43-ACTIVE-MCP-DISCOVERY.md`)
