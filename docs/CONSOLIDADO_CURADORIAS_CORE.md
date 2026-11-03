# Consolidado geral das curadorias para o Core (até 14 de outubro de 2026)

## Escopo e método

Este consolidado sintetiza as curadorias existentes no repositório:
- `docs/CURADORIA_CODIFICACAO_EFICIENTE.md` — codificação eficiente, pesquisa científica → redação (artigos/teses/dissertações/livros) → LaTeX profissional → diagramação editorial + diagramas
- `docs/AVALIACAO_CODE_INTELLIGENCE_R887.md` — avaliação estática de code-intelligence MCP (piloto R887)
- `docs/AVALIACAO_REPOS_METACOGNICA_R886.md` — metacognição/orquestração (memória tipada, decisão, sandbox, pesquisa) — workstream ativo
- `docs/AVALIACAO_BROWSER_MCP_AI_RESEARCHER.md` — MCPs para navegador/pesquisa (Playwright/CDP)
- `docs/AVALIACAO_PROJETOS_NSA.md` — projetos NSA/relacionados (verificação estática)

Regra geral: avaliação **estática** por fonte primária; **nenhuma** instalação/execução neste levantamento; acusações de desempenho são alegações dos projetos (não reproduzidas); privilégios, rede e instalação exigem autorização explícita.

## 1) Metacognição / Orquestração — R886 (ativo)

Foco: conexões internas entre memória canônica, reflexão, raciocínio e delegação pelo MarceloClaroOrchestrator.

| Candidato | Licença | Papel recomendado | Status |
|---|---|---|---|
| `laya` (fork + upstream NandhaKishorM) | Apache-2.0 | Conselho auxiliar (tipado), não altera TrustEngine/autorização | Candidato após calibração local |
| `knowl` (fork + upstream dat999zx) | Apache-2.0 | **Memória tipada opcional — 1ª prioridade**; schema com proveniência/supersedidos | Piloto possível; não substitui MetaBus |
| `awesome-llm-apps` (Shubhamsaboo) | Apache-2.0 | **Referência seletiva** (contratos RAG, multi-MCP, corrective RAG) | Não instalar coleção |
| `OpenShell` (NVIDIA) | Apache-2.0 | Sandbox opcional de execução; exige Docker/Podman, WSL experimental | Backend opcional conservador |
| `feynman` (Companion-Inc) | MIT | Especialista opcional de pesquisa; distinguir de `reversa_feynman` já existente | Delimitado por orçamento/rede |

Principais critérios: coordenação única (orquestrador), MetaBus permanece canônico; conselho/modelo → distinto de evidência observada; fallback explícito; instalação controlada.

## 2) Code-intelligence local (MCP) — R887

Gap: nenhum MCP de AST/grafo indexado no Core. Alavanca maior: leitura estruturada → eficiência de tokens.

| Candidato | Licença | Runtime | Status |
|---|---|---|---|
| `context-link-mcp/context-link` | Apache-2.0 ✓ | Go 1.24+ (binário, CGo) | **Recomendado p/ piloto R887** (bypass Python 3.14, read-only, contratos de ferramentas) |
| `cmillstead/codesight-mcp` | MIT ✓ | Python | Alternativa (66 linguagens, rico) |
| `padobrik/mcp-context-graph` | MIT ✓ | Python | Leve, benchmark offline com tiktoken |
| `maplenk/context-mcp` | MIT ✓ | Go | Híbrido PPR/BM25/betweenness + sqlite-vec |
| `g-tiwari/mcp-codebase-intelligence` | MIT ✓ | Node | 18 tools, Mermaid |
| `breca/mcp-codemap` | GPL-3.0 | TypeScript | Bloqueado (GPL) |
| `Elmoaid/TempoGraph` | AGPL-3.0 | Python | Bloqueado (AGPL/rede) |

Premissas R887: testar **somente** context-link primeiro; fixar revisão (`e5af49c`), checksum asset `v1.1.0` (sha256 verificado localmente), confinamento de índices, whitelist de consultas; medir tokens/tool-calls no Core antes de declarar ganho (anti-overclaim).

