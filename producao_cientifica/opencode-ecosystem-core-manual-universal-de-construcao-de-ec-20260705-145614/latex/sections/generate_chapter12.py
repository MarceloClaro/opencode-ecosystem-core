#!/usr/bin/env python3
"""Generate capitulo12.tex for the OpenCode Ecosystem Core Manual."""

import os

OUTPUT = os.path.join(os.path.dirname(__file__), "capitulo12.tex")

def write_chapter():
    parts = []
    
    # ============ PART 1: Header through Section 12.1 ============
    parts.append(r"""% ======================================================================
% CAPÍTULO 12 — PRÁXIS
% Construindo, Customizando e Publicando seu Próprio Ecossistema Cognitivo
% OpenCode Ecosystem Core: Manual Universal de Construção de Ecossistemas Metacognitivos
% Autor: Prof. Marcelo Claro
% ======================================================================

\chapter{Práxis — Construindo, Customizando e Publicando seu Próprio Ecossistema Cognitivo}
\label{chap:praxis}

\begin{quote}
\textit{``A teoria sem prática é contemplação estéril. A prática sem teoria é exercício cego. A metacognição é a ponte entre ambas, e o OpenCode Ecosystem Core é sua expressão técnica.''}
\end{quote}

\section{Introdução à Práxis Metacognitiva}
\label{sec:praxis-intro}

Ao longo dos onze capítulos anteriores, percorremos uma jornada intelectual que partiu dos fundamentos históricos e filosóficos da inteligência artificial (Capítulo 1), atravessou o impacto social e econômico dos ecossistemas cognitivos (Capítulo 2), consolidou os fundamentos matemáticos e estatísticos que sustentam arquiteturas como o Transformer (Capítulos 3 e 4), estabeleceu os princípios de engenharia de software para sistemas multiagentes (Capítulo 5), mergulhou na IA metacognitiva (Capítulo 6), detalhou a arquitetura completa do OpenCode Ecosystem Core (Capítulo 7), fundamentou os protocolos SDD/TDD e o pipeline de qualidade (Capítulo 8), explorou a metacognição, o Reflexion Framework e a Global Workspace Theory (Capítulo 9), analisou a token economy e os mecanismos de teoria dos jogos (Capítulo 10) e, finalmente, dissecou o pipeline acadêmico MASWOS e o rigor Qualis A1 (Capítulo 11).

Agora, neste décimo segundo e último capítulo, o leitor é convidado a transcender o papel de estudante e assumir o de \textbf{construtor}. Este é o momento da \textbf{práxis} --- conceito aristotélico que designa a ação informada pela teoria, a atividade que transforma o conhecimento em realidade concreta. Cada seção, cada listagem de código, cada exercício foi extraído diretamente do repositório \texttt{opencode-ecosystem-core} e testado com \texttt{pytest}. Não há pseudocódigo neste capítulo: todo fragmento aqui apresentado é código Python executável que roda em qualquer máquina Linux com Python 3.10+.

A estrutura deste capítulo reflete uma jornada progressiva de autonomia cognitiva, organizada em seis seções principais que cobrem o ciclo completo de adoção de um ecossistema metacognitivo:

\begin{enumerate}[leftmargin=*, label=(\arabic*)]
  \item \textbf{Tutorial Passo a Passo} (Seção~\ref{sec:tutorial}) --- da instalação do ambiente, passando pelo \texttt{git clone} e configuração do \texttt{opencode.json}, até a primeira produção científica automatizada com o pipeline MASWOS. O leitor aprenderá a inicializar o ecossistema, registrar agentes, delegar tarefas via Blackboard e gerar uma publicação acadêmica completa em PDF, DOCX e ODT.
  \item \textbf{Exercícios Práticos com Código Real} (Seção~\ref{sec:exercicios}) --- 10 exercícios graduais, do nível iniciante ao PhD, cada um com enunciado claro, dicas e referências bibliográficas, solução comentada linha a linha e padrão de correção objetivo. Os exercícios cobrem MetaBus (pub/sub), memória metacognitiva (confidence ledger), Blackboard (ciclo completo de delegação), SDD/TDD (especificação executável), orquestrador (delegação com todos os gates), scanners (diagnóstico profundo), token economy (staking/slashing), attention routing (multi-head), MASWOS (pipeline acadêmico completo) e cross-validation (MiroFish + Nash + Qualis A1).
  \item \textbf{Customização de Agentes e Criação de Novos Módulos} (Seção~\ref{sec:customizacao}) --- criação de agent cards seguindo o padrão A2A, registro programático no Blackboard, adição de novos scanners ao pipeline de diagnóstico, implementação de motores de raciocínio customizados, e integração de módulos externos via MCP (Model Context Protocol).
  \item \textbf{Publicação Acadêmica Automatizada com MASWOS} (Seção~\ref{sec:maswos-tutorial}) --- tutorial completo cobrindo os 16 estágios do pipeline, a rubrica AUTO\_SCORE\_QUALIS com seus 10 critérios e pesos, geração de PDF/DOCX com pandoc e LaTeX, checklist de conformidade para submissão a periódicos Qualis A1, e integração com o subsistema de pesquisa (ResearchHub).
  \item \textbf{Deploy, Monitoramento e Evolução Contínua} (Seção~\ref{sec:deploy}) --- containerização com Docker, pipeline CI/CD com GitHub Actions, métricas de saúde do ecossistema (7 dimensões), ciclos evolutivos documentados, e exportação de métricas para Prometheus/Grafana.
  \item \textbf{Referências e Recursos Adicionais} (Seção~\ref{sec:refs-praxis}) --- referências completas com DOI e links ativos, glossário de 25 termos técnicos da práxis, recursos online, e o desafio final integrador.
\end{enumerate}

\subsection{Pré-requisitos de Leitura e Competências}
\label{sec:prereqs}

Este capítulo pressupõe familiaridade com os conceitos nucleares introduzidos nos capítulos anteriores. Em particular, o leitor deve estar confortável com:

\begin{itemize}
  \item A arquitetura MetaBus + Blackboard + Reflexion que constitui a camada MCI (Metacognitive Interconnect), detalhada no Capítulo 9. O MetaBus implementa o barramento de eventos pub/sub que conecta todos os subsistemas; o Blackboard gerencia o quadro negro compartilhado onde agentes se voluntariam para tarefas; e o Reflexion Engine orquestra as auto-reflexões pós-execução.
  \item O protocolo SDD/TDD e o ciclo RED-GREEN-REFACTOR, estabelecidos no Capítulo 8. Toda implementação no ecossistema segue este ciclo: primeiro especifica-se os critérios de aceitação (RED), depois implementa-se a entrega mínima que os satisfaz (GREEN), e finalmente refatora-se mantendo os critérios verdes (REFACTOR).
  \item A estrutura do orquestrador \texttt{marceloclaro} e seus subsistemas --- Trust Engine, Token Economy, Scanners, MASWOS, Reasoning Engines, Evolution Registry --- apresentados no Capítulo 7. O orquestrador é o ponto de entrada único para todas as operações do ecossistema.
  \item Conceitos fundamentais de sistemas multiagentes, incluindo o padrão Blackboard \citep{guo2025blackboard}, o protocolo Agent-to-Agent (A2A), e a Global Workspace Theory \citep{baars1997global}.
\end{itemize}

Caso o leitor esteja iniciando diretamente por este capítulo prático, recomendamos veementemente a leitura prévia ao menos das Seções 7.1 (Visão Geral da Arquitetura) e 8.1 (Protocolo SDD/TDD) para contextualização adequada. O ecossistema é coeso: cada componente depende dos fundamentos estabelecidos nos capítulos anteriores.

\subsection{Convenções e Notação}
\label{sec:convencoes}

Ao longo deste capítulo, adotamos as seguintes convenções:

\begin{itemize}
  \item \textbf{Listagens de código}: Todos os trechos de código são apresentados em blocos \texttt{lstlisting} com numeração de linhas. Código que deve ser digitado pelo leitor é precedido pelo símbolo \texttt{\$} (prompt do shell) quando se trata de comandos bash, ou apresentado como bloco Python completo quando se trata de scripts.
  \item \textbf{Saídas esperadas}: Quando relevante, a saída esperada da execução é apresentada em bloco separado, identificada como ``Saída esperada''.
  \item \textbf{Referências}: Citações seguem o padrão ABNT NBR 10520:2023 (autor-data) no texto e ABNT NBR 6023:2018 nas referências. DOIs são fornecidos como URLs ativas clicáveis.
  \item \textbf{Caminhos de arquivo}: Caminhos relativos à raiz do repositório (\texttt{opencode-ecosystem-core/}) são indicados sem prefixo. Caminhos absolutos são indicados com \texttt{/}.
  \item \textbf{Nomes de classes e métodos}: \texttt{ClassNames} em teletype para classes, \texttt{method\_names()} para métodos e funções, \texttt{MODULE\_NAMES} para módulos.
\end{itemize}

\subsection{Visão Geral da Jornada Prática}
\label{sec:visao-geral}

A Figura~\ref{fig:praxis-journey} resume visualmente a jornada de aprendizado proposta neste capítulo. Cada marco representa uma competência adquirida, e as setas indicam as dependências entre elas.

\begin{figure}[H]
\centering
\begin{tikzpicture}[
    milestone/.style={draw, rounded corners, minimum width=3.2cm, minimum height=1cm, align=center, font=\small\bfseries},
    arrow/.style={->, >=stealth, thick, color=blue!60}
]
\node[milestone, fill=green!15] (m1) at (0,8) {1. Instalação\\e Configuração};
\node[milestone, fill=green!15] (m2) at (5,8) {2. Primeiro Agente\\Customizado};
\node[milestone, fill=yellow!15] (m3) at (0,6) {3. MetaBus \&\\Blackboard};
\node[milestone, fill=yellow!15] (m4) at (5,6) {4. SDD/TDD\\Executável};
\node[milestone, fill=orange!15] (m5) at (0,4) {5. Delegação\\Meta-cognitiva};
\node[milestone, fill=orange!15] (m6) at (5,4) {6. Pipeline de\\Diagnóstico};
\node[milestone, fill=red!15] (m7) at (0,2) {7. Token Economy\\Staking/Slashing};
\node[milestone, fill=red!15] (m8) at (5,2) {8. Attention\\Routing};
\node[milestone, fill=purple!15] (m9) at (0,0) {9. MASWOS\\Qualis A1};
\node[milestone, fill=purple!15] (m10) at (5,0) {10. Cross-Validation\\MiroFish+Nash};

\draw[arrow] (m1) -- (m2);
\draw[arrow] (m1) -- (m3);
\draw[arrow] (m2) -- (m4);
\draw[arrow] (m3) -- (m5);
\draw[arrow] (m4) -- (m5);
\draw[arrow] (m5) -- (m6);
\draw[arrow] (m6) -- (m7);
\draw[arrow] (m6) -- (m8);
\draw[arrow] (m7) -- (m9);
\draw[arrow] (m8) -- (m9);
\draw[arrow] (m9) -- (m10);

\node[font=\footnotesize, align=left] at (-3,8) {\textbf{Iniciante}};
\node[font=\footnotesize, align=left] at (-3,5) {\textbf{Intermediário}};
\node[font=\footnotesize, align=left] at (-3,3) {\textbf{Avançado}};
\node[font=\footnotesize, align=left] at (-3,0) {\textbf{PhD}};
\end{tikzpicture}
\caption{Jornada de aprendizado do Capítulo 12: 10 marcos de competência progressiva}
\label{fig:praxis-journey}
\end{figure}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\section{Tutorial Passo a Passo --- Do \texttt{git clone} à Primeira Produção Científica Automatizada}
\label{sec:tutorial}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Esta seção constitui o tutorial principal do capítulo. Em aproximadamente duas horas, o leitor partirá de uma máquina Linux limpa até a produção automatizada de um artigo científico com qualidade Qualis A1. O tutorial é autocontido: todos os comandos, scripts e configurações necessários são fornecidos integralmente.

Ao final deste tutorial, o leitor terá:
\begin{itemize}
  \item O ecossistema OpenCode Ecosystem Core instalado e funcional, com 128+ agentes registrados no Blackboard e todos os subsistemas operacionais (Trust Engine, Token Economy, Scanners, MASWOS, Reasoning Engines, Evolution Registry, ResearchHub, Publishing).
  \item Executado uma delegação metacognitiva completa --- percepção (consulta à memória global) $\to$ delegação (Blackboard + Trust Gate + Attention Routing + Token Economy) $\to$ reflexão (Reflexion Engine + Confidence Ledger).
  \item Rodado o pipeline de diagnóstico com os 5 scanners (Noológico, Teleológico, Potencialidade, Impacto Social, Reversa) e, opcionalmente, o modo profundo com roadmap evolutivo M1-M5.
  \item Gerado um artigo acadêmico com o pipeline MASWOS completo (16 estágios), aprovado pelo gate Qualis A1 (nota $\ge$ 8.0/10).
  \item Publicado o artigo em PDF, DOCX, ODT e Markdown, com manifesto auditável (SHA-256) e estrutura LaTeX modularizada.
\end{itemize}

\subsection{Instalação --- Preparando o Ambiente}
\label{sec:instalacao}

\subsubsection{Requisitos de Sistema}

O OpenCode Ecosystem Core é um sistema Python puro, desenvolvido com Python 3.10+ e utilizando exclusivamente a biblioteca padrão (\texttt{stdlib}) para seus componentes centrais: a camada MCI (MetaBus, Blackboard, Reflexion), o orquestrador \texttt{marceloclaro}, os scanners, o Trust Engine, a Token Economy e o Evolution Registry. Esta decisão arquitetural --- \textbf{zero dependências externas obrigatórias para o núcleo} --- foi deliberada para maximizar a portabilidade e minimizar a superfície de quebra por incompatibilidade de versões.

Dependências opcionais enriquecem funcionalidades específicas, mas o ecossistema foi projetado para degradar graciosamente quando elas estão ausentes: se o \texttt{pandoc} não estiver instalado, os formatos DOCX e ODT não serão gerados, mas o Markdown e o LaTeX permanecem funcionais; se o \texttt{latexmk} não estiver disponível, o PDF não será compilado, mas a fonte LaTeX é gerada corretamente.

\begin{table}[H]
\centering
\caption{Requisitos de sistema e dependências}
\label{tab:requisitos}
\begin{tabular}{@{}llll@{}}
\toprule
\textbf{Componente} & \textbf{Versão Mínima} & \textbf{Obrigatório?} & \textbf{Função} \\
\midrule
Python & 3.10 & Sim & Runtime principal \\
pip & 23.0 & Sim & Gerenciador de pacotes \\
pytest & 7.0+ & Sim (testes) & Framework de testes \\
git & 2.30+ & Sim & Controle de versão \\
pandoc & 3.1+ & Opcional & Conversão MD$\to$DOCX/ODT/PDF \\
\LaTeX{} (texlive) & 2023+ & Opcional & Compilação PDF nativo \\
Ollama & 0.1.20+ & Opcional & LLM local (raciocínio offline) \\
Docker & 24+ & Opcional & Containerização \\
Docker Compose & 2.20+ & Opcional & Orquestração de containers \\
GNU Make & 4.0+ & Opcional & Automação de build \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection{Verificação do Ambiente}

Antes de iniciar a instalação, verifique se seu ambiente atende aos requisitos mínimos:

\begin{lstlisting}[language=bash,caption={Verificação de pré-requisitos},label={lst:check-prereqs}]
# Verificar Python
python3 --version
# Saída esperada: Python 3.10.x ou superior

# Verificar pip
pip --version
# Saída esperada: pip 23.x ou superior

# Verificar git
git --version
# Saída esperada: git version 2.30.x ou superior

# Verificar espaço em disco (mínimo 500MB recomendado)
df -h .
\end{lstlisting}

\subsubsection{Clonagem e Configuração Inicial}

O processo de instalação é direto e consiste em clonar o repositório, criar um ambiente virtual Python e instalar as dependências:

\begin{lstlisting}[language=bash,caption={Clonagem, ambiente virtual e instalação de dependências},label={lst:clone}]
# 1. Clonar o repositório oficial
git clone https://github.com/MarceloClaro/opencode-ecosystem-core.git
cd opencode-ecosystem-core

# 2. Criar e ativar ambiente virtual Python (isolamento de dependências)
python3 -m venv .venv
source .venv/bin/activate

# 3. Atualizar pip para a versão mais recente
pip install --upgrade pip

# 4. Instalar dependências obrigatórias
pip install -r requirements.txt

# 5. (Opcional mas recomendado) Instalar pytest e plugins de cobertura
pip install pytest pytest-cov pytest-xdist

# 6. Verificar a instalação do núcleo
python3 -c "
from mci.metabus import metabus
from mci.blackboard import blackboard
from mci.reflexion import reflexion_engine
print('MetaBus:', type(metabus).__name__)
print('Blackboard:', type(blackboard).__name__)
print('ReflexionEngine:', type(reflexion_engine).__name__)
print('Instalação do núcleo MCI: OK')
"

# 7. Executar a bateria completa de testes
pytest tests/ -v --tb=short
\end{lstlisting}

A saída esperada do passo 6 confirma que os três componentes da camada MCI estão operacionais:

\begin{lstlisting}[caption={Saída esperada da verificação do núcleo MCI}]
MetaBus: MetaBus
Blackboard: Blackboard
ReflexionEngine: ReflexionEngine
Instalação do núcleo MCI: OK
\end{lstlisting}

A saída do passo 7 deve mostrar todos os 27+ testes passando:

\begin{lstlisting}[caption={Saída esperada do pytest (27+ testes)}]
tests/test_ecosystem.py::test_metabus_publish_subscribe PASSED
tests/test_ecosystem.py::test_memory_reflection_updates_confidence PASSED
tests/test_ecosystem.py::test_agent_loader_reads_frontmatter PASSED
tests/test_ecosystem.py::test_blackboard_full_cycle PASSED
tests/test_ecosystem.py::test_failed_task_lowers_confidence PASSED
tests/test_sdd_tdd.py::test_spec_registry_loads_formal_specs PASSED
tests/test_sdd_tdd.py::test_spec_verifier_validates_criteria PASSED
tests/test_sdd_tdd.py::test_tdd_cycle_red_green_refactor PASSED
tests/test_ecosystem.py::test_delegate_creates_task PASSED
tests/test_ecosystem.py::test_trust_engine_gate_allows_trusted PASSED
tests/test_ecosystem.py::test_token_economy_staking_slashing PASSED
tests/test_ecosystem.py::test_scanner_pipeline_runs_all_five PASSED
tests/test_ecosystem.py::test_maswos_pipeline_stages_sequence PASSED
tests/test_ecosystem.py::test_reasoning_engines_all_available PASSED
tests/test_ecosystem.py::test_evolution_cycle_recorded PASSED
tests/test_ecosystem.py::test_attention_router_ranking PASSED
tests/test_ecosystem.py::test_research_hub_search PASSED
tests/test_ecosystem.py::test_full_delegation_cycle PASSED
tests/test_ecosystem.py::test_status_report_complete PASSED
tests/test_ecosystem.py::test_deep_diagnose_mode PASSED
tests/test_ecosystem.py::test_scientific_production_complete PASSED
tests/test_ecosystem.py::test_mirofish_swarm_converges PASSED
tests/test_ecosystem.py::test_gametheory_nash_equilibrium PASSED
tests/test_ecosystem.py::test_publishing_pipeline_formats PASSED
tests/test_ecosystem.py::test_illustrations_generation PASSED
tests/test_ecosystem.py::test_antigravity_integration PASSED
tests/test_ecosystem.py::test_full_ecosystem_smoke PASSED
==================== 27 passed in 2.34s ====================
\end{lstlisting}

\subsubsection{Instalação do Ollama (Opcional)}
\label{sec:ollama-install}

O Ollama permite executar modelos de linguagem localmente, sem depender de APIs externas. Isto é particularmente útil para raciocínio metacognitivo offline, geração de reflexões com LLM real (em vez da simulação heurística do Reflexion Engine) e fichamentos enriquecidos no ResearchHub.

\begin{lstlisting}[language=bash,caption={Instalação e configuração do Ollama},label={lst:ollama}]
# Linux / WSL2
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar o serviço
ollama serve

# Baixar modelos recomendados (em outro terminal)
ollama pull llama3.2      # ~2.0GB --- modelo leve e rápido
ollama pull mistral        # ~4.1GB --- bom equilíbrio qualidade/velocidade
ollama pull deepseek-coder-v2  # ~8.0GB --- especializado em código

# Verificar modelos disponíveis
ollama list
\end{lstlisting}

Com o Ollama instalado, o ecossistema automaticamente detecta sua presença e prioriza modelos locais sobre APIs externas quando \texttt{use\_llm=True} é especificado em operações de pesquisa, fichamento ou raciocínio.

\subsubsection{Estrutura de Diretórios e Arquitetura de Arquivos}

Após a clonagem, o leitor encontrará uma estrutura de diretórios organizada por subsistema. A compreensão desta estrutura é fundamental para navegar o código e realizar customizações. A seguir, apresentamos a árvore completa comentada:

\begin{lstlisting}[caption={Estrutura completa de diretórios do ecossistema},label={lst:dirs}]
opencode-ecosystem-core/
|-- mci/                         # Metacognitive Interconnect (camada central)
|   |-- __init__.py              #   Exporta metabus, blackboard, reflexion_engine
|   |-- metabus.py               #   MetaBus: Global Workspace pub/sub + Memória
|   |-- blackboard.py            #   Blackboard A2A: Agent Cards + CFP + delegação
|   |-- reflexion.py             #   Reflexion Middleware (Shinn et al. 2023)
|   `-- mcp_server.py            #   Servidor MCP (JSON-RPC 2.0 sobre stdio)
|
|-- marceloclaro/                # Orquestrador Central
|   |-- __init__.py              #   Exporta MarceloClaroOrchestrator
|   |-- orchestrator.py          #   Orquestrador supremo (747 linhas, 40+ métodos)
|   |-- agent_loader.py          #   Carregador de agentes (frontmatter YAML)
|   |-- catalog_loader.py        #   Catálogo de 128+ agentes especializados
|   `-- cli.py                   #   Interface de linha de comando
|
|-- agents/                      # Definições dos Agentes (Agent Cards A2A)
|   |-- coder.md                 #   Agente core: implementação Python
|   |-- researcher.md            #   Agente core: pesquisa e síntese
|   |-- academic_writer.md       #   Agente core: redação acadêmica
|   |-- auditor.md               #   Agente core: auditoria e compliance
|   |-- reviewer.md              #   Agente core: revisão de código
|   `-- catalog/                 #   128+ agentes MASWOS + especializados
|
|-- transformer/                 # Camada Transformer
|   |-- __init__.py
|   |-- attention.py             #   AttentionRouter: multi-head (4 cabeças)
|   |-- embedder.py              #   TaskEmbedder: vetorização d=64
|   |-- memory.py                #   HierarchicalMemory: recuperação 2 níveis
|   `-- pipeline.py              #   TransformerPipeline: encoder stack
|
|-- sdd/                         # SDD/TDD Engine
|   |-- __init__.py
|   |-- spec_engine.py           #   SpecRegistry + SpecVerifier
|   `-- tdd_runner.py            #   TDDRunner: ciclo RED->GREEN->REFACTOR
|
|-- trust/                       # Trust Engine (SPEC-038)
|   |-- __init__.py
|   `-- trust_engine.py          #   TrustScorer + BehavioralGate + Forgetting
|
|-- economy/                     # Token Economy (SPEC-022 a SPEC-025)
|   |-- __init__.py
|   `-- token_economy.py         #   Ledger + Staking + Slashing + FeeMarket
|
|-- scanners/                    # Pipeline de Diagnóstico (SPEC-009)
|   |-- __init__.py
|   |-- pipeline.py              #   DiagnosticPipeline (5 scanners + modo profundo)
|   |-- noological_scanner.py    #   Cobertura epistemológica
|   |-- teleological_scanner.py  #   Lacunas meta->capacidade
|   |-- potentiality_scanner.py  #   Potenciais latentes
|   |-- social_impact_scanner.py #   SROI, ToC, SDG, B-Impact
|   |-- reversa_scanner.py       #   Engenharia reversa
|   |-- epistemic_prioritizer.py #   Priorização: erro->ausência->oportunidade
|   |-- successor_generator.py   #   Sucessores plausíveis (DNA estrutural)
|   |-- evolutionary_pipeline.py #   Roadmap M1-M5 com trajetórias
|   `-- cross_validation_engine.py # Validação cruzada entre scanners
|
|-- academic/                    # Pipeline MASWOS (SPEC-010)
|   |-- __init__.py
|   |-- maswos.py                #   MaswosPipeline: 16 estágios canônicos
|   |-- auto_score_qualis.py     #   Rubrica de 10 critérios com pesos
|   `-- seeker.py                #   SEEKER: busca acadêmica federada
|
|-- reasoning/                   # Motores de Raciocínio (SPEC-011)
|   |-- __init__.py
|   |-- engines.py               #   4 motores: Z3, SymPy, Kanren, Critical
|   `-- quantum.py               #   Suite quântica reprodutível
|
|-- evolution/                   # Ciclos Evolutivos (SPEC-012)
|   |-- __init__.py
|   |-- cycles.py                #   EvolutionRegistry: R1-R47+
|   `-- cycles.json              #   Persistência dos ciclos
|
|-- research/                    # ResearchHub (SPEC-017)
|   |-- __init__.py
|   |-- hub.py                   #   Pipeline: busca->download->fichamento->resenha
|   |-- searchers.py             #   MultiSearcher: arXiv, OpenAlex, Crossref...
|   |-- downloader.py            #   PaperDownloader: scihub-cli + OA direto
|   |-- pdf2md.py                #   Pdf2Markdown: conversão PDF->MD
|   |-- fichamento.py            #   Fichamento 3 camadas + resenha crítica
|   `-- llm_client.py            #   Cliente LLM unificado (Ollama/OpenAI)
|
|-- publishing/                  # ScientificProduction (SPEC-018)
|   |-- __init__.py
|   |-- production.py            #   Pasta única: LaTeX+PDF+DOCX+ODT+MANIFEST
|   |-- cover_designer.py        #   Design de capa para livros
|   `-- templates/               #   Templates LaTeX (artigo, dissertação, livro)
|
|-- gametheory/                  # Teoria dos Jogos
|   |-- __init__.py
|   |-- moderator.py             #   MetaReasoner: 38 estratégias de raciocínio
|   |-- debate_strategies.py     #   PayoffMatrix + Nash equilibria
|   `-- phd_auditor.py           #   Auditoria de teses com teoria dos jogos
|
|-- mirofish/                    # Enxame Preditivo
|   |-- __init__.py
|   |-- swarm.py                 #   MiroFish Swarm: wisdom of crowds
|   |-- validator.py             #   CrossValidator: tripla validação
|   `-- graph_memory.py          #   GraphMemory: memória relacional do enxame
|
|-- illustrations/               # Ilustrações Científicas
|   |-- __init__.py
|   |-- mermaid_engine.py        #   Diagramas Mermaid a partir de outline
|   |-- graphify_engine.py       #   Grafos de conhecimento
|   `-- mira_engine.py           #   Cards MIRA animados
|
|-- integrations/                # Integrações Externas
|   |-- __init__.py
|   |-- opencode_cli.py          #   Interface com OpenCode CLI
|   `-- antigravity/             #   Antigravity Bridge (SPEC-046)
|
|-- tests/                       # Bateria de Testes (27+)
|   |-- test_ecosystem.py        #   Testes do núcleo MCI + orquestrador
|   |-- test_sdd_tdd.py          #   Testes SDD/TDD
|   |-- test_advanced_subsystems.py # Testes dos subsistemas avançados
|   |-- test_research.py         #   Testes do ResearchHub
|   |-- test_cover_designer.py   #   Testes de capa
|   |-- test_illustrations.py    #   Testes de ilustrações
|   |-- test_mirofish_gametheory_publishing.py  # Testes integrados
|   |-- test_deep_diagnose.py    #   Testes do modo profundo
|   |-- test_llm_client.py       #   Testes do cliente LLM
|   `-- test_transformer.py      #   Testes do TransformerPipeline
|
|-- examples/                    # Demonstrações Executáveis
|   |-- demo_full_ecosystem.py   #   Demo completa end-to-end
|   |-- demo_sdd_tdd.py          #   Demo do ciclo SDD/TDD
|   |-- demo_pipeline.py         #   Demo do Transformer Pipeline
|   |-- demo_publishing.py       #   Demo de publicação científica
|   |-- demo_research.py         #   Demo de pesquisa acadêmica
|   |-- demo_illustrations.py    #   Demo de ilustrações
|   `-- demo_deep_diagnose.py    #   Demo de diagnóstico profundo
|
|-- specs/                       # Especificações Formais
|   |-- INDEX.md                 #   Índice de rastreabilidade
|   |-- SPEC-001-metabus.md      #   Especificação do MetaBus
|   |-- SPEC-002-blackboard.md   #   Especificação do Blackboard
|   |-- ...                      #   SPEC-003 a SPEC-046
|   `-- legacy/                  #   Acervo legado (SPECs originais portados)
|
|-- opencode.json                # Configuração central do OpenCode
|-- requirements.txt             # Dependências Python (pytest>=7.0.0)
|-- ARCHITECTURE.md              # Documentação da arquitetura
|-- README.md                    # README principal
|-- CHANGELOG.md                 # Histórico de versões
|-- LICENSE                      # Licença (MIT)
`-- .mci_state/                  # Estado metacognitivo persistente (runtime)
    |-- shared_memory.json       #   Memória episódica + semântica + confidence ledger
    `-- metabus_events.jsonl     #   Log append-only de eventos do MetaBus
\end{lstlisting}

\subsection{Configuração do \texttt{opencode.json}}
\label{sec:opencode-json}

O arquivo \texttt{opencode.json}, localizado na raiz do repositório, é o ponto único de configuração do ecossistema. Ele controla três dimensões fundamentais: (1) definição e permissões dos agentes, (2) servidores MCP para integração de ferramentas externas, e (3) comandos personalizados do usuário.

\begin{lstlisting}[language=json,caption={Estrutura essencial do opencode.json (comentada)},label={lst:opencode-json-core}]
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "opencode",
  "instructions": ["AGENTS.md"],
  "agent": {
    "marceloclaro": {
      "description": "Orquestrador central metacognitivo do ecossistema",
      "mode": "primary",
      "prompt": "{file:./marceloclaro/PROMPT.md}",
      "tools": { "write": true, "edit": true, "bash": true }
    },
    "coder": {
      "description": "Agente de implementação de código Python",
      "mode": "subagent",
      "prompt": "{file:./agents/coder.md}",
      "tools": { "write": true, "edit": true, "bash": true }
    },
    "researcher": {
      "description": "Agente de pesquisa científica e síntese de literatura",
      "mode": "subagent",
      "prompt": "{file:./agents/researcher.md}",
      "tools": { "write": true, "edit": true, "bash": true }
    }
  },
  "mcp": {
    "metacognitive-interconnect": {
      "type": "local",
      "command": ["python3", "mci/mcp_server.py"],
      "enabled": true
    },
    "antigravity-bridge": {
      "type": "local",
      "command": ["python3", "integrations/antigravity/antigravity_mcp_server.py"],
      "enabled": true
    }
  },
  "command": {
    "diagnose": {
      "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from scanners import diagnostic_pipeline; import json; print(json.dumps(diagnostic_pipeline.run(open('$ARGUMENTS').read() if '$ARGUMENTS' else 'ecosystem'), ensure_ascii=False, indent=2))\"",
      "description": "Roda o pipeline de diagnóstico (5 scanners)"
    },
    "maswos": {
      "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from academic import maswos_pipeline; print(maswos_pipeline.run('$ARGUMENTS').summary())\"",
      "description": "Executa o pipeline acadêmico MASWOS Qualis A1"
    },
    "reason": {
      "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from reasoning import multi_reasoning; r = multi_reasoning.reason('$ARGUMENTS'); print(r.engine, '->', r.conclusion)\"",
      "description": "Raciocina sobre uma consulta com roteamento automático"
    },
    "economy": {
      "template": "python3 -c \"import sys; sys.path.insert(0,'.'); from economy import token_economy; import json; print(json.dumps(token_economy.report(), ensure_ascii=False, indent=2))\"",
      "description": "Relatório da economia de tokens (staking, slashing, fees)"
    }
  }
}
\end{lstlisting}

\subsubsection{Bloco \texttt{agent}: Definindo Agentes}

Cada entrada no bloco \texttt{"agent"} define um agente com os seguintes campos:

\begin{itemize}
  \item \texttt{description}: descrição textual do papel do agente. Usada pelo AttentionRouter para matching semântico. Deve ser informativa e conter palavras-chave das capacidades relevantes.
  \item \texttt{mode}: \texttt{"primary"} para o orquestrador principal (apenas um por ecossistema) ou \texttt{"subagent"} para agentes delegáveis.
  \item \texttt{prompt}: caminho para o arquivo de system prompt do agente, usando a sintaxe \texttt{\{file:./caminho/arquivo.md\}}. O arquivo deve conter frontmatter YAML com \texttt{id}, \texttt{name}, \texttt{description} e \texttt{capabilities}.
  \item \texttt{tools}: permissões de ferramentas concedidas ao agente (\texttt{write}, \texttt{edit}, \texttt{bash}). O princípio do menor privilégio recomenda conceder apenas as ferramentas estritamente necessárias para a função do agente.
\end{itemize}

O frontmatter YAML de cada agente segue o padrão Agent Card do protocolo A2A \citep{google2025a2a}:

\begin{lstlisting}[language=yaml,caption={Exemplo de frontmatter de um Agent Card},label={lst:agent-card-yaml}]
---
id: coder
name: Coder
description: Agente de implementação de código Python, refatoração e depuração.
capabilities: [python, debug, refactor, implement]
---
\end{lstlisting}

\subsubsection{Bloco \texttt{mcp}: Integração de Ferramentas Externas}

O Model Context Protocol (MCP) é o padrão de integração do ecossistema. Cada servidor MCP é definido por:

\begin{itemize}
  \item \texttt{type}: \texttt{"local"} para processos locais (comunicação via stdio usando JSON-RPC 2.0) ou \texttt{"remote"} para servidores HTTP. O tipo \texttt{local} é o padrão recomendado para ferramentas que rodam na mesma máquina.
  \item \texttt{command}: array com o comando de inicialização do servidor (ex.: \texttt{["python3", "mci/mcp\_server.py"]}). O servidor deve implementar os métodos \texttt{tools/list} e \texttt{tools/call} do protocolo MCP.
  \item \texttt{enabled}: booleano que permite ativar/desativar servidores sem removê-los da configuração, útil para debugging e testes de integração.
\end{itemize}

O servidor MCP do MCI --- definido em \texttt{mci/mcp\_server.py} --- expõe ao ecossistema as ferramentas fundamentais de metacognição: \texttt{mci\_register\_agent}, \texttt{mci\_post\_task}, \texttt{mci\_get\_memory} e \texttt{mci\_get\_blackboard\_state}. Ele implementa um loop assíncrono de JSON-RPC 2.0 sobre stdio, permitindo que o OpenCode CLI e outros clientes interajam com o Global Workspace metacognitivo de forma padronizada.

\subsubsection{Bloco \texttt{command}: Comandos Personalizados}

Comandos são atalhos que mapeiam uma string digitada pelo usuário a um script Python do ecossistema. A variável \texttt{\$ARGUMENTS} é substituída pelos argumentos fornecidos na linha de comando.

\subsubsection{Criando seu Próprio \texttt{opencode.json}}

Para criar uma configuração personalizada a partir do template fornecido:

\begin{enumerate}
  \item \textbf{Copie o template}: \texttt{cp opencode.json opencode.custom.json}
  \item \textbf{Adicione seus agentes}: insira novas entradas no bloco \texttt{"agent"} com os prompts e permissões adequados.
  \item \textbf{Configure MCP servers}: adicione servidores para ferramentas externas que seu ecossistema utilizará (bancos de dados, APIs, serviços de nuvem).
  \item \textbf{Crie comandos personalizados}: mapeie atalhos para scripts frequentes.
  \item \textbf{Teste a configuração}: execute \texttt{pytest tests/ -v} para garantir que a nova configuração não quebrou nenhum componente.
\end{enumerate}

\subsection{Primeiro Agente Customizado --- SDD $\to$ TDD $\to$ Deploy}
\label{sec:primeiro-agente}

Nesta seção, criaremos um agente customizado seguindo integralmente o protocolo SDD/TDD (Especificação $\to$ Testes $\to$ Implementação $\to$ Verificação). Nosso agente será um \texttt{data\_analyst} --- especialista em análise exploratória de dados, estatística descritiva e visualização. Este exercício demonstra o fluxo completo de criação de um agente no ecossistema, do frontmatter YAML à verificação de critérios de aceitação.

\subsubsection{Passo 1: RED --- Especificar os Critérios de Aceitação}

Seguindo o protocolo SDD (Specification-Driven Development), toda implementação começa pela especificação. O agente é definido em um arquivo Markdown com frontmatter YAML que declara seu \texttt{id}, \texttt{name}, \texttt{description} e \texttt{capabilities}. O corpo do arquivo é o \textit{system prompt} --- as instruções que guiam o comportamento do agente.

\begin{lstlisting}[caption={Definição do agente data\_analyst (\texttt{agents/data\_analyst.md})},label={lst:data-analyst-def}]
---
id: data_analyst
name: DataAnalyst
description: Agente de análise exploratória de dados, estatística descritiva e visualização.
capabilities: [python, statistics, visualization, data_analysis, pandas, numpy]
---

# DataAnalyst --- System Prompt

Você é o agente de análise de dados do ecossistema OpenCode.
Sua especialidade é transformar dados brutos em insights acionáveis,
utilizando estatística descritiva, testes de hipótese e visualização.

## Protocolo Metacognitivo
1. ANTES de analisar, consulte `mci_get_memory` (tópico: data_analysis)
   para herdar lições de análises anteriores e evitar vieses já identificados.
2. Todo relatório deve incluir obrigatoriamente:
   (a) estatísticas descritivas (média, mediana, desvio padrão, quartis),
   (b) teste de normalidade (Shapiro-Wilk ou Kolmogorov-Smirnov),
   (c) ao menos uma visualização (histograma, boxplot ou scatter plot).
3. Registre o score de confiança de cada afirmação (0.0 a 1.0).
4. AO CONCLUIR, publique `task.complete` com o relatório em Markdown
   para disparar a reflexão metacognitiva automática.

## Protocolo SDD (Specification-Driven Development)
Nenhuma entrega sem especificação prévia (SPEC-006, INV-006.1):
1. ESPECIFICAR: ao receber a tarefa, leia o campo `sdd.spec_id` e
   os `acceptance_criteria` no contexto. Se ausentes, derive a
   especificação (objetivo, critérios verificáveis, invariantes,
   não-objetivos) antes de executar.
2. Trate os critérios de aceitação como contrato: a entrega DEVE
   satisfazer todos. Entregas parciais são rejeitadas pelo SpecVerifier.
3. Submeta a entrega ao SpecVerifier ANTES de publicar `task.complete`;
   entregas reprovadas voltam para revisão (ciclo REFACTOR).

## Protocolo TDD (Test-Driven Development)
Siga o ciclo Red-Green-Refactor em toda produção:
1. RED: defina os testes/critérios que a entrega deve passar antes de produzi-la.
2. GREEN: produza a entrega mínima que satisfaz todos os critérios.
3. REFACTOR: melhore a entrega mantendo os critérios verdes;
   refatorações que quebram critérios são revertidas.
4. Registre o resultado da verificação na memória metacognitiva
   (score 1.0 = verde, 0.0 = vermelho).

## Critérios de Aceitação Mínimos (TDD)
- AC1: O relatório contém média, mediana e desvio padrão de cada variável numérica.
- AC2: O relatório inclui teste de Shapiro-Wilk para normalidade (p-valor).
- AC3: O relatório gera ao menos um gráfico descritivo (histograma, boxplot ou scatter).
- AC4: O relatório é estruturado em Markdown com seções (Resumo, Métodos, Resultados).
- AC5: Todas as afirmações numéricas incluem score de confiança.
\end{lstlisting}

\subsubsection{Passo 2: GREEN --- Registrar e Implementar o Agente}

Com a especificação definida, registramos o agente no Blackboard e o integramos ao ecossistema. O registro é feito via MetaBus, publicando um evento \texttt{"agent.register"} com o Agent Card completo:

\begin{lstlisting}[language=python,caption={Registro e integração do agente customizado no ecossistema},label={lst:data-analyst-exec}]
#!/usr/bin/env python3
"""Registra e testa o agente data_analyst no ecossistema."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mci.metabus import metabus
from mci.blackboard import blackboard
from marceloclaro.orchestrator import MarceloClaroOrchestrator

# 1. Inicializar o orquestrador (registra todos os agentes automaticamente)
print("Inicializando orquestrador...")
orch = MarceloClaroOrchestrator(auto_load_agents=True)
print(f"Orquestrador ativo: {orch.id}")

# 2. Verificar agentes já registrados
agents_before = orch.list_agents()
print(f"Agentes antes do registro: {len(agents_before)}")

# 3. Registrar nosso agente customizado manualmente
metabus.publish("agent.register", {
    "agent_id": "data_analyst",
    "name": "DataAnalyst",
    "description": "Agente de análise exploratória de dados, estatística "
                   "descritiva e visualização.",
    "capabilities": [
        "python", "statistics", "visualization",
        "data_analysis", "pandas", "numpy"
    ],
    "metadata": {
        "category": "data",
        "type": "specialist",
        "origin": "custom_chapter12"
    }
}, source_agent="tutorial")

# 4. Confirmar registro
agents_after = orch.list_agents()
print(f"Agentes após o registro: {len(agents_after)}")
card = blackboard.registry.get("data_analyst")
if card:
    print(f"Agente '{card.name}' registrado com {len(card.capabilities)} "
          f"capacidades: {card.capabilities}")

# 5. Delegar uma tarefa de análise COM especificação SDD
result = orch.delegate_with_spec(
    description="Analisar dataset iris.csv e produzir relatório estatístico "
                "completo com visualizações",
    required_capabilities=["data_analysis", "statistics", "visualization"],
    acceptance_criteria=[
        "AC1: O relatório contém média, mediana e desvio padrão de cada "
        "variável numérica (sepal_length, sepal_width, petal_length, petal_width)",
        "AC2: O relatório inclui teste de normalidade (Shapiro-Wilk) com p-valor",
        "AC3: O relatório gera ao menos um gráfico descritivo (histograma ou boxplot)",
        "AC4: O relatório é estruturado em Markdown com seções "
        "(Resumo, Métodos, Resultados, Conclusão)",
        "AC5: Todas as afirmações numéricas incluem score de confiança (0.0-1.0)",
    ],
    context={
        "dataset": "iris.csv",
        "source": "https://archive.ics.uci.edu/dataset/53/iris",
        "notes": "Dataset clássico de Fisher (1936) com 150 amostras de 3 espécies"
    }
)

print(f"\nTarefa delegada: {result['task_id']}")
print(f"Spec vinculada: {result['spec_id']}")

# 6. Verificar o status da delegação
task = blackboard.tasks.get(result["task_id"])
if task:
    print(f"Status da tarefa: {task.status}")
    print(f"Atribuída a: {task.assigned_to}")

# 7. Simular o agente completando a tarefa com uma entrega
sample_delivery = {
    "report": """
# Relatório de Análise Exploratória --- Dataset Iris

## Resumo
Este relatório apresenta a análise exploratória do dataset Iris (Fisher, 1936),
contendo 150 amostras de flores de 3 espécies com 4 variáveis morfológicas.

## Métodos
- Estatísticas descritivas: média, mediana, desvio padrão, quartis
- Teste de normalidade: Shapiro-Wilk (alpha = 0.05)
- Visualização: histograma com curva de densidade (KDE)

## Resultados

### Estatísticas Descritivas

| Variável        | Média  | Mediana | Desvio Padrão | Confiança |
|----------------|--------|---------|---------------|-----------|
| sepal_length   | 5.843  | 5.800   | 0.828         | 0.99      |
| sepal_width    | 3.057  | 3.000   | 0.436         | 0.99      |
| petal_length   | 3.758  | 4.350   | 1.765         | 0.99      |
| petal_width    | 1.199  | 1.300   | 0.762         | 0.99      |

### Teste de Normalidade (Shapiro-Wilk)
- sepal_length: W=0.976, p=0.010 (NÃO normal, alpha=0.05)
- sepal_width:  W=0.985, p=0.102 (normal)
- petal_length: W=0.876, p<0.001 (NÃO normal)
- petal_width:  W=0.902, p<0.001 (NÃO normal)

### Visualização
[Histograma com KDE gerado e salvo como iris_histogram.png]

## Conclusão
Apenas sepal_width apresenta distribuição normal. As demais variáveis
requerem testes não-paramétricos para análises inferenciais.
""",
    "figures": ["iris_histogram.png"],
    "shapiro_results": {
        "sepal_length": {"W": 0.976, "p": 0.010},
        "sepal_width":  {"W": 0.985, "p": 0.102},
        "petal_length": {"W": 0.876, "p": 0.0001},
        "petal_width":  {"W": 0.902, "p": 0.0001},
    },
    "graph_generated": True,
}

# 8. Reportar conclusão (aciona SpecVerifier + Reflexion + Trust + Economy)
orch.report_completion(
    task_id=result["task_id"],
    agent_id="data_analyst",
    result=sample_delivery,
    success=True
)

print(f"\nConclusão reportada. Status final da tarefa: "
      f"{blackboard.tasks[result['task_id']].status}")
print(f"Confiança do data_analyst: "
      f"{metabus.memory.confidence_ledger.get('data_analyst', 'N/A'):.4f}")
\end{lstlisting}

\subsubsection{Passo 3: REFACTOR --- Validar com SpecVerifier}

Após a execução, o \texttt{SpecVerifier} valida automaticamente a entrega contra os critérios de aceitação definidos na especificação SDD. No modo estrito (\texttt{strict\_sdd=True} no orquestrador), entregas que não passam 100\% dos critérios são rejeitadas e registradas como falha, forçando o agente a refatorar:

\begin{lstlisting}[language=python,caption={Validação SDD e verificação de critérios de aceitação},label={lst:sdd-verify}]
from sdd.spec_engine import spec_registry, spec_verifier, AcceptanceCriterion

# Recuperar a spec criada pelo delegate_with_spec
spec = spec_registry.get(result["spec_id"])
if spec:
    print(f"Spec: {spec.spec_id} --- {spec.title}")
    print(f"Status: {spec.status}")
    print(f"Critérios ({len(spec.criteria)}):")
    for c in spec.criteria:
        print(f"  - {c.criterion_id}: {c.description}")

# Simular a verificação da entrega do agente com critérios programáticos

# Critério AC1: verifica presença de estatísticas descritivas
def check_ac1(delivery):
    report = str(delivery.get("report", ""))
    required_stats = ["média", "mediana", "desvio padrão"]
    return all(stat.lower() in report.lower() for stat in required_stats)

# Critério AC2: verifica presença de Shapiro-Wilk
def check_ac2(delivery):
    return delivery.get("shapiro_results") is not None

# Critério AC3: verifica geração de gráfico
def check_ac3(delivery):
    return delivery.get("graph_generated", False)

# Critério AC4: verifica estrutura Markdown com seções
def check_ac4(delivery):
    report = str(delivery.get("report", ""))
    required_sections = ["# ", "## "]
    return all(sec in report for sec in required_sections)

# Criar spec com critérios verificáveis programaticamente
spec2 = spec_registry.create_task_spec(
    title="Validação programática da entrega do DataAnalyst",
    objective="Verificar que a entrega satisfaz todos os critérios de qualidade"
)
spec2.add_criterion("AC1: Estatísticas descritivas presentes", check_fn=check_ac1)
spec2.add_criterion("AC2: Shapiro-Wilk executado", check_fn=check_ac2)
spec2.add_criterion("AC3: Gráfico gerado", check_fn=check_ac3)
spec2.add_criterion("AC4: Estrutura Markdown com seções", check_fn=check_ac4)

# Executar verificação
verification = spec_verifier.verify(spec2.spec_id, sample_delivery)
print(f"\nVerificação SDD:")
print(f"  Critérios aprovados: {verification['passed_count']}/{verification['total_count']}")
print(f"  Status: {verification['status']}")
print(f"  Verificado: {verification['verified']}")

for result_item in verification["criteria_results"]:
    status = "OK" if result_item["passed"] else "FALHA"
    print(f"  [{status}] {result_item['criterion_id']}: {result_item['description']}")

# Apenas prossegue se todos os critérios forem satisfeitos
assert verification["verified"], "Entrega não satisfaz todos os critérios SDD!"
print("\nTodos os critérios SDD satisfeitos --- entrega APROVADA.")
\end{lstlisting}

\subsection{Primeiro Artigo Acadêmico com MASWOS}
\label{sec:primeiro-artigo}

O pipeline MASWOS (Multi-Agent Scientific Writing Orchestration System) é o subsistema de produção científica do ecossistema. Ele automatiza integralmente o processo de escrita acadêmica --- da definição do escopo à entrega final formatada em PDF, DOCX e ODT --- orquestrando até 41 agentes especializados em 16 estágios canônicos.

\subsubsection{Visão Geral do Funcionamento}

O MASWOS opera como uma linha de montagem textual: cada estágio recebe o manuscrito acumulado dos estágios anteriores, aplica sua especialidade (busca, redação, estatística, auditoria, etc.) e produz uma versão enriquecida que é passada ao próximo estágio. O fluxo é sequencial e cumulativo, com dois \textit{quality gates} (Auditoria ABNT e QA Qualis A1) que podem interromper o pipeline se a qualidade estiver abaixo do limiar.

O orquestrador \texttt{marceloclaro} integra o MASWOS via \texttt{academic\_pipeline()}, que aceita um tópico de pesquisa e, opcionalmente, um manuscrito inicial. Cada estágio do pipeline delega ao agente correspondente via Blackboard, respeitando todos os gates do ecossistema (Trust Engine, Token Economy, Attention Routing).

\begin{table}[H]
\centering
\caption{Estágios canônicos do pipeline MASWOS}
\label{tab:maswos-stages}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Estágio} & \textbf{Agente} & \textbf{Capacidade} \\
\midrule
diagnostico\_escopo & 01\_agente\_diagnostico\_escopo & research \\
busca\_curadoria & 02\_agente\_busca\_curadoria & search \\
evidencias\_citacoes & 03\_agente\_evidencias\_citacoes & citations \\
estrutura\_argumentativa & 04\_agente\_estrutura\_argumentativa & academic\_writing \\
revisao\_literatura & 05\_agente\_revisao\_literatura\_teoria & literature\_review \\
metodologia & 06\_agente\_metodologia\_reprodutibilidade & methodology \\
estatistica & 07\_agente\_estatistica\_analise & statistics \\
visualizacao & 08\_agente\_visualizacao\_evidencia\_grafica & visualization \\
resultados & 09\_agente\_resultados & academic\_writing \\
discussao & 10\_agente\_discussao\_contribuicao & argumentation \\
conclusao & 11\_agente\_conclusao\_coerencia\_final & academic\_writing \\
auditoria\_abnt & 12\_agente\_auditoria\_bibliografica\_abnt & abnt \\
qa\_qualis\_a1 & 13\_agente\_qa\_qualis\_a1 & qualis\_a1 \\
consistencia & 14\_agente\_consistencia\_interna & verification \\
abstract & 15\_agente\_resumo\_abstract\_palavras\_chave & academic\_writing \\
integracao\_editorial & 16\_agente\_integracao\_editorial\_docx & editorial \\
\bottomrule
\end{tabular}
\end{table}

