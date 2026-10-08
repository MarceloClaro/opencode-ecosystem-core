---
name: awesome-mcp-servers
description: >-
  Curadoria executável da lista wong2/awesome-mcp-servers (SPEC-935-R652).
  Política referência-primeiro: servidores modelcontextprotocol sem auth
  (fetch, sequential-thinking, filesystem) já registrados no opencode.json;
  SaaS com API key só caso a caso com trust gate. Use para receitas de
  instalação (uvx/npx) e para decidir o que federar.
policy:
  allow_implicit_invocation: false
  disable-model-invocation: false
round: R652
spec: SPEC-935-R652-awesome-mcp-servers.md
---

# Skill: Awesome MCP Servers (SPEC-935-R652)

## Já registrados (provados ao vivo em 2026-10-04)

| MCP | Comando | Prova |
|---|---|---|
| `fetch` | `uvx mcp-server-fetch` | conteúdo real de example.com |
| `sequential-thinking` | `npx -y @modelcontextprotocol/server-sequential-thinking` | thought registrada |
| `filesystem` | `npx .../server-filesystem <repo>` | allowlist confirmada |

## Registrados em 2026-10-07 (R704, testados ao vivo)

| MCP | Comando | Prova | Uso no Core |
|---|---|---|---|
| `arxiv-mcp` | `uvx arxiv-mcp-server` | 19 tools via stdio + busca real retornando papers | `tdah-gap-hunter`: `search_papers`, `export_citations` (BibTeX), `get_paper_latex_section` |
| `latexmk-mcp` | `npx -y latexmk-mcp` | 11 tools via stdio | `abnt-latex-modular`: `latexmk_compile`, `latexmk_list_citations`, `latexmk_check` |

Trust: `arxiv-mcp-server` Apache-2.0 + PyPI + MCP Registry, sem auth obrigatória (chave Semantic Scholar opcional); `latexmk-mcp` MIT v1.1.3 + npm + CI, sem auth.

## Receitas

```bash
uvx mcp-server-fetch                    # Python, sem auth
npx -y @modelcontextprotocol/server-sequential-thinking
npx -y @modelcontextprotocol/server-filesystem /caminho/escopo
```

## Trust gate (Official/Community SaaS)

1. Exige API key/segredo? → só com ordem explícita do operador.
2. Licença declarada? Sem LICENSE = degraded (padrão R621).
3. `.mcp.json` do plugin lido antes de registrar.

## Adiado com motivo

- `memory` (KG): sobrepõe MetaBus — SPEC própria futura.
- `git`/`time`: bash cobre.
- `mcp-latex` (marcelogdomingues): pacote sumiu do npm (404) — reavaliar se republicar; alternativa `latexmk-mcp` já cobre.
- `san-rat/latex-mcp`: exige CLSI do Overleaf via Docker — pesado demais; adiado.
- Orquestradores externos (`jpicklyk/task-orchestrator`, `Oortonaut/task-graph-mcp`, `ZhuchenZhong/TaskFlow`): sobrepõem Blackboard/A2A do Core — referência, sem instalar.
- Skills acadêmicas (referência, sem vendored code): `Calix-L/awesome-latex-skills` (latex-rescue, paper-read), `Yila-AI/awesome-research-skills` (Claim-Strength Contract p/ anti-overclaim, research-presentation), `tahaturkistanli-ctrl/agent-research-skills` (literature-search: Semantic Scholar/arXiv/OpenAlex/Crossref), `bahayonghang/academic-writing-skills` (paper-audit, online_bib_verify sem API key). Instalar por skill conforme necessidade, com checagem de licença antes.
