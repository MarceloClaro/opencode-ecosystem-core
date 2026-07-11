# Arquitetura: OpenCode Ecosystem Core v3.0

Este documento detalha a arquitetura atual do ecossistema, incluindo o **Pipeline Acadêmico Agentivo (R101–R105)**, **Evolutionary Memory (R97)**, **Scientific RAG Evolved (R99)**, **MCP Security (R100)**, **CI/CD Quality Gates (R106)**, e os subsistemas legados de governança científica e jurídica.

---

## Diagrama de Arquitetura Completo

```mermaid
graph TD
    %% Atores e Orquestrador
    User([Usuário / CLI]) -->|Comandos| Orchestrator[Orquestrador: marceloclaro]
    WebUI([Webapp Streamlit<br>Dashboard + Jurídico]) -->|Painel visual| Orchestrator

    %% Camada de Interface Externa (R116)
    subgraph Interface ["Interface & Instalação (R116)"]
        OpenCodeCLI["OpenCode CLI<br>opencode.json · 165 agentes<br>8 comandos slash"]
        AntigravityCLI["Antigravity CLI<br>ponte para binário agy"]
        ClaudeCLI["Claude Code CLI<br>CLAUDE.md + AGENTS.md"]
        Installer["Instaladores<br>Windows(WSL 1-clique)/Linux/macOS<br>+ Desinstaladores com confirmação"]
    end
    Installer -.->|Provisiona| OpenCodeCLI
    Installer -.->|Provisiona| AntigravityCLI
    Installer -.->|Provisiona| ClaudeCLI
    OpenCodeCLI --> Orchestrator
    AntigravityCLI --> Orchestrator
    ClaudeCLI --> Orchestrator

    %% Camada SDD/TDD
    subgraph SDD [SDD & TDD Engine]
        Spec[SpecRegistry<br>Especificações]
        Ver[SpecVerifier<br>Gate SDD]
        TDD[TDDRunner<br>Red-Green-Refactor]
        LoopSpec["Loop Engineering (R109)<br>LoopSpecification<br>5 Estados Terminais Nomeados"]

        TDD -.->|Valida| Ver
        Ver -.->|Lê| Spec
        LoopSpec -.->|Formaliza| Spec
    end

    %% Camada Transformer
    subgraph TF [Transformer Layer]
        Attn[AttentionRouter<br>Multi-Head]
        Pipe[TransformerPipeline<br>Gerar-Verificar-Revisar]
        HTM[(Hierarchical<br>Memory HTM)]
        Emb[TaskEmbedder<br>d=64]
        
        Attn -.->|Usa| Emb
        HTM -.->|Usa| Emb
    end
    
    %% Pipeline Academico Agentivo (R101-R105)
    subgraph Acad ["Pipeline Academico Agentivo (R101-R105)"]
        EvoSci["R101: EvoSci<br>MentorAgent<br>PrimeResearcherAgent<br>ReviewerAgent<br>EvolutionManagerAgent<br>EvoEngine (Selection/Crossover/Mutation/Inheritance)"]
        DeepRes["R102: Deep Research<br>KnowledgeBaseRegistry<br>BFRSAgent<br>DFRSAgent<br>ExecutionSandbox<br>OrchestratorAgent"]
        PReview["R103: Peer Review<br>RubricEngine (8 dim)<br>ReviewLedger<br>AuditGraph<br>MultiCriticReviewer<br>Revisão às Cegas Real (R115)<br>OrchestratorReviewer"]
        Revision["R104d: Revision<br>ReviewAnalyzer<br>SectionMapper<br>ProposalGenerator<br>DiffEngine (rollback)<br>OrchestratorRevision"]
        Composer["R105: Paper Composer<br>StructurePlanner<br>SectionWriter (6 secoes)<br>CitationFormatter (3 estilos)<br>CrossConsistencyVerifier<br>OrchestratorComposer"]
        
        EvoSci --> DeepRes
        DeepRes --> PReview
        PReview --> Revision
        Revision --> Composer
    end

    %% Fusao real no orquestrador (R108/R109)
    FusionLoop["scientific_discovery_pipeline() (R108)<br>+ run_scientific_discovery_loop() (R109)<br>Gate real · Calibração · Loop com estagnação"]
    Orchestrator -->|Funde nativamente| FusionLoop
    FusionLoop -->|Executa em cadeia| EvoSci
    Composer -->|Retorna ao loop| FusionLoop

    %% Camada Core
    subgraph Core [Core Subsystems]
        Trust["Trust Engine<br>Behavioral Gate<br>GoalDriftDetector (R112)"]
        Eco[Token Economy<br>Staking/Slashing]
        Scan[Scanners & Deep Diagnose<br>M1-M5/Prioritizer]
        Acad[MASWOS<br>Qualis A1 - meta interna, ver Corrigendum]
        Reason["Reasoning<br>12 Engines + Quantum<br>ARCHE RLT - 6 tipos Peirce (R114)<br>Detector de Falácias - 15+4 (R113)"]
        Legal[Legal Reasoning + AuxJuris<br>SPEC-921/922/923/924/925/926/927/928]
        LegalBench[Legal Benchmarks<br>SPEC-928]
        RAG[Scientific RAG<br>Grounding + Citations]
        RAGEvolved["Scientific RAG Evolved (R99)<br>AdaptiveRetriever<br>CitationGraph<br>OutlineSynthesizer"]
        Bench[Superhuman Readiness<br>Benchmarks + Tiers]
        MetaEval[Metacognitive Eval<br>SPEC-920]
        MiroFish[MiroFish<br>Swarm c/ GraphMemory]
        SynthUniv["Synthetic University<br>SPEC-935 · 11 Faculdades"]
        Publishing[Publishing<br>LaTeX & Cover Designer]
        Research["Research<br>Hub c/ OSINT<br>11 fontes: +PubMed/bioRxiv/CORE (R111)<br>CLI: marceloclaro pesquisa (R120)<br>Download: OA direto + Sci-Hub fallback"]
        Illus[Illustrations<br>Mermaid/MIRA/Graph]
        EvoMem["Evolutionary Memory (R97)<br>IdeationMemory<br>ExperimentationMemory<br>HeartbeatReflection<br>StagnationDetector"]
        NoveltyV2["Novelty V2 (R98)<br>ContributionPointExtractor<br>PointwiseLiteratureRetriever<br>PointwiseNoveltyScorer<br>HierarchicalTaxonomyBuilder"]
    end

    %% Seguranca e Qualidade
    subgraph Security ["Seguranca & Qualidade"]
        MCPSec["MCP Security (R100)<br>MCPGuard<br>AuditLogger<br>ToolVetter<br>RateLimiter"]
        CICD["CI/CD Pipeline (R106)<br>GitHub Actions: Lint+Test+Package<br>scripts/quality_report.py<br>scripts/check_coverage.py<br>scripts/run_full_suite.sh"]
        Skills["Skills Exportaveis (R104a)<br>evo-science<br>deep-research<br>peer-review-v2<br>mcp-security"]
        PipPkg["Pip Packages (R104b)<br>opencode-evosci<br>opencode-deep-research<br>opencode-peer-review"]
        DoctorNode["Doctor + Helpdesk (R110)<br>marceloclaro/doctor.py + helpdesk.py<br>+ Prática pública CORRIGENDUM.md"]
    end
    DoctorNode -.->|Diagnostica| Orchestrator
    DoctorNode -.->|Verifica| Spec

    %% Camada Scientific Governance (legado)
    subgraph SGP [Scientific Governance Pipeline v2.x]
        OQS[OQS<br>Optimal Question Scanner]
        SCI[MCI Scientific Core<br>Hipótese·Experimento·Estatística]
        VSEE[VSEE<br>Vector Shortcut Engine]
        EGS[EGS<br>Ethical Governance Scanner]
        EvidenceGraph[EvidenceGraph<br>Memória Epistemológica]
        
        OQS --> SCI
        SCI --> VSEE
        VSEE --> EGS
        EGS -.->|Registra| EvidenceGraph
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
    Orchestrator -->|1. Cria Spec| Spec
    Orchestrator -->|2. Recuperação em 2 níveis| HTM
    HTM -->|Lê Episódica| Mem
    Orchestrator -->|3. Gate & Roteia| Trust
    Trust -->|Libera| Attn
    Attn -->|Publica Volunteer| BB
    Orchestrator -->|4. Executa TDD| Pipe
    Pipe -->|Verifica| Ver
    Orchestrator <-->|Usa| Core
    
    %% Conexões do pipeline academico
    Orchestrator -->|5. Pipeline Academico| EvoSci
    EvoSci -->|Alimenta| DeepRes
    DeepRes -->|Produz evidencia| PReview
    PReview -->|Gera revisao| Revision
    Revision -->|Manuscrito revisado| Composer
    Composer -->|Artigo final| Orchestrator
    
    %% Conexões de suporte
    Acad -->|Consulta evidências| RAG
    Reason -->|Grounding científico| RAG
    RAG -->|Métricas| Bench
    RAGEvolved -->|Citacoes em grafo| DeepRes
    EvoMem -->|Memoria de direcoes| EvoSci
    NoveltyV2 -->|Analise de novidade| EvoSci
    
    MB -->|Traços e reflexões| MetaEval
    Trust -->|Confiança e outcomes| MetaEval
    Orchestrator -->|6. Raciocínio Jurídico| Legal
    
    Legal -->|Subsunção + Ponderação| Reason
    Legal -->|Interpretação Constitucional| MetaEval
    Legal -->|RAG jurídico + Datajud| RAG
    Legal -->|Agentes jurídicos A2A| BB
    Legal -->|Especialização por 7 ramos| LegalBench
    LegalBench -->|tiers conservadores| MetaEval
    
    %% Seguranca
    MCPSec -.->|Protege| MB
    CICD -.->|Valida qualidade| Pipe
    Skills -.->|Exporta| BB
    PipPkg -.->|Distribui| External
    
    SynthUniv -->|10k+ combinações via MiroFish| MiroFish
    SynthUniv -->|Publica descobertas| MB
    EGS -->|Reflete Resultado| MB
    
    %% Agentes
    subgraph Agents [Catálogo de Agentes 160+]
        A1[Researcher]
        A2[Coder]
        A3[Reviewer]
        A4[32 MASWOS Agents]
        A5[Academic Writer]
        A6[Deep Research]
        A7[Peer Review]
        A8[Paper Composer]
        A9[Revision Agent]
        A10[EvoSci Agent]
    end
    
    %% Fluxo de Agentes
    Agents -.->|Registra Agent Card| BB
    BB -.->|Call for Proposals| Agents
    Agents -->|Voluntaria-se| BB
    Agents -->|Conclui Tarefa| Ref
    
    %% MCP
    MCP[MCP Server 14 Tools] -->|Expõe API| MCI
    External[External Tools / LLMs] -->|JSON-RPC| MCP
```