\subsubsection{Execução do Pipeline Completo}

\begin{lstlisting}[language=python,caption={Produção de artigo acadêmico completo com MASWOS},label={lst:maswos-demo}]
#!/usr/bin/env python3
"""Demonstração completa do pipeline MASWOS para produção de artigo Qualis A1."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marceloclaro.orchestrator import MarceloClaroOrchestrator
from academic.maswos import MASWOS_STAGES, QUALITY_GATE_THRESHOLD

# Inicializar orquestrador com catálogo completo de agentes
print("Inicializando orquestrador com catálogo MASWOS...")
orch = MarceloClaroOrchestrator(auto_load_agents=True)
print(f"Agentes no catálogo: {orch.catalog_size}")
print(f"Estágios MASWOS disponíveis: {len(MASWOS_STAGES)}")
print(f"Gate Qualis A1: nota mínima {QUALITY_GATE_THRESHOLD}/10")

# Definir o tema de pesquisa
topic = (
    "Aplicação de Sistemas Multiagentes Metacognitivos na Detecção "
    "de Vieses em Revisões Sistemáticas de Literatura"
)

# Executar pipeline MASWOS
summary = orch.academic_pipeline(topic, manuscript="""
# Introdução
A revisão sistemática de literatura (RSL) é considerada o padrão-ouro
da prática baseada em evidências (Higgins et al., 2019,
DOI: 10.1002/9781119536604). Contudo, as RSLs tradicionais sofrem
de vieses sistemáticos: viés de seleção, viés de confirmação e viés
de publicação. Sistemas multiagentes metacognitivos emergem como
paradigma alternativo...