## 3) Pesquisa científica → redação → LaTeX → diagramação editorial → diagramas

Cobre artigos/teses/dissertações/livros com LaTeX profissional e diagramação editorial.

### 3.1 Descoberta + RAG rastreável
| Candidato | Licença | Finalidade | Notas |
|---|---|---|---|
| `openalex/openalex-api` + `PyAlex` | MIT/CC0 | Descoberta (works/authors) OA-first | Sem chave obrigatória |
| `allenai/s2orc` | ODC-BY/variantes | Corpus referencial | Usar apenas corpus já licenciado |
| `RAGFlow/RAGFlow` | Apache-2.0 | RAG com citações por chunk/OCR | Self-host, read-first; controlar conectores |
| `neuml/txtai` | Apache-2.0 | RAG híbrido local | Leve, alto ROI |
| `llmware-ai/llmware` | Apache-2.0 | RAG p/ textos longos (teses) | Citações rastreáveis |

### 3.2 Markdown → LaTeX + ABNT + qualidade
| Candidato | Licença | Finalidade | Notas |
|---|---|---|---|
| `jgm/pandoc` | GPL-2.0+ | Universal (Markdown→LaTeX) | **Invocação CLI externa** (não embutir) |
| `pandoc/pandoc-crossref` | GPL-2.0 | Numeração cruzada | Requer pandoc |
| `quarto-dev/quarto-cli` | GPL-3.0 | Artigos/teses/livros (capítulos) | Ótimo p/ diagramação editorial; **CLI externo** |
| `abntex/abntex2` | LPPL-1.3c | ABNT | Compatível com uso LaTeX |
| `Wandmalfarbe/pandoc-latex-template` (Eisvogel) | MIT | Template limpo | Perfeito p/ artigos |
| `google-research/arxiv-latex-cleaner` | Apache-2.0 | Limpeza p/ arXiv | Pipeline útil |
| `tectonic-typesetting/tectonic` | Apache-2.0 | Compilador auto-contido | Builds herméticos/reprodutíveis (alternativa ao TeXLive gigante) |

### 3.3 Diagramação editorial (livros/teses)
| Candidato | Licença | Finalidade | Notas |
|---|---|---|---|
| `typst/typst` | Apache-2.0 | Layout declarativo, rápido | **Muito recomendado** (Apache-2.0, cobre ABNT na comunidade) |
| `sile-typesetter/sile` | MIT | Tipografia avançada (verso/reto, grids) | Excelência editorial, MIT |
| `mdBook` | MPL-2.0 | Manuais técnicos | Permissivo, menos flexível p/ normas acadêmicas rígidas |
| `vivliostyle/vivliostyle.js` | AGPL-3.0 | CSS Paged Media → PDF | Bloqueador p/ incorporação |
| `WeasyPrint` | BSD-3-Clause | HTML+CSS → PDF | Permissivo, bom para casos simples |

### 3.4 Diagramas/vetoriais
| Candidato | Licença | Finalidade | Notas |
|---|---|---|---|
| `mermaid-js/mermaid-cli` | MIT | Mermaid → SVG/PNG/PDF | Vetorial limpo |
| `jgraph/drawio` | Apache-2.0 | draw.io export | Ideal editorial |
| `cairosvg/cairosvg` | BSD | SVG→PDF | Permissivo |
| `pgf-tikz/pgf` + `pgfplots` | LPPL-1.3c | Matemáticos/científicos | Padrão LaTeX |
| `plantuml/plantuml`, `inkscape` | GPL | CLI externo OK | Não embutir como derivado |

**Recomendado integração:** `OpenAlex+txtai/LLMware+markitdown` (pesquisa/rastreabilidade) + `pandoc+crossref+abntex2/Eisvogel` ou `Typst` (LaTeX/profissional) + `Quarto` (livros/teses estruturados, via CLI externo) + `tectonic` (builds reprodutíveis) + `mermaid-cli+drawio+CairoSVG` (diagramas). Usar ferramentas GPL/AGPL **apenas por invocação CLI externa**, com recibos/hashes.

## 4) Browser/MCP AI Researcher (navegação automatizada, pontual)