---

## Fluxo de Vida de uma Tarefa no Pipeline Acadêmico

### 1. Descoberta (R101 — EvoSci)
O **MentorAgent** constrói o espaço do problema e gera direções de pesquisa. O **PrimeResearcherAgent** decompõe e gera soluções candidatas. O **ReviewerAgent** avalia com scores dimensionais. O **EvolutionManagerAgent** mantém memórias de ideação e experimentação. O **EvoEngine** executa o ciclo evolutivo: Selection → Crossover → Mutation → Inheritance, com detecção de estagnação.

### 2. Pesquisa Profunda (R102 — Deep Research)
O **KnowledgeBaseRegistry** gerencia fontes simuladas. O **BFRSAgent** explora conexões imediatas em largura. O **DFRSAgent** constrói cadeias multi-hop. O **EvidenceGraph** acumula entidades, relações e evidências com proveniência. O **OrchestratorAgent** planeja, roteia BF/DF, aplica gate de suficiência e sintetiza.

### 3. Revisão por Pares (R103 — Agentic Peer Review)
O **RubricEngine** instancia 8 meta-dimensões de avaliação. O **ReviewLedger** rastreia claims, evidências e riscos. O **AuditGraph** (integrado ao R102) ancora evidências. O **MultiCriticReviewer** executa 4 críticos em paralelo. O **OrchestratorReviewer** executa o pipeline: drafting → ledger → grounding → audit → gate → synthesis.

