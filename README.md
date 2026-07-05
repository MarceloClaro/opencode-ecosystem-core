# OpenCode Ecosystem Core

Bem-vindo ao **OpenCode Ecosystem Core**, uma versão limpa, portável e focada na orquestração metacognitiva do ecossistema OpenCode. Este repositório centraliza a operação no orquestrador `marceloclaro` e implementa a camada **Metacognitive Interconnect (MCI)**.

## O que é a Metacognitive Interconnect (MCI)?

A MCI é uma camada arquitetural desenhada para resolver o problema de "metacognição em silos" em sistemas multiagentes. Baseada no estado da arte da pesquisa em IA, ela garante que a metacognição (a habilidade de pensar sobre o próprio pensamento, avaliar confiança e aprender com erros) circule entre **todos** os agentes.

A MCI é composta por:
- **MetaBus**: Um barramento de eventos unificado baseado na *Global Workspace Theory* [1].
- **Memória Metacognitiva Compartilhada**: Memória episódica (rastros) e semântica (lições aprendidas) acessível a todos [2].
- **Blackboard & Agent Cards (A2A)**: Um quadro negro dinâmico onde agentes se voluntariam para tarefas baseados em suas capacidades declaradas [3][4].
- **Reflexion Middleware**: Um motor que força a auto-reflexão pós-execução, alimentando um *Confidence Ledger* (livro-razão de confiança) [5].

## Estrutura do Repositório

- `marceloclaro/`: O orquestrador central e seu CLI interativo.
- `mci/`: A camada Metacognitive Interconnect (MetaBus, Blackboard, Reflexion, MCP Server).
- `agents/`: Definições dos agentes em Markdown (com frontmatter YAML para Agent Cards).
- `examples/`: Scripts de demonstração end-to-end.
- `tests/`: Bateria de testes automatizados (pytest).

## Quickstart

### 1. Requisitos
- Python 3.10+
- (Opcional) `pytest` para rodar a bateria de testes.

```bash
pip install -r requirements.txt
```

### 2. Rodando o Demo End-to-End
Veja a metacognição em ação: o orquestrador carrega os agentes, consulta a memória, delega tarefas via Blackboard, e os agentes refletem sobre os resultados.

```bash
python3 examples/demo_pipeline.py
```

### 3. CLI Interativo
O ecossistema possui um menu de terminal amigável para operar o orquestrador `marceloclaro`:

```bash
python3 -m marceloclaro.cli
```

### 4. Integração MCP (Model Context Protocol)
A camada MCI expõe um servidor MCP para que ferramentas externas (como o Antigravity ou o Claude) possam interagir com o Global Workspace.
O arquivo `opencode.json` já está configurado. Para iniciar o servidor standalone:

```bash
python3 mci/mcp_server.py
```

## Arquitetura
Para um mergulho profundo na arquitetura, consulte o [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Referências

[1] Baars, B. J. (1988). *A cognitive theory of consciousness*. Cambridge University Press.  
[2] Anônimo. (2025). *Multi-User Memory Sharing in LLM Agents with Dynamic Access*. arXiv:2505.18279.  
[3] Salemi, A., et al. (2025). *LLM-Based Multi-Agent Blackboard System for Information Discovery in Data Science*. arXiv:2510.01285.  
[4] Ehtesham, A., et al. (2025). *A Survey of Agent Interoperability Protocols*. arXiv:2505.02279.  
[5] Shinn, N., et al. (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning*. arXiv:2303.11366.