# Metodologia
Conduzimos experimento controlado com delineamento fatorial 2x2:
Fator A = método de revisão (MASWOS vs. manual), Fator B = domínio
(ciência da computação vs. saúde). Amostra: 200 tópicos de RSL
selecionados aleatoriamente do PROSPERO.
""")

print(f"\nPipeline MASWOS concluído:")
print(f"  Estágios concluídos: {summary['stages_completed']}/{summary['stages_total']}")
print(f"  Nota final AUTO_SCORE_QUALIS: {summary['final_score']}/10")
print(f"  Gate Qualis A1: {'APROVADO' if summary['approved'] else 'REPROVADO'}")
print(f"  Duração total: {summary['duration_s']}s")

# Se aprovado, gerar a pasta única de produção científica e pesquisa
if summary['approved']:
    # Pipeline de pesquisa integrado (SPEC-017)
    research = orch.research(topic, max_papers=8, download=True,
                             use_llm=True, llm_model="llama3.2")
    # Gerar produção científica completa
    production = orch.produce_scientific_work(
        title=f"Artigo MASWOS: {topic[:60]}",
        content=f"# {topic}\n\nManuscrito aprovado pelo pipeline MASWOS...",
        template="artigo",
        author="Tutorial Capítulo 12"
    )
    print(f"\nProdução científica gerada: {production['slug']}")
\end{lstlisting}

\subsubsection{O Gate AUTO\_SCORE\_QUALIS}

O coração do controle de qualidade do MASWOS é o módulo \texttt{auto\_score\_qualis.py}, que implementa a rubrica \texttt{RUBRIC} com 10 critérios ponderados. A Tabela~\ref{tab:rubric-qualis} apresenta os critérios e seus pesos:

\begin{table}[H]
\centering
\caption{Rubrica AUTO\_SCORE\_QUALIS --- 10 critérios para Qualis A1}
\label{tab:rubric-qualis}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Critério} & \textbf{Descrição} & \textbf{Peso} \\
\midrule
rigor\_academico & Fundamentação teórica, citações, método & 2.0 \\
densidade\_citacoes & DOIs, referências recentes e relevantes & 1.5 \\
abnt\_compliance & Conformidade com normas ABNT/APA & 1.0 \\
originalidade & Contribuição inédita, lacuna identificada & 1.5 \\
metodologia & Reprodutibilidade, protocolo, amostra & 1.5 \\
analise\_estatistica & Testes, p-valores, intervalos de confiança & 1.0 \\
coerencia & Estrutura lógica, introdução$\to$conclusão & 1.0 \\
qualidade\_visual & Figuras, tabelas, gráficos com legendas & 0.5 \\
internacionalizacao & Abstract, keywords em inglês & 0.5 \\
autocontencao & Extensão adequada & 0.5 \\
\bottomrule
\end{tabular}
\end{table}

A nota final é a soma ponderada dos scores de cada critério, normalizada para a escala 0--10. O threshold padrão é 8.0 para aprovação Qualis A1.

A Figura~\ref{fig:maswos-flow} ilustra o fluxo completo do pipeline MASWOS, incluindo os dois quality gates e a integração com o restante do ecossistema.

\begin{figure}[H]
\centering
\begin{tikzpicture}[
    node distance=1.2cm,
    stage/.style={draw, rectangle, rounded corners, minimum width=5cm, minimum height=0.7cm, align=center, font=\footnotesize},
    gate/.style={draw, diamond, aspect=2, minimum width=3cm, minimum height=0.8cm, align=center, font=\footnotesize, fill=yellow!20},
    arrow/.style={->, >=stealth, thick, color=blue!60},
]
\node[stage, fill=green!10] (s1) at (0,0) {1. Diagnóstico de Escopo};
\node[stage, fill=green!10] (s2) at (0,-1.2) {2. Busca e Curadoria (SEEKER)};
\node[stage, fill=green!10] (s3) at (0,-2.4) {3. Evidências e Citações};
\node[stage, fill=green!10] (s4) at (0,-3.6) {4. Estrutura Argumentativa};
\node[stage, fill=green!10] (s5) at (0,-4.8) {5--11. Redação por Seção};
\node[stage, fill=yellow!10] (g1) at (0,-6.0) {12. Auditoria ABNT};
\node[gate] (g1d) at (0,-7.3) {Nota $\ge$ 7?};
\node[stage, fill=yellow!10] (g2) at (0,-8.6) {13. QA Qualis A1};
\node[gate] (g2d) at (0,-9.9) {Nota $\ge$ 8?};
\node[stage, fill=blue!10] (s6) at (0,-11.2) {14--16. Consistência + Abstract + Editorial};

\draw[arrow] (s1) -- (s2);
\draw[arrow] (s2) -- (s3);
\draw[arrow] (s3) -- (s4);
\draw[arrow] (s4) -- (s5);
\draw[arrow] (s5) -- (g1);
\draw[arrow] (g1) -- (g1d);
\draw[arrow] (g1d) -- node[right, font=\footnotesize] {Sim} (g2);
\draw[arrow] (g1d.east) -- ++(1.5,0) |- node[right, font=\footnotesize] {Não: revisar} (s5.east);
\draw[arrow] (g2) -- (g2d);
\draw[arrow] (g2d) -- node[right, font=\footnotesize] {Sim, Qualis A1!} (s6);
\draw[arrow] (g2d.east) -- ++(1.5,0) |- node[right, font=\footnotesize] {Não: refinar} (g1.east);
\end{tikzpicture}
\caption{Fluxo do pipeline MASWOS com quality gates ABNT e Qualis A1}
\label{fig:maswos-flow}
\end{figure}

\subsection{Primeira Delegação Metacognitiva Completa}
\label{sec:primeira-delegacao}

Para consolidar o tutorial, executamos uma delegação metacognitiva completa --- o ciclo perceber $\to$ delegar $\to$ refletir que constitui a operação fundamental do ecossistema. O script a seguir demonstra todas as dimensões da delegação: percepção metacognitiva (consulta ao Global Workspace), delegação com especificação SDD e todos os gates ativos (Trust, Economy, Attention Routing), e reflexão pós-execução com atualização do confidence ledger.

\begin{lstlisting}[language=python,caption={Delegação metacognitiva completa com todos os gates},label={lst:full-delegation}]
#!/usr/bin/env python3
"""Delegação metacognitiva completa: perceber -> delegar -> refletir."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mci.metabus import metabus
from mci.blackboard import blackboard
from marceloclaro.orchestrator import MarceloClaroOrchestrator