### 4. Revisão de Manuscrito (R104d — Agentic Revision)
O **ReviewAnalyzer** extrai claims, riscos e ações do pacote de revisão R103. O **SectionMapper** mapeia claims para seções. O **ProposalGenerator** gera propostas de correção com alternativas. O **DiffEngine** aplica diffs controlados com rollback. O **OrchestratorRevision** executa: analyze → map → propose → apply → verify → report.

### 5. Composição Final (R105 — Paper Composer)
O **StructurePlanner** gera outline por venue (ABNT, APA, IEEE). O **SectionWriter** escreve 6 seções com fallbacks para inputs vazios. O **CitationFormatter** formata em 3 estilos. O **CrossConsistencyVerifier** executa 5 verificações de consistência interna. O **OrchestratorComposer** executa: plan → write → format → verify → export.

---

## Subsistemas de Suporte

### Evolutionary Memory (R97)
Memória persistente que registra direções de pesquisa, estratégias, outcomes de experimentos e detecta estagnação. Usada pelo EvoSci para evitar re-exploração de direções falhadas e sugerir pivots.

### Scientific RAG Evolved (R99)
O `rag/evolved.py` fornece:
- **AdaptiveRetriever:** analisa complexidade da query (simple/moderate/complex) com 3 estratégias
- **CitationGraph:** grafo direcionado com BFS até max_depth
- **OutlineSynthesizer:** gera outlines com templates temáticos
- **RAGEvolved:** roteia automaticamente entre answer_simple e answer_structured

