# Curadoria — Codificação eficiente de alto nível e evolução de eficiência/autonomia

Levantamento estático em **14 de outubro de 2026**. Escopo: repositórios candidatos a
**aumentar eficiência de codificação** (contexto de código, harnesses de agente,
auto-evolução de skills) e a **ampliar autonomia real** do OpenCode Ecosystem Core.

**Relação com R886:** a avaliação `docs/AVALIACAO_REPOS_METACOGNICA_R886.md` cobre o eixo
*metacognição/orquestração* (memória tipada, decisão, sandbox, pesquisa). Este documento é
**complementar**: cobre o eixo *code-intelligence / codificação eficiente*, que aquele não
trata. Não repete candidatos nem substitui aquele levantamento.

## Método e limites

- Verificação por **fonte primária** quando possível: os arquivos de licença foram lidos
  diretamente no `raw.githubusercontent.com` (SHA/exemplo indicado). Onde não foi possível,
  o dado é marcado como **(não verificado)** ou **alegação do projeto**.
- **Nenhum** runtime externo foi instalado, executado, clonado ou testado nesta fase.
- Contagem de estrelas, versões e benchmarks **não foram confirmados** por API
  (`api.github.com` está bloqueado neste ambiente) e variam entre fontes de busca —
  portanto são omitidos ou explicitamente rotulados como não verificados.
- Ler código/documentação **não** equivale a integração, inferência ou validação externa.
  Alegações de redução de tokens e de speedup **pertencem aos projetos** e não foram
  reproduzidas.

## Trust gate aplicado

1. Licença declarada e lida na fonte primária; **sem LICENSE = `degraded`** (padrão R621).
2. Licença **copyleft forte em serviço de rede** (AGPL) ou **GPL** → **bloqueio** para
   incorporação direta no Core (mantém-se apenas como referência conceitual).
3. Exige API key/segredo obrigatório → só com ordem explícita do operador.
4. Sem instalação automática; federação só após spec própria, fixação de revisão e testes.

---

## Eixo A — Code-intelligence local via MCP (tree-sitter + grafo) — **prioridade**

Gap confirmado: o Core registra 16 MCPs (`opencode.json`), mas **nenhum** indexa o
repositório por AST/grafo de símbolos. É o eixo de maior alavancagem para **eficiência de
tokens** (leitura dirigida em vez de arquivo inteiro).

| Candidato | Licença (fonte primária) | Runtime | Mecanismo | Situação |
|---|---|---|---|---|
| `context-link-mcp/context-link` | **Apache-2.0** ✓ | Go 1.22+ (CGo + GCC) | tree-sitter → símbolos+grafo; SQLite FTS5 + KNN; MCP stdio | **recomendado** (binário, sem Python) |
| `cmillstead/codesight-mcp` | **MIT** ✓ | Python | tree-sitter, 66 linguagens, 34 operações, zero-DB (grafo em memória) | **recomendado** (funcionalidades ricas) |
| `padobrik/mcp-context-graph` | **MIT** ✓ | Python | tree-sitter + NetworkX, 6 tools, benchmark offline com `tiktoken` | **recomendado** (leve, auditável) |
| `maplenk/context-mcp` | **MIT** ✓ | Go | AST + PPR/BM25/betweenness, SQLite FTS5 + sqlite-vec | candidato |
| `g-tiwari/mcp-codebase-intelligence` | **MIT** ✓ | Node | tree-sitter, 18 tools, 8 linguagens, diagramas mermaid | candidato |
| `breca/mcp-codemap` | **GPL-3.0** (busca) | TypeScript | tree-sitter → SQLite, 3 tools | **bloqueado** (GPL) |
| `Elmoaid/TempoGraph` | **AGPL-3.0** (busca) | Python | tree-sitter → SQLite, 24 tools | **bloqueado** (AGPL/rede) |

Observações de risco:
- Muitos projetos publicam **benchmarks próprios** de redução (60–92% de tokens). São
  **alegações do projeto**, não medidas do Core; exigem reprodução local antes de adoção.
- Os projetos de licença permissiva acima são recentes (2026) e, em sua maioria, de baixa
  tração (estrelas não verificadas); risco de manutenção e de dependências nativas (CGo,
  Node, modelos de embedding locais) deve ser pesado.
- `codesight-mcp` e `tempo` citam *summaries* opcionais via API Anthropic — **desativar**
  por padrão (não introduzir chamada externa de custo).

Recomendação de integração (contrato, não execução):
1. Adotar **um** servidor de code-context federado por MCP, com escopo **read-only** sobre
   o repositório e índice em `.cache/` local.