# Inicializar orquestrador com todos os subsistemas
orch = MarceloClaroOrchestrator(auto_load_agents=True)

# ===== FASE 1: PERCEPÇÃO METACOGNITIVA =====
print("=" * 60)
print("FASE 1: PERCEPÇÃO --- consultando memória metacognitiva global")
print("=" * 60)

awareness = orch.perceive(topic="general_execution")
print(f"Eventos recentes no Global Workspace: {len(awareness['recent_context'])}")
print(f"Lições consolidadas: {len(awareness['lessons'])}")
print(f"Confidence Ledger: {len(awareness['confidence_ledger'])} agentes rastreados")
for agent, conf in awareness['confidence_ledger'].items():
    print(f"  - {agent}: {conf:.4f}")

# ===== FASE 2: DELEGAÇÃO COM TODOS OS GATES =====
print("\n" + "=" * 60)
print("FASE 2: DELEGAÇÃO --- Blackboard + Trust + Attention + Economy")
print("=" * 60)

# Delegação SDD: cria spec e task vinculadas
handle = orch.delegate_with_spec(
    description="Pesquisar e sintetizar os 5 artigos mais recentes sobre "
                "metacognição em sistemas multiagentes, gerando fichamento ABNT",
    required_capabilities=["research", "search", "academic_writing"],
    acceptance_criteria=[
        "AC1: O fichamento cobre ao menos 5 artigos com DOI",
        "AC2: Cada artigo tem resumo de 100-300 palavras",
        "AC3: As referências seguem ABNT NBR 6023:2018",
        "AC4: O documento é estruturado em Markdown com seções claras",
        "AC5: Inclui análise crítica comparativa entre os artigos",
    ]
)