### MCP Security (R100)
Camada que envolve o servidor MCP com:
- **MCPGuard:** valida argumentos contra JSON Schema
- **AuditLogger:** registro estruturado de todas as chamadas
- **ToolVetter:** detecta prompt injection, command injection, path traversal, SQLi
- **RateLimiter:** token bucket por caller

### CI/CD Pipeline (R106)
Infraestrutura de qualidade com:
- **GitHub Actions:** 3 jobs (lint → test matrix → package build)
- **quality_report.py:** score 0-10 com análise de testes, cobertura e lint
- **check_coverage.py:** gate que bloqueia se cobertura < 80% ou testes falham

---

## Especificações Formais (SDD)

Cada ciclo possui uma especificação formal em `specs/SPEC-935-R*.md`:

| Spec | Ciclo | Critérios |
|---|---|---|
| SPEC-935-R97 | Evolutionary Memory | 9 CA |
| SPEC-935-R98 | Novelty V2 | 10 CA |
| SPEC-935-R99 | RAG Evolved | 8 CA |
| SPEC-935-R100 | MCP Security | 9 CA |
| SPEC-935-R101 | Agentic Science V2 | 10 CA |
| SPEC-935-R102 | Deep Research | 10 CA |
| SPEC-935-R103 | Peer Review | 10 CA |
| SPEC-935-R104a | Integration Skills | 7 CA |
| SPEC-935-R104b | Pip Packages | 6 CA |
| SPEC-935-R104c | Compatibility Doc | 4 CA |
| SPEC-935-R104d | Manuscript Revision | 8 CA |
| SPEC-935-R105 | Paper Composer | 8 CA |
| SPEC-935-R106 | CI/CD Pipeline | 7 CA |
| SPEC-935-R107 | Auditoria Sistêmica + Hardening | 9 CA |
| SPEC-935-R108 | Fusão do Pipeline Científico no Orquestrador MarceloClaro | 10 CA |
| SPEC-935-R109 | Loop Engineering: Loop Real + Especificação Formal no SDD | 7 CA |
| SPEC-935-R110 | Doctor (Diagnóstico de Saúde) + Prática de CORRIGENDUM | 7 CA |
| SPEC-935-R111 | Expansão de Fontes de Pesquisa (PubMed, bioRxiv, CORE) | 6 CA |
| SPEC-935-R112 | Goal Drift Detection no Trust Engine | 5 CA |
| SPEC-935-R113 | Detector de Falácias Lógicas e Vieses Cognitivos | 5 CA |
| SPEC-935-R114 | ARCHE RLT: Reasoning Logic Tree (SPEC-057) | 5 CA |
| SPEC-935-R115 | Revisão às Cegas Real (Double-Blind) no R103 | 6 CA |
| SPEC-935-R116 | Instalação Multiplataforma, Ícone Próprio, Claude CLI e Manual/Helpdesk | 11 CA |
| SPEC-935-R117 | Mapa Interativo da Arquitetura + Documentação Dupla-Registro | 6 CA |
| SPEC-935-R118 | Correção do Handshake MCP em metacognitive-interconnect | 7 CA |