2. Exigir métrica própria: rodar um task-set fixo com e sem o MCP e medir tokens/tool-calls
   **no Core** (anti-overclaim R110). Sem essa medição, não declarar ganho.
3. Preferir implementação sem rede (servidores locais) e sem chamadas a provedores pagos.

## Eixo B — Harnesses de agente de código (autonomia)

O Core já orquestra `claude` (CLI read-only), `codex` (interop Windows), `antigravity`
(`agy`) e recusa `opencode` externo por recursão. Adicionar um harness **não** amplia
capacidade sem modelo forte; a escolha é de *workflow e isolamento*.

| Candidato | Licença (fonte primária) | Papel | Observação |
|---|---|---|---|
| `All-Hands-AI/OpenHands` | **MIT** ✓ | Agente autônomo (sandbox Docker), ACP-compatível | `Agent Canvas` aceita agentes ACP, inclui OpenCode/Claude Code/Codex — poderia ser **backend**, mas exige Docker (indisponível aqui) |
| `Aider-AI/aider` | **Apache-2.0** ✓ | Par-programador terminal, **repomap tree-sitter**, auto-commit por edição | Relevante pelo **repomap**; último tag público antigo (cadência lenta) |
| `cline/cline` | Apache-2.0 (busca, não verificado) | Agente em IDE/CLI/SDK, aprovação por ação | Sem IDE no escopo atual |

Risco: sobreposição com os executores já existentes e com o **gate SDD/TDD** do Core. Se
adotado, deve entrar como *executor externo orquestrável* (padrão dos cards
`agents/catalog/*`), **nunca** como segundo coordenador.

## Eixo C — Auto-evolução de skills / memória procedimental

**Sobreposição forte com R886** (memória: `knowl`) e com o que o Core já tem (`Reflexion`,
MetaBus, agente `autoevolve`, `Blackboard`). Manter como **referência**, sem duplicar.

| Candidato | Licença (fonte primária) | Ideia aproveitável |
|---|---|---|
| `stanfordnlp/dspy` (+ **GEPA**) | MIT (amplamente conhecido, não reverificado aqui) | Otimização reflexiva de prompts/skills com métrica; **MIT**, encaixa no ciclo SDD/TDD |
| `ReflexioAI/reflexio` | **Apache-2.0** ✓ | Aprende com correções do usuário; integra mem0/OpenClaw |
| `vishnu-77/openreflex` | **MIT** ✓ | "Memória muscular" por hooks de ciclo de vida; suporta **OpenCode/Codex/Claude Code**; alerta de loop |
| `AnthonyRonning/reflex` | (não verificado) | Loop de auto-melhoria sobre **traces do Antigravity** (o Core usa `agy`) |

Recomendação: aproveitar **padrões** (métrica-primeiro, hooks de ciclo de vida, detecção de
loop) já no `autoevolve`/`reflexion` do Core, sem importar runtimes de terceiros.

## Eixo D — Eficiência de inferência (decodificação especulativa)

**Baixa prioridade agora:** o Core não tem GPU NVIDIA e usa **LiteRT-LM local**. Candidatos
(Apache-2.0/BSD) pressupõem GPU/serving — registrar como referência futura apenas.

- `vllm-project/speculators` (Apache-2.0), `huawei-csl/sssd_speculator` (BSD-3-Clause-Clear),
  `apple/ml-speculative-streaming`, `SqueezeAILab/QuantSpec`, `hao-ai-lab/JetSpec` (MIT).

---

## Ordem sugerida (com não-colisão)

1. **Eixo A** (code-context MCP) — maior ganho de eficiência, sem tocar o eixo R886.
2. **Eixo C** (padrões de auto-evolução) — só se não duplicar R886.
3. Eixos B/D — referência; B exige Docker (indisponível), D exige GPU (indisponível).

## O que exige autorização do operador

- **Instalar/clonar** qualquer candidato (nenhuma instalação foi feita).
- **Registrar MCP** no `opencode.json` (mudança de configuração do Core).
- **Registrar ciclo/spec** para a integração — evita colidir com o ciclo **R886**
  (workstream de metacognição ativo) e com escrita concorrente em `evolution/cycles.json`.
- Definir a **métrica de eficiência** (tokens/tool-calls) que servirá de gate.

> Nada aqui altera `TrustEngine`, `MetaBus`, estado epistêmico ou autorização. Candidato
> presente nesta lista **não** é capacidade entregue nem validada externamente.