`docs/AVALIACAO_BROWSER_MCP_AI_RESEARCHER.md`: avalia MCPs para navegação (Playwright/CDP), pesquisa e captura. Considerar apenas se necessário a acessos OA ou páginas dinâmicas, com consentimento explícito e política de rede; não substituir OpenAlex/arXiv. Manter read-only e auditável.

## 5) Projetos NSA / verificação

`docs/AVALIACAO_PROJETOS_NSA.md`: horizonte de verificação estática/auxiliar. Apenas referência; não instalar.

## Priorização consolidada (menos colisão)

1. **R886 — Metacognição** (ativo): consolidar loop interno primeiro; avaliar `knowl` opcionalmente, com separação clara de autoridade.
2. **R887 — Code-intelligence**: piloto `context-link` (Apache-2.0, binário) — medir tokens/tool-calls antes de declarar ganho.
3. **Pesquisa→LaTeX→Editorial**: priorizar `txtai+OpenAlex+markitdown` + `pandoc+Typst/Quarto` + `tectonic` — cobertura completa do pedido, com licença majoritariamente permissiva (GPLs tratados via CLI externo).

## Guardrails (aplicam-se a todos)

- **Não instala automaticamente**. Tudo via proposta/spec, autorização explícita, fixação de revisão/asset e checksum.
- **Licenças**: AGPL/GPL → invocação externa; preferir Apache-2.0/MIT/LPPL/BSD.
- **Separação de estados**: conselho (modelo) ≠ evidência observada ≠ confiança (TrustEngine). MetaBus canônico.
- **Anti-overclaim** (R110): nenhuma alegação de "qualis A1", verificado, superhuman sem validação externa. Ganhos devem ser medidos no Core.
- **Fail-closed**: indisponibilidade → limitação explícita, nunca execução simulada.
- **Rede**: controle explícito; OA-first (OpenAlex/arXiv/acesso-aberto-auditoria já existem).

## 6) Notebooker (man-group/notebooker)

Avaliado sob demanda (14 de outubro de 2026).

| Campo | Valor |
|---|---|
| Repositório | `man-group/notebooker` |
| Descrição | "Productionise & schedule your Jupyter Notebooks as easily as you wrote them." — webapp para executar/parametrizar notebooks (papermill/nbconvert), armazenar resultados em MongoDB, interface web. |
| Default branch | `master` |
| Licença (fonte primária, via API) | **AGPL-3.0** (`LICENSE.txt`) |

Observações:
- **AGPL-3.0**: copyleft forte; se usado como **serviço de rede** (webapp exposto), exige disponibilização do código-fonte aos usuários da interface. Se integrado como **execução externa isolada** (CLI/serviço separado, sem incorporar código), pode ser viável — mas exige cuidado.
- Arquitetura: webapp + CLI (`notebooker-cli`, `notebooker_execute`), depende de Jupyter/papermill/nbconvert, MongoDB. Requer stack extra.
- **Não recomendado** para incorporação direta no Core. Apenas referência; se houver necessidade real de "programar/schedulear notebooks como relatórios", avaliar via **execução externa orquestrável** com política de rede/privacidade.

Fit com pedido: marginal p/ "diagramação editorial de artigos/teses/livros". Foco é operacional (agendar/executar notebooks), não tipografia/editorial. Core já tem ferramentas de exportação LaTeX/editorial (pandoc/quarto/typst/sile/tectonic). **Prioridade baixa**.

---

## Conclusão

1. **Metacognição (R886)** — ativa; `knowl` potencial memória tipada (não substituir MetaBus).
2. **Code-intelligence (R887)** — piloto `context-link` (Apache-2.0, binário) primeiro.
3. **Pesquisa→LaTeX→Editorial** — melhor cobertura: `txtai+OpenAlex+markitdown` + `pandoc+Typst/Quarto (CLI externo)` + `tectonic` + `mermaid-cli+drawio+CairoSVG`. `SILE` (MIT) forte p/ tipografia avançada. `notebooker` (AGPL) não agrega ao pipeline editorial e tem sobreposição baixa.
