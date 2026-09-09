---
language:
  - en
  - pt
license: mit
license_name: mit
license_link: https://opensource.org/licenses/MIT
tags:
  - opencode
  - ecosystem
  - multi-agent
  - scientific-research
  - maswos
  - sdd-tdd
  - metacognitive
  - orchestration
  - game-theory
  - trust-engine
  - evolution-registry
  - scanner
  - transformer
  - reasoning
  - cli
pretty_name: "OpenCode Ecosystem Core"
datasets:
  - marceloclaro/opencode-research
task_categories:
  - other
---

# OpenCode Ecosystem Core

> **Ecossistema Python completo para orquestração de tarefas, memória metacognitiva, especificações SDD/TDD, integrações MCP e fluxos de pesquisa científica.**

[![GitHub](https://img.shields.io/badge/GitHub-MarceloClaro%2Fopencode--ecosystem--core-blue?logo=github)](https://github.com/MarceloClaro/opencode-ecosystem-core)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Datasets-yellow?logo=huggingface)](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10-3.14](https://img.shields.io/badge/Python-3.10--3.14-red?logo=python)](https://www.python.org/)
[![Evolution R485](https://img.shields.io/badge/Evolution-R485-orange)](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core)

## Visão Geral

O **OpenCode Ecosystem Core** é um ecossistema Python de código aberto que organiza o ciclo **perceber → especificar → delegar → executar → verificar → refletir**. Ele combina:

- **Interface de linha de comando (CLI)** para diagnóstico, pesquisa e apresentações
- **Registro de especificações** com 303 specs formais (SDD)
- **Testes vinculados** a cada especificação (TDD)
- **Memória compartilhada** (MetaBus, Blackboard, A2A)
- **Integrações MCP** (LiteRT-LM, Antigravity, PyPI Search, Colibri, Scanners)
- **Pipeline acadêmico** MASWOS de 16 estágios
- **Economia de tokens** com staking, slashing e fee market

> ⚠️ **Aviso**: Este repositório descreve controles e resultados internos observados no checkout. Testes, hashes, diagnósticos e saídas de modelos não constituem certificação externa, garantia de resultado ou substituto para revisão humana.

## Estrutura do Repositório

```
opencode-ecosystem-core/
├── marceloclaro/              # Núcleo do orquestrador
│   ├── orchestrator.py        # Orquestrador central metacognitivo
│   ├── cli.py                 # Interface de linha de comando
│   ├── doctor.py              # Diagnóstico de saúde do ecossistema
│   ├── scientific_lab.py      # Lab científico integrado
│   └── helpdesk.py            # Ajuda guiada
├── academic/                  # Pipeline acadêmico
│   ├── maswos.py              # MASWOS: 16 estágios Qualis A1
│   ├── maswos_llm_delegate.py # Delegação LLM via OpenCode CLI
│   ├── auto_score_qualis.py   # Auto-score rubric (10 critérios)
│   ├── rigorous_board.py      # Board review multi-reviewer
│   └── papers/                # Artigos e scripts de análise
├── research/                  # Pipeline de pesquisa
│   ├── orchestrate.py         # Orquestrador 12 passos
│   ├── experimental_data.py   # 8 experimentos ML reais (sklearn)
│   ├── simulated_reviews.py   # V1: 5 reviewers heurísticos
│   ├── simulated_reviews_v2.py# V2: lógica formal + axiomas + GT
│   └── llm_client.py          # Cliente LLM para delegates
├── evolution/                 # Registro de evolução
│   ├── cycles.py              # EvolutionRegistry (298 ciclos)
│   ├── cycles.json            # Dados de evolução R468-R485
│   ├── audit_pipeline.py      # Pipeline de auditoria
│   └── quality_correlator.py  # Correlação de qualidade
├── sdd/                       # Spec-Driven Development
│   ├── spec_engine.py         # Motor de especificações
│   ├── tdd_runner.py          # Runner de testes TDD
│   └── loop_spec.py           # Loop de specs
├── scanner/                   # Scanners do ecossistema
│   ├── literary/              # 8 scanners literários
│   ├── scientific/            # Scientific Reasoning Scan
│   ├── merkle/                # Integrity Check (SHA-256)
│   └── super_rigor_audit.py   # Auditoria completa 8 scanners
├── transformer/               # Módulos transformer
│   ├── attention.py           # AttentionRouter
│   ├── memory.py              # Memória transformada
│   ├── episteme.py            # Episteme transformer
│   └── pipeline.py            # Pipeline transformer
├── trust/                     # Trust engine
│   ├── trust_engine.py        # Staking, slashing, behavioral gates
│   └── vectorized_drift.py    # Detecção de drift
├── translation/               # Tradução cultural
│   ├── cultural_episteme.py   # Epistemes culturais
│   ├── terminology_graph.py   # Grafo terminológico trilíngue
│   ├── author_voice.py        # Guarda de voz autoral
│   └── back_translation.py    # Verificação retrotradução
├── mci/                       # Metacognitive Interconnect
│   ├── MetaBus/               # Memória metacognitiva global
│   ├── Blackboard/            # Blackboard A2A
│   └── AttentionRouter/       # Roteamento de atenção
├── reasoning/                 # Motores de raciocínio
│   ├── z3_solver.py           # SMT Solver (Z3)
│   ├── sympy_engine.py        # SymPy matemático
│   └── kanren_engine.py       # Kanren lógico
├── gametheory/                # Teoria dos Jogos
│   ├── nash.py                # Nash Equilibrium
│   ├── pareto.py              # Pareto Optimality
│   ├── mechanism_design.py    # Mechanism Design
│   └── prisoner_dilemma.py    # Prisoner's Dilemma
├── economy/                   # Economia de tokens
│   ├── staking.py             # Staking de agentes
│   ├── slashing.py            # Slashing por falhas
│   └── fee_market.py          # Fee market
├── data/                      # Dados de pesquisa
│   ├── research_proposals.json    # 160 proposals (8 domínios)
│   ├── scientific_datasets_catalog.json # 243 datasets
│   └── phd_agents.json           # 8 PhD agents
├── agents/catalog/            # 205 agentes especializados
├── specs/                     # 303 especificações formais
├── tests/                     # Suite de testes
├── scripts/                   # Scripts utilitários
├── integrations/              # Integrações CLI
├── docs/                      # Documentação
├── examples/                  # Exemplos de uso
└── scientific_lab/            # Lab científico integrado
```

## Capacidades Principais

| Capacidade | Descrição | Módulo |
|---|---|---|
| **Orquestração** | Coordena tarefas via Blackboard (A2A) e MetaBus | `marceloclaro/orchestrator.py` |
| **SDD/TDD** | Especificações formais vinculadas a testes | `sdd/spec_engine.py`, `sdd/tdd_runner.py` |
| **MASWOS** | Pipeline acadêmico de 16 estágios (Qualis A1) | `academic/maswos.py` |
| **Research** | 160 proposals, 243 datasets, 8 PhD agents | `research/orchestrate.py` |
| **Scanners** | Literary, scientific, reasoning, Merkle integrity | `scanner/` |
| **Game Theory** | Nash equilibrium, Pareto, Prisoner's Dilemma | `gametheory/` |
| **Trust Engine** | Staking, slashing, behavioral gates | `trust/trust_engine.py` |
| **Evolution** | 298 ciclos registrados (R468-R485) | `evolution/cycles.py` |
| **Reasoning** | Z3, SymPy, Kanren solvers | `reasoning/` |
| **Translation** | Tradução cultural trilíngue | `translation/` |
| **Economy** | Economia de tokens com staking/slashing | `economy/` |
| **CLI** | Diagnóstico, pesquisa, apresentação | `marceloclaro/cli.py` |

## Dados de Pesquisa

### 160 Research Proposals

Propostas de pesquisa estruturadas em 8 domínios científicos:

| Domínio | Proposals | Periódicos Alvo |
|---|---|---|
| Healthcare | 20 | Nature Medicine, Lancet Digital Health, NEJM |
| Environment | 20 | Nature Climate Change, Nature Sustainability |
| Social Sciences | 20 | Nature Human Behaviour, Science |
| Computer Science | 20 | Nature Computational Science, ICSE, NeurIPS |
| Engineering | 20 | Nature Materials, Nature Energy, Science Robotics |
| Biology | 20 | Nature, Nature Methods, Nature Biotechnology |
| Finance | 20 | Journal of Financial Economics, Journal of Finance |
| Agriculture | 20 | Nature Food, Nature Biotechnology |

### 243 Datasets Catalog

Datasets reais de Kaggle e HuggingFace em 8 domínios:
- Healthcare (32), Environment (35), Social Sciences (34)
- Computer Science (29), Engineering (27), Biology (29)
- Finance (30), Agriculture (27)

### 8 PhD Agents

Agentes especializados com periódicos e lacunas de pesquisa documentadas.

### 8 ML Experiments

Experimentos reais com scikit-learn:
- Classification (Breast Cancer, Wine)
- Regression (Synthetic)
- Clustering (K-Means)
- Statistical Tests (Mann-Whitney)
- Association Rules (Apriori)
- Feature Importance (Permutation)
- CV Robustness (Stratified K-Fold)
- PCA Variance Analysis

## Auto-Score

O pipeline MASWOS atingiu **97/100** (Qualis A1: True) com:

| Critério | Nota |
|---|---|
| Coerência Lógica Interna | 10/10 |
| Rigor Metodológico | 10/10 |
| Análise Estatística | 10/10 |
| Diagramação e Qualidade Visual | 10/10 |
| Densidade de Citações | 10/10 |
| Originalidade e Contribuição | 10/10 |
| Diálogo Crítico com a Literatura | 9/10 |
| Clareza e Acessibilidade | 10/10 |
| Conformidade Ética e FAIR | 10/10 |
| Impacto Potencial | 8/10 |

## Início Rápido

### Instalação

```bash
git clone https://github.com/MarceloClaro/opencode-ecosystem-core.git
cd opencode-ecosystem-core
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Verificação de Saúde

```bash
.venv/bin/python -m marceloclaro.cli doctor
```

### Comandos Principais

```bash
# Diagnóstico completo
.venv/bin/python -m marceloclaro.cli doctor

# Ajuda guiada
.venv/bin/python -m marceloclaro.cli helpdesk

# Pesquisa científica
.venv/bin/python -m marceloclaro.cli pesquisa-full "tema"

# MASWOS pipeline
.venv/bin/python -m academic.maswos
```

## Arquitetura

O ecossistema segue o ciclo **perceber → especificar → delegar → executar → verificar → refletir**:

1. **Perceber**: Consulta MetaBus e lições passadas
2. **Especificar**: Cria/recupera especificação formal (SDD)
3. **Delegar**: Roteia para agente mais adequado via Blackboard
4. **Executar**: Ciclo TDD (RED → GREEN → REFACTOR)
5. **Verificar**: Gate SDD + Behavioral Gate
6. **Refletir**: Auto-reflexão + lições no MetaBus

## Integrações MCP

| MCP | Função |
|---|---|
| `litert-lm` | Modelos on-device (Gemma 4, Qwen3) |
| `metacognitive-interconnect` | MetaBus, Blackboard, A2A |
| `antigravity-bridge` | Google DeepMind (imagens, browser, pesquisa) |
| `pypi-search` | Busca de pacotes Python |
| `colibri-mcp` | Geração de texto local (OLMoE 1B/7B) |
| `scanners-mcp` | 8 scanners literários e científicos |

## Ciclos de Evolução

O ecossistema registra cada ciclo evolutivo no `EvolutionRegistry`:

- **R468-R485**: 298 ciclos totais
- **Score médio**: 9.2/10
- **Último ciclo**: R485 (HuggingFace Hub mirror)

## Backup e Portfólio

Este repositório no HuggingFace Hub serve como:

1. **Backup completo** do ecossistema OpenCode Ecosystem Core
2. **Portfólio** de capacidades e conquistas
3. **Repositório de dados** de pesquisa (160 proposals, 243 datasets)
4. **Documentação viva** com dataset card atualizado

### Repos Relacionados

| Repositório | Descrição |
|---|---|
| [opencode-ecosystem-core](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core) | Este repositório (backup + portfólio) |
| [opencode-research](https://huggingface.co/datasets/marceloclaro/opencode-research) | 160 proposals + 243 datasets + 8 agents |
| [GitHub](https://github.com/MarceloClaro/opencode-ecosystem-core) | Repositório principal (desenvolvimento) |

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Autor

**Marcelo Claro** - [GitHub](https://github.com/MarceloClaro) - [HuggingFace](https://huggingface.co/marceloclaro)

## Como Citar

```bibtex
@software{claro2026opencode,
  author = {Claro, Marcelo},
  title = {OpenCode Ecosystem Core},
  year = {2026},
  url = {https://github.com/MarceloClaro/opencode-ecosystem-core},
  version = {R485}
}
```
