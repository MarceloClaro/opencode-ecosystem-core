# OpenCode Ecosystem Core

Bem-vindo ao **OpenCode Ecosystem Core**, uma versão limpa, portável e focada na orquestração metacognitiva do ecossistema OpenCode. Este repositório centraliza a operação no orquestrador `marceloclaro` e implementa duas camadas de estado da arte: a **Metacognitive Interconnect (MCI)** e a **Transformer Layer**.

## A Camada Transformer (Inspirada em Vaswani et al. e Google DeepMind)

A orquestração do ecossistema mapeia conceitos da arquitetura Transformer diretamente para o fluxo multiagente. Esta camada foi inspirada nas pesquisas do [DeepMind](https://github.com/MarceloClaro/deepmind-research) e na equipe [Superhuman Reasoning](https://github.com/MarceloClaro/superhuman):

- **Task Embedder**: Converte tarefas e capacidades de agentes em vetores densos (hashing de features d=64 com *positional encoding* senoidal).
- **Attention Router (Multi-Head)**: Em vez de escolher agentes aleatoriamente, o orquestrador usa atenção com 4 "cabeças" (semântica, capacidade, confiança e carga) para rankear o agente ideal para a tarefa (inspirado no *Perceiver* e *PrediNet*).
- **Transformer Pipeline**: Cada tarefa passa por um *encoder stack* com o ciclo **Gerar → Verificar → Revisar** (inspirado no agente *Aletheia* do DeepMind), com conexões residuais que preservam o histórico de correções.
- **Grading Head**: Uma cabeça de avaliação que pontua saídas de 0 a 7 (inspirado no *IMO-GradingBench*).
- **Hierarchical Memory**: Recuperação de memórias em dois níveis (atenção grossa sobre sumários de *chunks* e atenção fina sobre eventos), inspirado no *Hierarchical Transformer Memory (HTM)*.

## Subsistemas Avançados

O ecossistema integra os seguintes subsistemas avançados (portados do repositório OpenCode_Ecosystem original):

- **MiroFish (Swarm Intelligence)**: Motor preditivo baseado em enxame ("wisdom of crowds"). Agentes com vieses distintos (otimista, pessimista, contrário) emitem previsões que convergem em um debate Delphi, triplamente validado por Teoria dos Jogos e auditoria acadêmica.
- **Game Theory & 38 Raciocínios**: Catálogo formal de 38 tipos de raciocínio (lógica clássica, dialética, Teoria dos Jogos). Inclui solver de Equilíbrio de Nash puro, Valor de Shapley, e um `MetaReasoner` que seleciona a estratégia ideal por contexto.
- **Produção Científica (Pasta Única)**: Pipeline de publicação que converte a fonte Markdown canônica em LaTeX (usando templates Qualis A1, abnTeX2 ou livros KDP-ready) e compila automaticamente para PDF, DOCX, MD e ODT, gerando um manifesto com checksums SHA-256 para total rastreabilidade.
- **Trust Engine & Token Economy**: Segurança comportamental (BehavioralGate, NaturalForgetting) e mercado de agentes (staking, slashing, fee market).
- **Scanners de Diagnóstico**: Pipeline com 5 scanners (Noológico, Teleológico, Evolutivo, Potentiality, Social Impact).
- **MASWOS (Qualis A1)**: Pipeline acadêmico multiagente com 16 estágios e gate de aprovação rigoroso.
- **Motores de Raciocínio & Quantum**: Solvers lógicos (Z3, SymPy, Kanren) e simulador quântico reproduzível (Bell, GHZ).

## O que é a Metacognitive Interconnect (MCI)?

A MCI é uma camada arquitetural desenhada para resolver o problema de "metacognição em silos" em sistemas multiagentes. Baseada no estado da arte da pesquisa em IA, ela garante que a metacognição (a habilidade de pensar sobre o próprio pensamento, avaliar confiança e aprender com erros) circule entre **todos** os agentes.

A MCI é composta por:
- **MetaBus**: Um barramento de eventos unificado baseado na *Global Workspace Theory* [1].
- **Memória Metacognitiva Compartilhada**: Memória episódica (rastros) e semântica (lições aprendidas) acessível a todos [2].
- **Blackboard & Agent Cards (A2A)**: Um quadro negro dinâmico onde agentes se voluntariam para tarefas baseados em suas capacidades declaradas [3][4].
- **Reflexion Middleware**: Um motor que força a auto-reflexão pós-execução, alimentando um *Confidence Ledger* (livro-razão de confiança) [5].

## SDD e TDD: Metodologia Orientada a Especificação e Testes

Todos os componentes e agentes do ecossistema operam estritamente sob as metodologias **Specification-Driven Development (SDD)** e **Test-Driven Development (TDD)**:

- **SpecRegistry e SpecVerifier**: Cada componente possui uma especificação formal (arquivos `specs/SPEC-*.md`) com invariantes e critérios de aceitação verificáveis.
- **Delegação SDD-First**: O orquestrador `marceloclaro` cria uma especificação (TSPEC) *antes* de delegar qualquer tarefa. No **modo estrito**, entregas que não satisfazem 100% dos critérios são automaticamente rejeitadas (Gate SDD).
- **Ciclo TDD (Red-Green-Refactor)**: Os agentes executam o ciclo TDD integrado ao pipeline Transformer. Refatorações que quebram critérios estabelecidos são revertidas.
- **Metacognição de Código**: O orquestrador roda a bateria `pytest` real do repositório e registra os resultados no Global Workspace, permitindo que os agentes aprendam com falhas estruturais.

## Estrutura do Repositório

- `marceloclaro/`: O orquestrador central e seu CLI interativo.
- `transformer/`: A nova camada de orquestração (Attention, Pipeline, Embedder, HTM Memory).
- `mci/`: A camada Metacognitive Interconnect (MetaBus, Blackboard, Reflexion, MCP Server).
- `sdd/`: O motor de especificações e TDD Runner (SpecVerifier, SpecRegistry).
- `trust/`: Trust Engine com BehavioralGate e NaturalForgetting.
- `economy/`: Token Economy (staking, slashing, fee market).
- `scanners/`: Pipeline de diagnóstico (Noológico, Teleológico, Evolutivo, etc.).
- `academic/`: Pipeline MASWOS Qualis A1 com gate AUTO_SCORE.
- `reasoning/`: Motores de raciocínio lógico e simulador quântico.
- `evolution/`: Registro de ciclos evolutivos.
- `integrations/`: Integração com OpenCode CLI e Antigravity.
- `gametheory/`: 38 tipos de raciocínio, Equilíbrio de Nash, auditoria PhD.
- `mirofish/`: Enxame preditivo (Swarm Intelligence) e CrossValidator.
- `publishing/`: Pipeline de pasta única (LaTeX, PDF, DOCX, ODT) e templates.
- `specs/`: Especificações formais (SDD nativas e acervo de rastreabilidade original).
- `agents/`: 134 agentes no total (incluindo catálogo de 130 especializados).
- `examples/`: Scripts de demonstração end-to-end.
- `tests/`: Bateria de testes automatizados (pytest).

## Quickstart

### 1. Requisitos
- Python 3.10+
- (Opcional) `pytest` para rodar a bateria de testes.

```bash
pip install -r requirements.txt
```

### 2. Rodando os Demos End-to-End
Veja a metacognição e a camada Transformer em ação:

```bash
python3 examples/demo_full_ecosystem.py # Demo completa: Trust, Economy, MASWOS, Scanners, Quantum
python3 examples/demo_publishing.py     # Demo: Pasta Única de Produção Científica (LaTeX/KDP)
python3 examples/demo_sdd_tdd.py        # Ciclo Red-Green-Refactor e Gate SDD Estrito
python3 examples/demo_transformer.py    # Atenção, Pipeline Gerar-Revisar e HTM Memory
python3 examples/demo_pipeline.py       # Fluxo MCI clássico (Blackboard + Reflexion)
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
[6] Vaswani, A., et al. (2017). *Attention Is All You Need*. arXiv:1706.03762.  
[7] Google DeepMind. (2025). *Superhuman Reasoning Team: Aletheia & IMO-Bench*. Repositório.  
[8] Google DeepMind. (2024). *DeepMind Research: Perceiver, HTM, PrediNet*. Repositório.