---

## Fusão do Pipeline Científico no Orquestrador (R108)

A partir do R108, `MarceloClaroOrchestrator.scientific_discovery_pipeline()`
executa o pipeline R101→R102→R103→R104d→R105 nativamente — a conexão
`Orchestrator -->|5. Pipeline Academico| EvoSci` no diagrama acima deixou de
ser apenas aspiracional. O pipeline agora passa por:

- **Gate real** entre R103 e R104d/R105 (`export_gate_passed`), com parada
  efetiva do pipeline em vez de continuação cega
- **Calibração de confiança** (Brier Score) via `mci/confidence_calibrator.py`
  em cada estágio
- **Avaliação metacognitiva SPEC-920** sobre os traços reais de cada run
  (`mci/metacognitive_evaluator.py`), não apenas o benchmark sintético estático
- Eventos publicados no MetaBus e aprendizado no Trust Engine por estágio

`webapp/pipeline_helpers.py::run_full_academic_pipeline` delega a esse método
em vez de encadear os 5 estágios manualmente na camada de UI. Ver
`specs/SPEC-935-R108.md`.

---

## Loop Engineering (R109)

Inspirado em Macedo (2026, arXiv:2607.00038), `sdd/loop_spec.py` formaliza
o conceito de **loop specification** — distinto de uma `Specification` de
entrega única do SDD — como um artefato com trigger justificado, objetivo
verificável, verificação em escada de 5 níveis, arquitetura,
estados terminais nomeados, detector de estagnação e memória persistente.

`MarceloClaroOrchestrator.run_scientific_discovery_loop()` é o primeiro
loop real do ecossistema sob essa disciplina: repete
`scientific_discovery_pipeline` (R108) até um de cinco estados terminais
nomeados (`success`, `no_op`, `blocked`, `stalled`, `exhausted`, `error`),
nunca confundindo erro ou esgotamento de orçamento com sucesso, e para
antecipadamente por estagnação do `readiness_score` (SPEC-920) quando o
resultado para de melhorar. O trigger permanece manual (o ecossistema não
tem scheduler); a verificação (gate do R103) opera inteiramente na zona
autônoma da escada (nível 1, determinística), sem juiz de modelo
envolvido. Ver `specs/SPEC-935-R109.md` e `specs/loops/scientific-discovery-loop.md`.

---

## Métricas de Maturidade

| Métrica | v2.5.0 | v3.0.0 (atual) |
|---|---|---|
| Testes | 617 | **1266** |
| Ciclos de evolução | 49 | **76** |
| MCP Tools | 8 | **14** |
| Agentes | 156 | **160+** |
| Score médio | — | **9.4/10** |
| Skills exportáveis | 0 | **4** |
| Pip packages | 0 | **3** |
| Cobertura estimada | — | **84%** |
| CI/CD | ❌ | **GitHub Actions** |

> "Score médio" e "Agentes" têm ressalvas de leitura em [`CORRIGENDUM.md`](CORRIGENDUM.md): o primeiro é autoavaliação interna por ciclo, não benchmark externo; o segundo conta agent cards elegíveis para delegação, não processos de IA sempre ativos.
