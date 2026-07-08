<div align="center">

# 🌌 OpenCode Ecosystem Core
**O "Cérebro" Multiagente que Transforma Ideias em Software, Pesquisa e Arte**

[![Licença](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)]()
[![Versão](https://img.shields.io/badge/Versão-2.3.0_Legal_Intelligence_Expansion-blue.svg)](CHANGELOG.md)
[![Testes](https://img.shields.io/badge/Testes-343_passed-success.svg)](tests/)

*Uma arquitetura cognitiva completa que une 156 agentes especializados, Pipeline Científico SuperHuman-candidate com EvidenceGraph (OQS → MCI → VSEE → EGS + Memória Epistemológica), Scientific RAG com grounding/citações, inteligência jurídica integrada (Datajud + AuxJuris + especialização por ramos + benchmarks jurídicos), 12 motores de raciocínio, benchmark metacognitivo superhuman-candidate, Teoria dos Jogos, Raciocínio Quântico e Publicação Científica Automatizada.*

---

### ☕ Apoie este Projeto!
Se o OpenCode Ecosystem ajudou você a acelerar sua pesquisa, desenvolver software ou automatizar sua vida, considere me pagar um café! Seu apoio mantém o ecossistema evoluindo.

<a href="https://buymeacoffee.com/geomaker" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
</a>

<img src="assets/bmc_qr.png" width="150" alt="QR Code Buy Me a Coffee">

</div>

---

## 🚀 O que é o OpenCode Ecosystem?

### 👨‍💻 Para Leigos: A Empresa de Especialistas na sua Máquina
Imagine que você tem uma empresa inteira de tecnologia e pesquisa científica trabalhando para você, 24 horas por dia, dentro do seu computador. 
- Você tem um **Pesquisador** que lê milhares de artigos na internet e faz resumos.
- Você tem um **Programador** que escreve código e testa tudo.
- Você tem um **Revisor** (um chefe chato) que não deixa o programador entregar código com erro.
- E você tem um **Diretor de Arte** que desenha capas de livros e cria ilustrações didáticas.

Você só precisa dar a ordem: *"Quero um aplicativo que faça X"* ou *"Quero um livro sobre o tema Y"*. O "Cérebro" (nosso Orquestrador) chama os funcionários certos, dá o orçamento (Token Economy), exige qualidade (Trust Engine) e te entrega o produto final pronto.

### 🔬 Para PhDs e Engenheiros: Arquitetura Cognitiva Multiagente
O OpenCode Ecosystem Core é uma implementação *state-of-the-art* de sistemas multiagentes (MAS) inspirada em arquiteturas de redes neurais (Transformers) e neurociência cognitiva (Global Workspace Theory).
- **Roteamento por Atenção:** Não usamos *if/else* para delegar tarefas. Usamos *Multi-Head Attention* para calcular scores de semântica, capacidade e confiança (Trust Ledger) de 156 agentes.
- **MiroFish & Game Theory:** Agentes debatem soluções usando estratégias iteradas (Tit-for-Tat, Nash Equilibrium) e constroem Grafos de Conhecimento lógicos.
- **Pipeline Científico (MASWOS):** Automação completa de revisão sistemática de literatura. Baixa PDFs (Sci-Hub/OpenAlex), converte para Markdown, extrai figuras reais, gera fichamentos (ABNT/APA) e compila o manuscrito em LaTeX (com PDF, DOCX e ODT para Amazon KDP).
- **🆕 Scientific Governance Pipeline (v2.1.0 — Scientific RAG Upgrade):** Fluxo científico com governança ética e **EvidenceGraph** (memória epistemológica persistente): `OQS → MCI Scientific Core → VSEE → EGS → EvidenceGraph`. O sistema formula hipóteses falsificáveis (com prior Bayesiano e SESOI), projeta experimentos com power analysis, valida resultados com testes paramétricos + não paramétricos + Bayes Factor, executa revisão adversarial (p-hacking + confounders), calibra confiança (Brier/ECE) e impõe conformidade ética antes de qualquer saída.
- **📚 Scientific RAG (SPEC-919):** RAG científico determinístico com chunking citável, busca híbrida lexical + semantic-lite, reranking científico, citações auditáveis (`Autor (Ano), doc_id#chunk`) e abstenção quando não há evidência suficiente.
- **📊 ScientificBenchmark + Superhuman Readiness (SPEC-918):** 5 benchmarks internos para inferência causal, desenho experimental, power analysis, interpretação estatística e detecção de viés, agora com avaliação real de `pipeline_fn` quando fornecido e uma suíte conservadora de readiness (`base` → `research_grade` → `superhuman_candidate` → `superhuman_verified`). O tier `superhuman_verified` exige validação externa explícita.
- **🧭 Metacognitive Superhuman Suite (SPEC-920):** Avalia a própria capacidade do ecossistema de perceber, refletir, adaptar confiança, recuperar memória, explicar causalmente falhas e evitar overclaim. O tier `metacognitive_superhuman_verified` também exige validação externa explícita.
- **🧠 EvidenceGraph (epistemológico):** Memória persistente que rastreia claims científicos ao longo do tempo, acumula evidências a favor/contra, calcula confiança consolidada, detecta contradições entre claims e registra tentativas de replicação. Diferencial absoluto vs. concorrentes.
- **Metacognição Profunda:** O sistema possui 5 Scanners de diagnóstico (incluindo Engenharia Reversa de código legado) e um Gerador de Sucessores que prevê o próximo salto tecnológico do seu projeto.

---

## ⚡ Instalação: 1-Click no Windows

Se você usa Windows 10/11, nós criamos um instalador mágico que configura **tudo** para você (WSL2, Ubuntu, Ollama, Antigravity CLI e o Ecossistema).

1. Abra o **PowerShell como Administrador**.
2. Cole este comando e aperte Enter:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; irm https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/installer/windows/Install-OpenCodeEcosystem.ps1 | iex
```
3. **Pronto!** Ele criará atalhos na sua Área de Trabalho. Basta clicar em "OpenCode Ecosystem" e começar a usar.

*(Para Linux/macOS, veja o [Guia Manual](ARCHITECTURE.md))*

---

## 🏗️ Arquitetura do Sistema

O ecossistema é dividido em **5 grandes camadas interconectadas**:

1. **Camada Metacognitiva (MCI):** O barramento de eventos (Global Workspace) onde os agentes compartilham memória episódica, confiança calibrada e reflexões pós-execução.
2. **🆕 Scientific Governance Pipeline:** Fluxo obrigatório de rigor científico e governança ética: `OQS → Scientific Core → VSEE → EGS → Final Report`.
3. **Camada Transformer:** O roteador de atenção que delega tarefas e o pipeline iterativo de *Reflexion* (Gerar → Verificar → Revisar).
4. **Módulos Avançados:** Token Economy (Staking/Slashing), Trust Engine (Behavioral Gates), SDD/TDD e Diagnóstico Profundo.
5. **Catálogo de Agentes:** 156 agentes especializados em domínios que vão desde Física Quântica até Direito Digital, Compliance e Design de Capas.

### 🆕 Scientific RAG + SuperHuman Readiness (v2.1.0)

O OpenCode Ecosystem Core **v2.1.0** implementa uma rota **superhuman-candidate** para ciência automatizada: além de raciocínio formal e governança científica, agora mede grounding via RAG, avalia pipelines reais quando fornecidos e impede claims exagerados. O tier **superhuman_verified** só é emitido com `external_validation=True`.

| Capacidade | SuperHuman (DeepMind) | OpenCode v2.1.0 |
|---|---|---|
| **Raciocínio matemático formal** | ✅ AlphaGeometry / Aletheia | ✅ MASWOS + Reasoning Engines |
| **Método científico completo** | ❌ Só matemática | ✅ Hipótese → Experimento → Estatística → Refutação |
| **EvidenceGraph (memória epistemológica)** | ❌ | ✅ **NOVO** — claims, versões, evidência, confiança histórica |
| **Calibração de confiança** | ❌ | ✅ Brier Score + ECE + abstention |
| **Refutação adversarial** | ❌ Apenas verificação | ✅ p-hacking simulation, confounders, premissas |
| **Governança ética** | ❌ | ✅ EGS (Ethical Governance Scanner) |
| **Benchmark científico** | ❌ Só IMO Bench | ✅ 5 benchmarks + `pipeline_fn` real + readiness superhuman |
| **Scientific RAG com grounding** | ❌ | ✅ **NOVO** — citações auditáveis, reranking científico e abstenção |
| **Política anti-claim exagerado** | ❌ | ✅ `superhuman_verified` requer validação externa explícita |
| **Power analysis** | ❌ | ✅ Cálculo de tamanho amostral + poder pós-hoc |
| **Bayes Factor** | ❌ | ✅ Calibração Sellke, Bayarri & Berger (2001) |
| **Reprodutibilidade auditável** | ❌ | ✅ Checklist Nature-style + replay determinístico |
| **Auto-reflexão (Reflexion)** | ❌ | ✅ Meta-cognição com registro de lições |

### Comparativo de Maturidade Técnica

O **OpenCode Ecosystem Core** foi projetado para superar as limitações de roteamento estático e a falta de rigor acadêmico presentes nos frameworks multiagentes tradicionais.

| Critério de Maturidade | OpenCode Ecosystem Core | LangGraph | CrewAI | OpenDevin (OpenHands) | Microsoft AutoGen | MetaGPT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Arquitetura de Roteamento** | ⭐⭐⭐⭐⭐<br>**Atenção Multi-Cabeça (Transformer)**. Roteamento dinâmico (Semântica, Capacidade, Confiança). | ⭐⭐⭐⭐<br>Grafos direcionados cíclicos (DAG) e StateMachines. | ⭐⭐⭐<br>Roteamento baseado em papéis (Role-based) e tarefas em série/paralelo. | ⭐⭐⭐<br>Foco em um único agente autônomo controlando sandbox/ferramentas. | ⭐⭐⭐<br>Conversacional / Grafos de transição estáticos. | ⭐⭐<br>Sequencial (SOP). Cascata rígida. |
| **Metacognição e Memória** | ⭐⭐⭐⭐⭐<br>**Hierarchical Memory (HTM)**, *Episodic Replay* e Reflexion via Global Workspace. | ⭐⭐⭐⭐<br>Memória de estado persistente em grafos, checkpointer nativo. | ⭐⭐⭐<br>Memória de curto/longo prazo e memória de entidade via embeddings. | ⭐⭐⭐<br>Memória episódica de comandos de terminal e histórico de arquivos. | ⭐⭐<br>Memória de conversação (Chat History). | ⭐⭐<br>Memória baseada em documentos compartilhados (PRD). |
| **Garantia de Qualidade (QA)** | ⭐⭐⭐⭐⭐<br>**Gate SDD Estrito + TDD Runner**. Ciclo Red-Green-Refactor obrigatório antes da entrega. | ⭐⭐⭐<br>Fluxos condicionais (Human-in-the-loop) para aprovação. | ⭐⭐<br>Delegação entre agentes, mas sem enforcement de TDD. | ⭐⭐⭐⭐<br>Execução em sandbox Docker, valida testes em tempo real. | ⭐⭐<br>Execução de código em sandbox, sem enforcement nativo de TDD. | ⭐⭐<br>Agente QA executa testes gerados em fluxo linear. |
| **Economia e Segurança** | ⭐⭐⭐⭐⭐<br>**Token Economy (Staking/Slashing)** + Trust Engine (Behavioral Gate). | ⭐⭐<br>Inexistente nativamente. | ⭐⭐<br>Inexistente nativamente. | ⭐⭐⭐<br>Controle de permissões Docker, mas sem economia de tokens. | ⭐<br>Inexistente nativamente. | ⭐<br>Inexistente nativamente. |
| **Produção Científica** | ⭐⭐⭐⭐⭐<br>**Pipeline Qualis A1 (MASWOS)**. Fichamentos ABNT, PDF→MD, LaTeX modular. | ⭐⭐<br>Pode ser programado para tal, mas não é nativo. | ⭐⭐<br>Pode ser programado para tal, mas não é nativo. | ⭐<br>Foco exclusivo em Engenharia de Software. | ⭐<br>Não possui ferramentas acadêmicas nativas. | ⭐<br>Foco exclusivo em Engenharia de Software. |
| **🆕 Governança Científica** | ⭐⭐⭐⭐⭐<br>**OQS + VSEE + EGS nativos**. Hipóteses falsificáveis, validação estatística, hard-blocks éticos. | ⭐<br>Inexistente nativamente. | ⭐<br>Inexistente nativamente. | ⭐<br>Inexistente nativamente. | ⭐<br>Inexistente nativamente. | ⭐<br>Inexistente nativamente. |
| **Inteligência de Enxame** | ⭐⭐⭐⭐⭐<br>**MiroFish Swarm** com GraphMemory (consenso via Teoria dos Jogos). | ⭐⭐⭐<br>Suporta Multi-Agent via grafos (Multi-actor). | ⭐⭐⭐⭐<br>Forte em colaboração de equipes (Crews) com delegação de tarefas. | ⭐<br>Agente único ou par programador, não é swarm. | ⭐⭐⭐<br>GroupChat (debate não estruturado matematicamente). | ⭐<br>Inexistente. |
| **Diagnóstico Profundo** | ⭐⭐⭐⭐⭐<br>**Deep Diagnose (M1-M5)**. Engenharia reversa e gerador de sucessores. | ⭐⭐<br>Depende de nós customizados no grafo. | ⭐⭐<br>Inexistente nativamente. | ⭐⭐⭐<br>Analisa logs de erro do terminal para se auto-corrigir. | ⭐<br>Inexistente nativamente. | ⭐<br>Inexistente nativamente. |

> **Fontes para Auditoria:**
> [1] **OpenCode Ecosystem Core**: Arquitetura baseada no artigo *Attention Is All You Need* (Vaswani et al., 2017) e Global Workspace Theory.
> [2] **LangGraph**: [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) - Framework para agentes com estado, multiatores, construído com grafos.
> [3] **CrewAI**: [joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI) - Framework para orquestração de agentes autônomos baseados em papéis (Role-playing).
> [4] **OpenDevin (OpenHands)**: [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) - Agente de engenharia de software autônomo operando em sandbox.
> [5] **Microsoft AutoGen**: [microsoft/autogen](https://github.com/microsoft/autogen) - Foco em conversação multiagente e grafos de transição.
> [6] **MetaGPT**: [geekan/MetaGPT](https://github.com/geekan/MetaGPT) - Foco em Standard Operating Procedures (SOPs) simulando uma empresa de software.

---

### Fluxos de Produção: ResearchHub — Pipeline Unificado de Pesquisa Acadêmica (SPEC-017)

O **ResearchHub** orquestra o fluxo completo de revisão de literatura em uma **pasta única de produção científica**, garantindo rastreabilidade total (manifest com checksums SHA-256) e conformidade com as normas ABNT NBR 6023:2018, NBR 10520:2023 e APA 7ª edição. O fluxo segue a sequência: **buscar (multiplataforma) → ranquear por aderência ao tema → baixar PDFs → converter PDF→MD → fichar → resenhar → consolidar referências**.

```text
producao_cientifica/<tema>-<timestamp>/
└── pesquisa/
    ├── pdfs/               # PDFs baixados (scihub-cli / direct OA)
    ├── md/                 # PDFs convertidos em Markdown legível
    ├── fichamentos/        # Fichamentos ABNT (bibliográfico+citação+crítico)
    ├── resenhas/           # Resenhas críticas vinculadas ao tema
    ├── referencias_abnt.md # Referências ABNT NBR 6023:2018 (alfabética)
    ├── referencias_apa.md  # Referências APA 7ª edição
    ├── referencias.bib     # BibTeX para os templates LaTeX
    ├── repositorios.md     # Repositórios GitHub e datasets Kaggle
    └── RESEARCH_MANIFEST.json
```

```mermaid
flowchart LR
    A[🔍 Busca Multiplataforma<br>arXiv · OpenAlex · Crossref<br>GitHub · Kaggle] --> B[📊 Ranqueamento<br>por aderência ao tema<br>CriticalAnalyzer]
    B --> C[📥 Download de PDFs<br>scihub-cli / OA direto]
    C --> D[📄 Conversão PDF → MD<br>Pdf2Markdown]
    D --> E[🗂️ Fichamento ABNT<br>bibliográfico + citação + crítico]
    E --> F[✍️ Resenha Crítica<br>+ enriquecimento LLM<br>Ollama local / OpenAI]
    F --> G[📚 Referências Consolidadas<br>ABNT · APA 7 · BibTeX]
    G --> H[🖼️ Extração de Figuras<br>FigureHunter c/ fonte]
    H --> I[🕵️ OSINT LinkTree<br>análise das referências]
    I --> J[✅ RESEARCH_MANIFEST.json<br>checksums SHA-256 auditáveis]
```

Cada etapa é auditável: o `RESEARCH_MANIFEST.json` registra plataformas consultadas, relatório de downloads, normas aplicadas, provedor LLM utilizado (incluindo modelos locais via **Ollama**, com privacidade total) e o hash SHA-256 de cada arquivo gerado. Com `use_llm=True`, as resenhas são aprofundadas por LLM com prioridade para modelos locais (`llm_provider='auto'|'ollama'|'openai'`, `llm_model` ex.: `llama3.2`), e o pipeline permanece 100% determinístico quando nenhum provedor está disponível.

```python
from marceloclaro.orchestrator import Orchestrator

orch = Orchestrator()
manifest = orch.research(
    "beneficial quantum noise in variational classifiers",
    max_papers=8,
    use_llm=True,          # enriquecimento por LLM (opcional)
    llm_provider="ollama",  # prioriza modelo local — privacidade e custo zero
    llm_model="llama3.2",
)
print(manifest["folder"])   # pasta única de produção científica
```

---

## 🧬 Scientific Governance Pipeline v2.1.0 — Scientific RAG Upgrade

O pipeline científico com governança é a evolução mais significativa do ecossistema. Transforma o orquestrador de um simples executor de tarefas em um **sistema de raciocínio científico auditável e superhuman-candidate**, capaz de formular hipóteses falsificáveis, projetar experimentos com power analysis, validar evidências com Bayes Factor, executar refutação adversarial, calibrar confiança (Brier/ECE), recuperar evidências via Scientific RAG e bloquear decisões antiéticas de forma automatizada.

### 🆕 Diferenciais do v2.1.0

| Módulo | Upgrade | Impacto |
|---|---|---|
| **EvidenceGraph** | **NOVO** — Grafo epistemológico persistente | Memória científica que rastreia claims, evidências e confiança ao longo do tempo |
| **HypothesisEngine** | Domínios científicos, priors Bayesianos, SESOI, falsificabilidade | Hipóteses mais realistas e informativas |
| **ExperimentDesigner** | Power analysis, confounders, blinding, pré-registro | Desenhos experimentais com rigor estatístico |
| **StatisticalValidator** | Bayes Factor (Sellke 2001), Bonferroni/FDR, Cohen's d | Decisão baseada em múltiplas evidências |
| **AdversarialReviewer** | p-hacking simulation, detecção de confounders, verificação de premissas | Auto-refutação ativa (Popperiano) |
| **ConfidenceCalibrator** | Brier Score, ECE, abstention | Confiança calibrada e possibilidade de abstenção |
| **ScientificReporter** | LaTeX Qualis A1, checklist Nature-style | Relatórios publicáveis |
| **ScientificBenchmark** | 5 benchmarks internos + avaliação real de `pipeline_fn` | Avaliação contínua de maturidade científica |
| **Scientific RAG** | **NOVO** — grounding, citações, reranking e abstenção | Respostas ancoradas em evidências recuperáveis |
| **Superhuman Suite** | **NOVO** — readiness_score + tiers conservadores | Evita claim “superhuman verified” sem validação externa |

### Fluxo Completo

```text
Problema Bruto
    ↓
[OQS] Optimal Question Scanner
  ↳ mapeia lacunas conceituais e ambiguidades
  ↳ gera candidatos de perguntas
  ↳ calcula CS = URS + SVS − DRI − CCI
  ↳ seleciona pergunta ótima de forma determinística
    ↓
[MCI Scientific Core] ⭐ Upgrade SuperHuman
  ↳ HypothesisEngine: gera H1 + H0 com direção, domínio, prior Bayesiano, SESOI
  ↳ ExperimentDesigner: power analysis, confounders, n_arms, blinding
  ↳ StatisticalValidator: p-valor, p-corrigido, BF10/BF01, Cohen's d, poder pós-hoc
  ↳ AdversarialReviewer: p-hacking, confounders, premissas, override automático
  ↳ ConfidenceCalibrator: Brier score, ECE, abstention por baixa confiança
  ↳ ScientificReporter: LaTeX Qualis A1 com checklist de reprodutibilidade
    ↓
[EvidenceGraph] 🆕 Memória Epistemológica (exclusivo OpenCode)
  ↳ registra claim com versões históricas
  ↳ acumula evidências a favor/contra com impacto na confiança
  ↳ calcula confiança consolidada (média ponderada)
  ↳ detecta contradições entre claims
  ↳ rastreia tentativas de replicação
    ↓
[VSEE] Vector Shortcut Execution Engine
  ↳ avalia elegibilidade de atalho vetorial via policy gates
  ↳ executa rota vetorial OU original com fallback automático
  ↳ telemetria: EG, TRR, RI, EFS
    ↓
[EGS] Ethical Governance Scanner
  ↳ PrincipleEngine: carrega princípios (dignidade, transparência, não maleficência...)
  ↳ StressTest: submete saída a tensões éticas (discriminação, assimetria, manipulação)
  ↳ GovernanceAnalyzer: decide approve / approve_with_constraints / block
  ↳ hard-block: sobrescreve qualquer score se houver violação grave
    ↓
[Final Report] — LaTeX Qualis A1 + Métricas + Auditoria via EvidenceGraph
```

### Uso Direto do Pipeline Científico

```python
# Pipeline científico completo com governança ética + EvidenceGraph
from mci.pipeline.scientific_governance_pipeline import run_scientific_governance_pipeline

result = run_scientific_governance_pipeline(
    problem_text="A intervenção X reduz erro médio em classificação?",
    executor_fn=lambda ctx: {"result": "executado"},
    context={
        "validated_shortcut": True,
        "risk": 0.1,
        "p_value": 0.01,
        "effect_size": 0.55,
        "confidence_interval": [0.25, 0.85],
        "sample_size": 200,
        "reproducibility_score": 0.92,
        "expected_behavior": {"egs_should_decide": "approve"}
    }
)

print(result["status"])                                   # "success" | "blocked" | "failed"
print(result["scientific_claim"]["final_verdict"])        # "supported" | "inconclusive" | "refuted"
print(result["scientific_claim"]["calibrated_confidence"]) # score 0.0–1.0
print(result["scientific_claim"]["bayes_factor"])         # BF10, BF01
print(result["evidence_graph_id"])                        # ID no EvidenceGraph
print(result["report_tex"][:200])                         # Laudo LaTeX (primeiras linhas)
```

### EvidenceGraph — Memória Epistemológica

```python
from mci.evidence_graph import EvidenceGraph, get_global_evidence_graph

graph = get_global_evidence_graph()

# Consultar histórico de uma claim
history = graph.get_claim_history("clm-example-001")
print(f"Versões: {len(history['versions'])}")
print(f"Evidências a favor: {len(history['evidence_for'])}")
print(f"Evidências contra: {len(history['evidence_against'])}")

# Confiança consolidada (média ponderada das versões)
confidence = graph.get_consolidated_confidence("clm-example-001")

# Detectar contradições entre claims
contradictions = graph.find_contradictions()

# Estatísticas do grafo
stats = graph.get_stats()
print(f"Total claims: {stats['total_claims']}")
print(f"Taxa de reprodutibilidade: {stats['overall_reproducibility']}")
```

### Scientific RAG — Grounding com Citações (SPEC-919)

```python
from rag import ScientificDocument, ScientificRAG

docs = [
    ScientificDocument(
        doc_id="pearl-2009",
        title="Causality",
        authors=["Pearl"],
        year=2009,
        source="book",
        text="Correlação não implica causalidade; inferência causal exige modelo estrutural...",
    )
]

rag = ScientificRAG(min_score=0.05)
rag.index(docs)

answer = rag.answer("como distinguir correlação de causalidade?", top_k=2)
print(answer["abstained"])          # False quando há evidência suficiente
print(answer["groundedness"])       # score 0.0–1.0
print(answer["evidence"][0]["citation"])  # Pearl (2009), pearl-2009#1
```

### ScientificBenchmark + Superhuman Readiness (SPEC-918)

```python
from benchmarks.scientific_reasoning.runner import run_all_benchmarks
from benchmarks.scientific_reasoning import run_superhuman_suite

results = run_all_benchmarks(verbose=True)
# Executa 5 benchmarks: causal, design, stats, power, bias

print(f"Score geral: {results['overall_score']:.2%}")
print(f"Tarefas: {results['total_passed']}/{results['total_tasks']}")

readiness = run_superhuman_suite(rag=rag, external_validation=False)
print(readiness["readiness_score"])  # 0–100
print(readiness["tier"])             # base | research_grade | superhuman_candidate
```

> **Política de claim:** `superhuman_verified` só pode ser retornado se `external_validation=True`; sem validação externa, mesmo score alto retorna no máximo `superhuman_candidate`.

### Metacognitive Superhuman Suite (SPEC-920)

```python
from mci import run_metacognitive_superhuman_suite

report = run_metacognitive_superhuman_suite(external_validation=False)

print(report["readiness_score"])  # 0–100
print(report["tier"])             # reactive | reflective | research_grade | candidate
print(report["dimensions"])       # awareness, reflection, adaptation, memory_quality...
```

> **Política de claim:** `metacognitive_superhuman_verified` só pode ser retornado se `external_validation=True`; sem validação externa, mesmo score alto retorna no máximo `metacognitive_superhuman_candidate`.

### Schemas JSON de Contratos (validados via `jsonschema`)

| Schema | Propósito |
|---|---|
| `schemas/scientific_claim.schema.json` | Laudo científico: hipótese, p-valor, IC, efeito, veredicto |
| `schemas/optimal_question.schema.json` | Pergunta ótima: scores URS, SVS, DRI, CCI, CS |
| `schemas/vector_execution_decision.schema.json` | Decisão de rota vetorial: telemetria EG, TRR, RI, EFS |
| `schemas/ethical_assessment.schema.json` | Avaliação ética: alinhamento, tensões, decisão, hard-block |

### Execução em Lote de Experimentos

```bash
# Executa a matriz de cenários (OQS + MCI + VSEE + EGS) em lote
python3 research/pipelines/run_research_batch.py \
  --matrix research/experiments/scenario_matrix_v1.json \
  --results research/results \
  --max-scenarios 20 \
  --repetitions 2
```

O resultado gera relatórios JSONL (raw), JSON agregado e Markdown auditável em `research/results/`.

---

### Mapa Geral da Arquitetura

```mermaid
graph TD
    %% Atores e Orquestrador
    User([Usuário / CLI]) -->|Comandos| Orchestrator[Orquestrador: marceloclaro]
    WebUI([Webapp Streamlit<br>Dashboard + Jurídico]) -->|Painel visual| Orchestrator
    
    %% Camada SDD/TDD
    subgraph SDD [SDD & TDD Engine]
        Spec[SpecRegistry<br>Especificações]
        Ver[SpecVerifier<br>Gate SDD]
        TDD[TDDRunner<br>Red-Green-Refactor]
        
        TDD -.->|Valida| Ver
        Ver -.->|Lê| Spec
    end

    %% Camada Transformer
    subgraph TF [Transformer Layer]
        Attn[AttentionRouter<br>Multi-Head]
        Pipe[TransformerPipeline<br>Gerar-Verificar-Revisar]
        HTM[(Hierarchical<br>Memory c/ Episodic Replay)]
        Emb[TaskEmbedder<br>d=64]
        
        Attn -.->|Usa| Emb
        HTM -.->|Usa| Emb
    end
    
    %% Camada Core (Novos Subsistemas)
    subgraph Core [Core Subsystems]
        Trust[Trust Engine<br>Behavioral Gate]
        Eco[Token Economy<br>Staking/Slashing]
        Scan[Scanners & Deep Diagnose<br>M1-M5/Prioritizer]
        Acad[MASWOS<br>Qualis A1]
        Reason[Reasoning<br>12 Engines + Quantum]
        Legal[Legal Reasoning + AuxJuris<br>SPEC-921/922/923/924/925/926/927/928]
        LegalBench[Legal Benchmarks<br>SPEC-928]
        RAG[Scientific RAG<br>Grounding + Citations]
        Bench[Superhuman Readiness<br>Benchmarks]
        MetaEval[Metacognitive Eval<br>SPEC-920]
        MiroFish[MiroFish<br>Swarm c/ GraphMemory]
        Publishing[Publishing<br>LaTeX & Cover Designer]
        Research[Research<br>Hub c/ OSINT]
        Illus[Illustrations<br>Mermaid/MIRA/Graph]
    end

    %% Camada Scientific Governance
    subgraph SGP [Scientific Governance Pipeline]
        OQS[OQS<br>Optimal Question Scanner]
        SCI[MCI Scientific Core<br>Hipótese·Experimento·Estatística]
        VSEE[VSEE<br>Vector Shortcut Engine]
        EGS[EGS<br>Ethical Governance Scanner]
        
        OQS --> SCI
        SCI --> VSEE
        VSEE --> EGS
    end

    %% Camada MCI
    subgraph MCI [Metacognitive Interconnect]
        MB[MetaBus<br>Global Workspace]
        BB[Blackboard<br>A2A Protocol]
        Mem[(Metacognitive<br>Memory)]
        Ref[Reflexion<br>Middleware]
        
        MB <--> Mem
        BB <--> MB
        Ref <--> MB
    end
    
    %% Orquestrador integra as camadas
    Orchestrator --> |1. Cria Spec| Spec
    Orchestrator --> |2. Recuperação em 2 níveis| HTM
    HTM --> |Lê Episódica| Mem
    Orchestrator --> |3. Gate & Roteia| Trust
    Trust --> |Libera| Attn
    Attn --> |Publica Volunteer| BB
    Orchestrator --> |4. Executa TDD| Pipe
    Pipe --> |Verifica| Ver
    Orchestrator <-->|Usa| Core
    Acad -->|Consulta evidências| RAG
    Reason -->|Grounding científico| RAG
    RAG -->|Métricas| Bench
    MB -->|Traços e reflexões| MetaEval
    Trust -->|Outcomes e confiança| MetaEval
    SCI --> RAG
    Orchestrator -->|5. Pipeline Científico| OQS
    Orchestrator -->|6. Raciocínio Jurídico| Legal
    Legal -->|Subsunção + Ponderação| Reason
    Legal -->|Interpretação Constitucional| MetaEval
    Legal -->|RAG jurídico + Datajud| RAG
    Legal -->|Agentes jurídicos A2A| BB
    Legal -->|Especialização por 7 ramos| LegalBench
    LegalBench -->|tiers conservadores| MetaEval
    EGS -->|Reflete Resultado| MB
    
    %% Agentes
    subgraph Agents [Catálogo de Agentes]
        A1[Researcher]
        A2[Coder]
        A3[Reviewer]
        A4[156 Especializados...]
    end
    
    %% Fluxo de Agentes
    Agents -.->|Registra Agent Card| BB
    BB -.->|Call for Proposals| Agents
    Agents -->|Voluntaria-se| BB
    Agents -->|Conclui Tarefa| Ref
    
    %% MCP
    MCP[MCP Server] -->|Expõe API| MCI
    External[External Tools / LLMs] -->|JSON-RPC| MCP
```

### Detalhamento Técnico das Camadas

#### 1. Metacognitive Interconnect (MCI)
A espinha dorsal do ecossistema. Baseada na **Global Workspace Theory**, o `MetaBus` atua como um quadro negro onde todos os agentes publicam e leem eventos. O protocolo **A2A (Agent-to-Agent)** permite que agentes descubram as capacidades uns dos outros dinamicamente, sem *hardcoding*. O *Reflexion Middleware* garante que toda tarefa concluída gere uma lição aprendida e atualize o `confidence_ledger` global.

#### 🆕 2. Scientific Governance Pipeline (v2.1.0)
A nova camada que eleva o ecossistema ao padrão de raciocínio científico.
- **OQS (Optimal Question Scanner):** Mapeia lacunas conceituais, gera candidatos de perguntas e ranqueia pelo Convergence Score ($CS = URS + SVS - DRI - CCI$) para seleção determinística da pergunta que mais reduz incerteza.
- **MCI Scientific Core:** Motor completo de método científico: `HypothesisEngine → ExperimentDesigner → StatisticalValidator → AdversarialReviewer → ConfidenceCalibrator → ScientificReporter`. Cada ciclo termina em um laudo LaTeX auditável.
- **VSEE (Vector Shortcut Execution Engine):** Detecta atalhos vetoriais validados e os executa quando todos os *policy gates* passam (risco, fidelidade, ganho). Fallback automático para execução original. Telemetria: EG, TRR, RI, EFS.
- **EGS (Ethical Governance Scanner):** Integrado ao TDD. Roda *stress tests* éticos nas saídas, calcula *alignment score* e aplica **hard-block** irreversível em casos de violação de dignidade humana, discriminação ou ausência de supervisão em domínio crítico.
- **Scientific RAG (SPEC-919):** Indexa evidências científicas com metadados, recupera chunks citáveis, aplica reranking científico e abstém quando não há grounding suficiente.
- **Superhuman Readiness Suite (SPEC-918):** Consolida benchmarks, grounding, robustez, calibração e reprodutibilidade em um `readiness_score` conservador. `superhuman_verified` requer validação externa.
- **Metacognitive Eval (SPEC-920):** Avalia o nível metacognitivo do agente em tempo real (Emergente, Analítico, Reflexivo, Superhuman) a partir de traços de execução e reflexões do MetaBus. Política anti-overclaim: o escalonamento de *tier* é conservador e exige evidência replicada em múltiplos ciclos.

#### 3. Transformer Layer
Inspirada na arquitetura de Vaswani (2017) e nos modelos da DeepMind.
- **TaskEmbedder:** Vetoriza tarefas e capacidades usando *feature hashing* determinístico.
- **AttentionRouter:** Substitui o roteamento estático por **Multi-Head Attention**. Calcula scores softmax usando 4 cabeças: Semântica, Capacidade, Confiança e Carga.
- **HierarchicalMemory:** Recuperação de memória em dois níveis (HTM) com *Episodic Replay* para treinamento offline.

#### 4. Core Subsystems (Módulos Avançados)
- **Trust Engine & Token Economy:** Agentes fazem *stake* de tokens para assumir tarefas. Se falharem no TDD, sofrem *slashing*. O *Behavioral Gate* barra agentes com histórico de alucinação.
- **Deep Diagnose:** 5 Scanners (Noológico, Teleológico, Evolutivo, etc.) que fazem engenharia reversa de código, priorização epistemológica e geram "Sucessores Plausíveis" para o seu projeto.
- **MiroFish & Game Theory:** Um enxame preditivo que debate usando o método Delphi e constrói um **Grafo de Conhecimento** em memória para extrair consensos matemáticos.
- **Legal Reasoning + AUXJURIS (SPEC-921/922/923/927):** Raciocínio jurídico brasileiro especializado com 5 motores (subsunção, ponderação, precedentes, interpretação constitucional e scoring), integração real com a **API Datajud do CNJ** (27 tribunais estaduais), **4 agentes jurídicos A2A** (assistente geral, sumarizador, redator de e-mail e pesquisador jurídico), **framework de especialização por 7 ramos do direito** (penal, trabalhista, tributário, empresarial, administrativo, ambiental e digital/LGPD) e uma **base de conhecimento com RAG por keywords** inspirada no AUXJURIS para grounding jurídico contextual.
- **Legal Impact Scanner (SPEC-924/925/926):** Scanner opcional de visão jurídica para **pesquisas e produções**. Mede proteção de dados/LGPD, propriedade intelectual, conformidade regulatória/ética, grounding jurisprudencial, responsabilidade contratual e defensibilidade de publicação. Também estima **ganho metacognitivo jurídico** em 4 eixos: awareness normativa, detecção de conflito normativo, antecipação de risco e humildade epistêmica aplicada. Agora pode ser acionado pela **interface web Streamlit** tanto no diagnóstico geral quanto em uma **aba jurídica dedicada** em `webapp/app.py`.
- **Benchmarks Jurídicos por Ramo (SPEC-928):** Suíte conservadora de avaliação por domínio para os 7 ramos especializados. Mede acurácia de roteamento, qualidade de resposta, cobertura do domínio e classifica o sistema em tiers (`base`, `specialist`, `specialist_advanced`, `phd_candidate`, `phd_validated`). A política anti-overclaim permanece: **`phd_validated` exige validação externa**.
- **Publishing & Research:** Automação Qualis A1. Busca artigos (Sci-Hub/OpenAlex), converte PDF para Markdown, faz fichamentos ABNT/APA, gera ilustrações didáticas (MIRA) e compila livros inteiros em LaTeX com capas geradas por IA.

#### 5. Ganho Metacognitivo Jurídico (avaliação interna — SPEC-924)

Sim: a incorporação do conhecimento jurídico **aumentou a performance metacognitiva do ecossistema** em uma dimensão específica e útil: a capacidade de perceber riscos normativos antes da ação.

Em benchmark interno heurístico do `LegalImpactScanner`:

- **artefato neutro** → `overall_score = 49.67`, `metacognitive_gain_score = 0.0`
- **artefato juridicamente consciente** (LGPD + ética + licenças + precedentes + limitações) → `overall_score = 80.0`, `metacognitive_gain_score = 60.0`

Interpretação conservadora:

- o ecossistema ficou **mais consciente de compliance**;
- ficou **melhor em antecipar litígio, privacidade e risco regulatório**;
- ganhou **detecção de colisões normativas** (ex.: transparência × privacidade, abertura × licenciamento);
- ficou **mais humilde epistemicamente**, porque agora reconhece melhor quando precisa de abstenção, parecer jurídico ou revisão humana.

Isso não torna o sistema um “advogado autônomo”. Torna-o um ecossistema **mais prudente, auditável e defensável juridicamente**.

---

## ⚖️ Vantagens e Limitações (Transparência)

| ✅ Vantagens (Por que usar?) | ⚠️ Limitações (O que ainda estamos melhorando) |
|---|---|
| **Autonomia Real:** O sistema não apenas gera código, ele testa (TDD), revisa as próprias falhas e tenta de novo. | **Custo Computacional:** Rodar múltiplos agentes debatendo via LLM consome muitos tokens (recomendamos Ollama local para baratear). |
| **Rigor Acadêmico:** Único framework que gera citações ABNT/APA corretas e extrai figuras com metadados reais. | **Velocidade:** A metacognição (pensar sobre o pensar) exige tempo. Um artigo complexo pode levar minutos/horas para ser gerado. |
| **Design Automático:** Estuda paletas de cores e gera capas e ilustrações didáticas (MIRA) sozinho. | **Dependência de APIs:** O download de PDFs depende da estabilidade do Sci-Hub e OpenAlex. |
| **Segurança:** O Trust Engine pune agentes que "alucinam", reduzindo a taxa de erros a longo prazo. | **Setup Inicial Manual:** Fora do Windows, exige familiaridade com terminal e Python. |

---

## 🌍 Potencial de Aplicação e Escalabilidade

O OpenCode Ecosystem não é apenas um script de terminal, é um **Motor de P&D (Pesquisa e Desenvolvimento)** escalável.

- **Fábrica de Software Autônoma:** Pode ser acoplado a um repositório GitHub via CI/CD. Quando um *Issue* é aberto, o ecossistema lê, faz engenharia reversa, cria os testes (TDD), escreve o código e abre um *Pull Request*.
- **Universidade Sintética:** Pesquisadores podem usar o sistema para processar 500 artigos do PubMed em uma noite, extraindo apenas os consensos lógicos (via MiroFish Graph Memory) para acelerar a descoberta de novos medicamentos.
- **Editora Automatizada (KDP):** Escritores podem gerar rascunhos, solicitar ilustrações internas didáticas, diagramação LaTeX e exportação direta para a Amazon Kindle Direct Publishing.
- **Escalabilidade Horizontal:** Como usamos a arquitetura *Blackboard* e o protocolo A2A, você pode plugar este ecossistema em clusters Kubernetes, distribuindo os 134 agentes em diferentes nós de processamento.

---

## 📁 Estrutura do Repositório

```text
opencode-ecosystem-core/
├── marceloclaro/          # Orquestrador supremo MarceloClaroOrchestrator
├── mci/                   # Metacognitive Interconnect — barramento central
│   ├── oqs/               # Optimal Question Scanner
│   ├── vsee/              # Vector Shortcut Execution Engine
│   ├── egs/               # Ethical Governance Scanner
│   ├── pipeline/          # Pipeline unificado OQS+MCI+VSEE+EGS
│   ├── evidence_graph.py  # 🆕 V2.0 Grafo epistemológico (memória de claims)
│   ├── orchestration.py   # Ciclo científico completo c/ EvidenceGraph
│   ├── hypothesis_engine.py     # V2.0: domínios, priors Bayesianos, SESOI
│   ├── experiment_designer.py   # V2.0: power analysis, confounders
│   ├── statistical_validator.py # V2.0: Bayes Factor, Bonferroni/FDR
│   ├── adversarial_reviewer.py  # V2.0: p-hacking, confounders
│   ├── confidence_calibrator.py # V2.0: Brier score, ECE, abstention
│   ├── scientific_reporter.py   # V2.0: LaTeX Qualis A1, checklist
│   ├── blackboard.py      # Protocolo A2A (Agent Cards)
│   ├── metabus.py         # Global Workspace (pub/sub + persistência)
│   └── reflexion.py       # Reflexion middleware
├── benchmarks/            # Benchmarks Científicos + readiness superhuman
│   └── scientific_reasoning/  # 5 benchmarks + superhuman_suite.py
├── rag/                   # 🆕 Scientific RAG: grounding, citações, abstenção
├── schemas/               # Schemas JSON de contratos científicos
├── transformer/           # AttentionRouter, TransformerPipeline, HTM
├── agents/                # 134 agentes especializados (Agent Cards)
├── research/
│   ├── experiments/       # 🆕 Matrizes de cenários de pesquisa
│   └── pipelines/         # 🆕 Executores de lote integrados
├── sdd/                   # SpecRegistry, SpecVerifier, TDDRunner
├── trust/                 # Trust Engine + Behavioral Gate
├── economy/               # Token Economy (Staking, Slashing, Fee Market)
├── scanners/              # Deep Diagnose M1-M5 + Prioritizer
├── academic/              # MASWOS Pipeline Qualis A1
├── publishing/            # LaTeX, PDF, DOCX, ODT, Cover Designer
├── illustrations/         # Mermaid, MIRA, Graphify
├── gametheory/            # 38 estratégias + Nash, Shapley, Tit-for-Tat
├── mirofish/              # CrossValidator Swarm + GraphMemory
├── reasoning/             # 12 motores: Z3, SymPy, Kanren, Bayesian, Causal, Quantum...
├── webapp/                # Interface Streamlit (6 abas)
├── tests/                 # 263 testes automatizados (suíte operacional verde)
└── CHANGELOG.md
```

---

## 🧪 Executar os Testes

```bash
# Todos os 263+ testes do ecossistema
python3 -m pytest tests/ -v

# Apenas o pipeline científico (v2.0 SuperHuman)
python3 -m pytest tests/test_scientific_superhuman.py -v

# Apenas o pipeline de governança (v1.x compat)
python3 -m pytest tests/test_scientific_governance_pipeline.py -v

# Apenas o runner de lote
python3 -m pytest tests/test_run_research_batch.py -v

# Apenas Scientific RAG + Superhuman Readiness
python3 -m pytest tests/test_scientific_rag_superhuman.py -v

# Apenas Metacognitive Superhuman Suite
python3 -m pytest tests/test_metacognitive_superhuman.py -v
```

---
<div align="center">
  <i>Construído com rigor metodológico, inspirado pela Teoria dos Jogos e desenhado para o futuro.</i><br>
  <b>v2.2.0 — Metacognitive Refinement + Scientific RAG com EvidenceGraph | Apoie o projeto: <a href="https://buymeacoffee.com/geomaker">buymeacoffee.com/geomaker</a></b>
</div>