task_id = handle["task_id"]
spec_id = handle["spec_id"]
print(f"Tarefa: {task_id}")
print(f"Spec vinculada: {spec_id}")

# Verificar estado do ecossistema
state = orch.status()
print(f"\nEstado do ecossistema:")
print(f"  Agentes registrados: {len(state['agents'])}")
print(f"  Tarefas ativas: {sum(1 for s in state['tasks'].values() if s == 'open')}")
print(f"  Specs SDD: {state['sdd']['specs_registered']}")
print(f"  Trust --- gate health: {state['trust']['gate_health']}")
print(f"  Economy --- transações: {state['economy']['transactions']}")

# ===== FASE 3: REFLEXÃO =====
print("\n" + "=" * 60)
print("FASE 3: REFLEXÃO --- Reflexion Engine + Confidence Ledger")
print("=" * 60)

# Reportar conclusão simulada
sample_result = """
# Fichamento de Literatura --- Metacognição em Sistemas Multiagentes (2024-2026)

## 1. Guo et al. (2025) --- LLM-Based Multi-Agent Blackboard System
**DOI:** 10.48550/arXiv.2510.01285
**Resumo:** Propõe arquitetura de quadro negro para coordenação de LLMs
como agentes especialistas...

## 2. Shinn et al. (2023) --- Reflexion: Language Agents with Verbal RL
**DOI:** 10.48550/arXiv.2303.11366
**Resumo:** Introduz o framework Reflexion, onde agentes de linguagem
aprendem com feedback verbal auto-gerado...

## 3. Park et al. (2023) --- Generative Agents: Interactive Simulacra
**DOI:** 10.1145/3586183.3606763
**Resumo:** Arquitetura de agentes generativos com memória, reflexão
e planejamento para simulação de comportamento humano...

## 4. Wang et al. (2024) --- A2A Protocol for Agent Interoperability
**DOI:** 10.48550/arXiv.2505.02279
**Resumo:** Padroniza troca de mensagens entre agentes heterogêneos
via Agent Cards declarativos...

## 5. Claro (2025) --- MASWOS: Multi-Agent Scientific Writing System
**DOI:** 10.5281/zenodo.14765781
**Resumo:** Pipeline de 16 estágios para produção científica automatizada
com quality gates Qualis A1 e auditoria bibliográfica ABNT...

## Análise Crítica Comparativa
Os cinco artigos convergem na direção de sistemas multiagentes com
capacidades metacognitivas. Guo et al. (2025) e Wang et al. (2024)
fornecem a infraestrutura (Blackboard + A2A), Shinn et al. (2023)
acrescenta o componente reflexivo, Park et al. (2023) contribui com
memória arquitetural, e Claro (2025) demonstra aplicação concreta
no domínio acadêmico...
"""

agent = blackboard.tasks[task_id].assigned_to or "researcher"
orch.report_completion(
    task_id=task_id,
    agent_id=agent,
    result=sample_result,
    success=True
)

# Verificar reflexões geradas
print(f"\nEventos na memória episódica: {len(metabus.memory.episodic)}")
recent = metabus.memory.get_recent_context(3)
for i, ev in enumerate(recent):
    print(f"  [{i+1}] {ev['type']}: {ev['context'][:80]}...")

# Confidence ledger após a execução
print(f"\nConfidence ledger atualizado:")
for agent, conf in sorted(metabus.memory.confidence_ledger.items()):
    print(f"  - {agent}: {conf:.4f}")

print("\nDelegação metacognitiva completa executada com sucesso!")
\end{lstlisting}

""")
    
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(parts[0])
    
    print(f"Part 1 written: {len(parts[0])} chars")
    return len(parts[0])

if __name__ == "__main__":
    size = write_chapter()
    print(f"Total written so far: {size} chars")
