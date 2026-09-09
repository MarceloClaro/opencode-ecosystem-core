<div align="center">

<img src="https://avatars.githubusercontent.com/u/58664974?s=400&u=b58dbf2c479bff1f942355f0ce28106f0b81ecae&v=4" width="150" height="150" style="border-radius: 50%; border: 4px solid #1565c0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" alt="Marcelo Claro Laranjeira"/>

# MARCELO CLARO LARANJEIRA

### Professor de Geografia · Pedagogo · Desenvolvedor Científico

**55 seguidores · 66 seguindo · 310 contribuições**

[![GitHub](https://img.shields.io/badge/GitHub-marceloclaro-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MarceloClaro)
[![ORCID](https://img.shields.io/badge/ORCID-0000--0001--8996--2887-A6CE39?style=for-the-badge&logo=orcid&logoColor=white)](https://orcid.org/0000-0001-8996-2887)
[![Website](https://img.shields.io/badge/Website-geomaker-00ACC1?style=for-the-badge&logo=googleearth&logoColor=white)](https://bit.ly/geomaker)
[![Location](https://img.shields.io/badge/Location-Crateús%20CE-FF5722?style=for-the-badge&logo=googlemaps&logoColor=white)](https://maps.google.com/?q=Crateús+CE+Brasil)

---

**"Transformando dados em conhecimento, e conhecimento em ferramentas para a educação e a ciência aberta."**

</div>

---

## 🧠 OpenCode Ecosystem Core

<div align="center">

### Ecossistema de Orquestração Multi-Agente para Pesquisa Científica e Automação

![GitHub Stars](https://img.shields.io/github/stars/MarceloClaro/opencode-ecosystem-core?style=flat-square&logo=github)
![GitHub Forks](https://img.shields.io/github/forks/MarceloClaro/opencode-ecosystem-core?style=flat-square&logo=github)
![GitHub Issues](https://img.shields.io/github/issues/MarceloClaro/opencode-ecosystem-core?style=flat-square)
![GitHub License](https://img.shields.io/github/license/MarceloClaro/opencode-ecosystem-core?style=flat-square)
![Python Version](https://img.shields.io/badge/python-3.10+-blue?style=flat-square&logo=python&logoColor=white)

---

**205 Agentes** · **303 Specs** · **160 Propostas de Pesquisa** · **Auto-Score 97/100**

</div>

---

## 📑 Navegação Rápida

| Seção | Descrição |
|---|---|
| [🚀 Instalação One-Click](#-instalação-one-click) | Instale tudo com um único comando |
| [🗑️ Desinstalação](#-desinstalação-total) | Remova tudo com um clique |
| [🏗️ Arquitetura](#-arquitetura-do-ecossistema) | Como o ecossistema funciona |
| [⚡ Fluxo de Trabalho](#-fluxo-de-trabalho) | Ciclo completo de operação |
| [🔬 Pipeline Acadêmico](#-pipeline-acadêmico) | Pesquisa científica automatizada |
| [🤖 Agentes](#-agentes-especializados) | 205 especialistas por domínio |
| [📊 Dados](#-dados-científicos) | 160 propostas e 243 datasets |
| [🛠️ Comandos](#-comandos-úteis) | Tudo que você pode fazer |
| [📚 Documentação](#-documentação) | Guias detalhados |
| [👤 Autor](#-sobre-o-autor) | Quem criou este projeto |

---

## 🚀 Instalação One-Click

<div align="center">

### 🪟 Windows

**Um único comando no PowerShell (como Administrador):**

```powershell
wsl --install -d Ubuntu
```

Após reiniciar, abra o **Ubuntu** e cole:

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

### 🐧 Linux / 🍎 macOS

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/setup.sh | bash
```

### ✅ Após a instalação

```bash
source ~/opencode-ecosystem-core/.venv/bin/activate
python3 -m marceloclaro.cli helpdesk
```

</div>

---

## 🗑️ Desinstalação Total

<div align="center">

### Remover apenas o ecossistema

```bash
curl -sSL https://raw.githubusercontent.com/MarceloClaro/opencode-ecosystem-core/main/uninstall.sh | bash
```

### Remover WSL do Windows (Tudo)

**PowerShell como Administrador:**

```powershell
wsl --unregister Ubuntu
dism.exe /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux
dism.exe /online /disable-feature /featurename:VirtualMachinePlatform
```

</div>

---

## 🏗️ Arquitetura do Ecossistema

### Visão Geral — Como Tudo se Conecta

```mermaid
flowchart TB
    subgraph ENTRADA ["🎯 ENTRADA"]
        USER["👤 Pessoa ou Automação"]
        CLI["⌨️ CLI marceloclaro"]
    end

    subgraph NUCLEO ["🧠 NÚCLEO INTELIGENTE"]
        ORQ["🤖 MarceloClaroOrchestrator"]
        ATT["🎯 AttentionRouter"]
        META["🧠 MetaBus"]
        BB["📋 Blackboard A2A"]
    end

    subgraph SDD ["📝 SDD/TDD"]
        SPEC["📄 SpecRegistry"]
        VER["✅ SpecVerifier"]
        TDD["🔄 TDDRunner"]
    end

    subgraph AGENTES ["👥 205 AGENTES"]
        ACAD["🎓 Acadêmico (45)"]
        TECH["💻 Técnico (40)"]
        DOMAIN["🏥 Domínio (30)"]
        RESEARCH["🔬 Pesquisa (25)"]
        SUPPORT["🛠️ Suporte (65)"]
    end

    subgraph INTEGRACOES ["🔌 INTEGRAÇÕES"]
        MCP["📡 6 MCPs"]
        LITERT["📱 LiteRT-LM"]
        COLIBRI["🐦 Colibri OLMoE"]
        Z3["🔢 Z3/SymPy"]
    end

    subgraph SAIDA ["📊 SAÍDA"]
        DOC["📄 Documentos"]
        PRES["🎯 Apresentações"]
        PAPER["📝 Artigos"]
        RAG["📚 Scientific RAG"]
    end

    USER --> CLI
    CLI --> ORQ
    ORQ --> ATT
    ORQ --> META
    ORQ --> BB
    ORQ --> SPEC
    ORQ --> VER
    ORQ --> TDD
    ORQ --> AGENTES
    ORQ --> INTEGRACOES
    ORQ --> SAIDA

    META <--> BB
    SPEC --> VER
    TDD --> VER

    ATT --> ACAD
    ATT --> TECH
    ATT --> DOMAIN
    ATT --> RESEARCH
    ATT --> SUPPORT

    ACAD --> DOC
    TECH --> PRES
    DOMAIN --> PAPER
    RESEARCH --> RAG

    style ENTRADA fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1
    style NUCLEO fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    style SDD fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    style AGENTES fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#e65100
    style INTEGRACOES fill:#fce4ec,stroke:#c62828,stroke-width:2px,color:#b71c1c
    style SAIDA fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#006064
```

---

### Arquitetura Técnica — Camadas Internas

```mermaid
flowchart LR
    subgraph L1 ["Camada 1: Interface"]
        CLI2["CLI Python"]
        WEB["API Web"]
        MCP2["MCP Servers"]
    end

    subgraph L2 ["Camada 2: Orquestração"]
        ORQ2["MarceloClaroOrchestrator"]
        ROUTE["Attention Router"]
        QUEUE["Task Queue"]
    end

    subgraph L3 ["Camada 3: Memória"]
        MB["MetaBus Global"]
        BB2["Blackboard"]
        EVO["Evolution Registry"]
        TRUST["Trust Engine"]
    end

    subgraph L4 ["Camada 4: Execução"]
        SDD2["Spec Engine"]
        TDD2["TDD Runner"]
        AG2["Agent Pool (205)"]
    end

    subgraph L5 ["Camada 5: Integração"]
        MCP3["MCP Clients"]
        LLM["LLM Providers"]
        FS["File System"]
        NET["Network"]
    end

    L1 --> L2
    L2 --> L3
    L2 --> L4
    L3 --> L5
    L4 --> L5

    style L1 fill:#e3f2fd,stroke:#1565c0
    style L2 fill:#f3e5f5,stroke:#7b1fa2
    style L3 fill:#e8f5e9,stroke:#2e7d32
    style L4 fill:#fff3e0,stroke:#ef6c00
    style L5 fill:#fce4ec,stroke:#c62828
```

---

## ⚡ Fluxo de Trabalho

### Ciclo Principal — Perceber → Especificar → Delegar → Executar → Verificar → Refletir

```mermaid
flowchart TD
    START(["🚀 Início da Tarefa"]) --> P["👁️ 1. PERCEBER"]
    P --> P1["Consulta MetaBus"]
    P1 --> P2["Recupera contexto"]
    P2 --> P3["Verifica lições passadas"]
    P3 --> E["📝 2. ESPECIFICAR"]

    E --> E1{"Spec existe?"}
    E1 -->|Sim| E2["Recupera spec existente"]
    E1 -->|Não| E3["Cria nova spec"]
    E2 --> D["👥 3. DELEGAR"]
    E3 --> D

    D --> D1["Publica CFP no Blackboard"]
    D1 --> D2["Agentes se voluntariam"]
    D2 --> D3["Seleciona melhor agente"]
    D3 --> EX["⚙️ 4. EXECUTAR"]

    EX --> EX1["Ciclo RED-GREEN-REFACTOR"]
    EX1 --> EX2["Implementa solução"]
    EX2 --> EX3["Roda testes"]
    EX3 --> V["✅ 5. VERIFICAR"]

    V --> V1["Gate SDD"]
    V1 --> V2{"Aprovado?"}
    V2 -->|Sim| R["🔄 6. REFLETIR"]
    V2 -->|Não| EX

    R --> R1["Registra lições"]
    R1 --> R2["Atualiza Trust Engine"]
    R2 --> R3["Evolution Registry"]
    R3 --> DONE(["✅ Tarefa Concluída"])

    style START fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style P fill:#f3e5f5,stroke:#7b1fa2
    style E fill:#e8f5e9,stroke:#2e7d32
    style D fill:#fff3e0,stroke:#ef6c00
    style EX fill:#fce4ec,stroke:#c62828
    style V fill:#e0f7fa,stroke:#00838f
    style R fill:#f1f8e9,stroke:#558b2f
    style DONE fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

### Fluxo de Decisão — Qual Agente Usar?

```mermaid
flowchart TD
    TASK["📋 Nova Tarefa"] --> CLASS{"Classificação"}

    CLASS -->|"Pesquisa científica"| ACAD["🎓 Pipeline Acadêmico"]
    CLASS -->|"Código/programação"| TECH["💻 Agente Técnico"]
    CLASS -->|"Domínio específico"| DOM["🏥 Especialista"]
    CLASS -->|"Apresentação"| PRES["🎯 MIRA"]
    CLASS -->|"Formal/matémático"| FORM["🔢 Formal Verifier"]

    ACAD --> A1["Busca literatura"]
    ACAD --> A2["Coleta evidências"]
    ACAD --> A3["Revisão por pares"]
    ACAD --> A4["Redação do artigo"]

    TECH --> T1["Analisa código"]
    TECH --> T2["Implementa solução"]
    TECH --> T3["Testa e valida"]
    TECH --> T4["Documenta"]

    DOM --> D1["Consulta especialista"]
    DOM --> D2["Aplica conhecimento"]
    DOM --> D3["Gera relatório"]

    PRES --> P1["Extrai conteúdo"]
    PRES --> P2["Planeja slides"]
    PRES --> P3["Constrói deck"]
    PRES --> P4["Valida consistência"]

    FORM --> F1["Formaliza problema"]
    FORM --> F2["Verifica prova"]
    FORM --> F3["Gera certificado"]

    style TASK fill:#e3f2fd,stroke:#1565c0,stroke-width:3px
    style CLASS fill:#f3e5f5,stroke:#7b1fa2
    style ACAD fill:#e8f5e9,stroke:#2e7d32
    style TECH fill:#fff3e0,stroke:#ef6c00
    style DOM fill:#fce4ec,stroke:#c62828
    style PRES fill:#e0f7fa,stroke:#00838f
    style FORM fill:#f1f8e9,stroke:#558b2f
```

---

## 🔬 Pipeline Acadêmico

### Fluxo Completo — Da Ideia ao Artigo Publicado

```mermaid
flowchart LR
    subgraph FASE1 ["Fase 1: Descoberta"]
        I["💡 Ideia"]
        G["🎯 Gap de Pesquisa"]
        P["📋 Proposta"]
    end

    subgraph FASE2 ["Fase 2: Pesquisa"]
        L["📚 Revisão Literária"]
        E["📊 Coleta Dados"]
        M["⚙️ Metodologia"]
    end

    subgraph FASE3 ["Fase 3: Análise"]
        A["📈 Análise Estatística"]
        V["🔍 Validação"]
        R["📊 Resultados"]
    end

    subgraph FASE4 ["Fase 4: Escrita"]
        D["📝 Rascunho"]
        REV["🔄 Revisão"]
        F["📄 Final"]
    end

    subgraph FASE5 ["Fase 5: Publicação"]
        SUB["📤 Submissão"]
        PR["👥 Peer Review"]
        PUB["🎉 Publicação"]
    end

    I --> G --> P
    P --> L --> E --> M
    M --> A --> V --> R
    R --> D --> REV --> F
    F --> SUB --> PR --> PUB

    style FASE1 fill:#e3f2fd,stroke:#1565c0
    style FASE2 fill:#f3e5f5,stroke:#7b1fa2
    style FASE3 fill:#e8f5e9,stroke:#2e7d32
    style FASE4 fill:#fff3e0,stroke:#ef6c00
    style FASE5 fill:#fce4ec,stroke:#c62828
```

---

### Detalhes do Pipeline Acadêmico

```mermaid
flowchart TD
    subgraph INPUT ["📥 ENTRADA"]
        TOPIC["🎯 Tema de Pesquisa"]
        GAP["🔍 Gap Identificado"]
    end

    subgraph PROCESS ["⚙️ PROCESSAMENTO"]
        SEARCH["📚 Busca Multi-Fonte"]
        SEARCH -->|"OpenAlex"| OA["243M papers"]
        SEARCH -->|"CrossRef"| CR["150M works"]
        SEARCH -->|"PubMed"| PM["36M abstracts"]
        SEARCH -->|"arXiv"| AR["2M e-prints"]
        SEARCH -->|"Kaggle"| KG["200K datasets"]

        CURATE["🔍 Curadoria Automática"]
        CURATE --> RELEVANCE["Score de Relevância"]
        CURATE --> QUALITY["Filtro de Qualidade"]
        CURATE --> DEDUP["Deduplicação"]

        ANALYZE["📊 Análise Profunda"]
        ANALYZE --> CITATION["Análise de Citações"]
        ANALYZE --> TREND["Detecção de Tendências"]
        ANALYZE --> GAP2["Identificação de Gaps"]
    end

    subgraph OUTPUT ["📤 SAÍDA"]
        REPORT["📄 Relatório Executivo"]
        MANUSCRIPT["📝 Manuscrito"]
        SUPPLEMENT["📎 Material Suplementar"]
    end

    TOPIC --> SEARCH
    GAP --> SEARCH
    RELEVANCE --> CURATE
    QUALITY --> CURATE
    DEDUP --> ANALYZE
    CITATION --> REPORT
    TREND --> MANUSCRIPT
    GAP2 --> SUPPLEMENT

    style INPUT fill:#e3f2fd,stroke:#1565c0
    style PROCESS fill:#f3e5f5,stroke:#7b1fa2
    style OUTPUT fill:#e8f5e9,stroke:#2e7d32
```

---

## 🔄 Ciclo SDD/TDD

### Spec-Driven Development + Test-Driven Development

```mermaid
flowchart TD
    subgraph SDD ["📝 SDD — Spec-Driven Development"]
        SPEC1["📄 Cria Spec"]
        SPEC1 --> CRIT["🎯 Critérios de Aceitação"]
        CRIT --> TESTS["🧪 Testes Vinculados"]
    end

    subgraph TDD ["🔄 TDD — Test-Driven Development"]
        RED["🔴 RED — Testes Falham"]
        RED --> GREEN["🟢 GREEN — Implementação Mínima"]
        GREEN --> REFACTOR["🔵 REFACTOR — Melhora Código"]
        REFACTOR --> VERIFY["✅ VERIFY — Todos Passam"]
    end

    subgraph GATE ["🚪 GATE — Validação"]
        GATE1["🔍 SpecVerifier"]
        GATE1 --> CHECK{"Todos critérios OK?"}
        CHECK -->|Sim| APPROVE["✅ APROVADO"]
        CHECK -->|Não| REJECT["❌ REPROVADO"]
        REJECT --> RED
    end

    SPEC1 --> RED
    TESTS --> RED
    VERIFY --> GATE1

    style SDD fill:#e3f2fd,stroke:#1565c0
    style TDD fill:#e8f5e9,stroke:#2e7d32
    style GATE fill:#fff3e0,stroke:#ef6c00
    style RED fill:#ffebee,stroke:#c62828
    style GREEN fill:#e8f5e9,stroke:#2e7d32
    style REFACTOR fill:#e3f2fd,stroke:#1565c0
    style APPROVE fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style REJECT fill:#ffebee,stroke:#c62828,stroke-width:3px
```

---

## 🤖 Agentes Especializados

### Distribuição por Domínio

```mermaid
pie title 205 Agentes por Domínio
    "Acadêmico / Pesquisa" : 45
    "Técnico / Código" : 40
    "Domínio Específico" : 30
    "Pesquisa / Dados" : 25
    "Suporte / QA" : 65
```

### Mapa de Agentes Principais

```mermaid
flowchart TB
    subgraph ACADEMIC ["🎓 Agentes Acadêmicos"]
        A1["A00 — Editor-Chefe PhD"]
        A2["A01 — Escopo"]
        A3["A02 — Busca"]
        A4["A03 — Evidências"]
        A5["A04 — Estrutura"]
        A6["A05 — Revisão"]
        A7["A06 — Metodologia"]
        A8["A07 — Estatística"]
        A9["A08 — Visualização"]
        A10["A09 — Resultados"]
        A11["A10 — Discussão"]
        A12["A11 — Conclusão"]
        A13["A12 — Bibliografia"]
        A14["A13 — QA Qualis"]
        A15["A14 — Consistência"]
        A16["A15 — Resumo"]
        A17["A16 — Integração"]
        A18["A17 — Framework"]
        A19["A18 — Dados"]
        A20["A19 — Auditoria"]
    end

    subgraph TECH ["💻 Agentes Técnicos"]
        T1["C — Coder"]
        T2["R — Researcher"]
        T3["W — Writer"]
        T4["V — Reviewer"]
        T5["D — Debugger"]
        T6["O — Optimizer"]
        T7["A — Architect"]
    end

    subgraph DOMAIN ["🏥 Especialistas de Domínio"]
        D1["Médico Cardiologista"]
        D2["Médico Neurologista"]
        D3["Médico Radiologista"]
        D4["Especialista KDP"]
        D5["Especialista GIS"]
        D6["Especialista Quântico"]
    end

    ACADEMIC --> TECH
    TECH --> DOMAIN

    style ACADEMIC fill:#e3f2fd,stroke:#1565c0
    style TECH fill:#fff3e0,stroke:#ef6c00
    style DOMAIN fill:#fce4ec,stroke:#c62828
```

---

## 📊 Dados Científicos

### Catalogo de Dados Disponíveis

```mermaid
flowchart LR
    subgraph CATALOG ["📊 CATÁLOGO DE DADOS"]
        PROP["📋 160 Propostas"]
        DS["🗄️ 243 Datasets"]
        AG["🤖 8 Agentes PhD"]
    end

    subgraph DOMAINS ["🎯 POR DOMÍNIO"]
        AI["IA / ML — 20 propostas"]
        HEALTH["Saúde — 20 propostas"]
        BIO["Biologia — 20 propostas"]
        ENV["Meio Ambiente — 20 propostas"]
        ENERGY["Energia — 20 propostas"]
        MATERIAL["Materiais — 20 propostas"]
        SOCIAL["Social — 20 propostas"]
        ECON["Economia — 20 propostas"]
    end

    subgraph SOURCES ["🌍 FONTES"]
        OA2["OpenAlex — 243M papers"]
        CR2["CrossRef — 150M works"]
        PM2["PubMed — 36M abstracts"]
        AR2["arXiv — 2M e-prints"]
        KG2["Kaggle — 200K datasets"]
    end

    CATALOG --> DOMAINS
    CATALOG --> SOURCES

    style CATALOG fill:#e3f2fd,stroke:#1565c0
    style DOMAINS fill:#e8f5e9,stroke:#2e7d32
    style SOURCES fill:#fff3e0,stroke:#ef6c00
```

---

## 🛠️ Comandos Úteis

<div align="center">

| Comando | O que faz | Nível |
|---|---|---|
| `python3 -m marceloclaro.cli` | 🎯 Menu interativo principal | Iniciante |
| `python3 -m marceloclaro.cli doctor` | 🩺 Diagnóstico do sistema | Iniciante |
| `python3 -m marceloclaro.cli helpdesk` | 💡 Ajuda guiada | Iniciante |
| `python3 -m marceloclaro.cli status` | 📊 Status do ecossistema | Intermediário |
| `python3 -m marceloclaro.cli pesquisa "tema"` | 🔍 Pesquisa científica | Intermediário |
| `python3 -m marceloclaro.cli apresentacao /caminho` | 🎨 Gerar apresentação | Avançado |

</div>

---

## 📚 Documentação

<div align="center">

| Documento | Para quem | Descrição |
|---|---|---|
| [QUICKSTART.md](QUICKSTART.md) | 🟢 Iniciantes | Primeiros passos |
| [MANUAL.md](MANUAL.md) | 🟡 Todos | Uso completo da CLI |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 🟠 Desenvolvedores | Arquitetura técnica |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 🟠 Contribuidores | Como participar |
| [SECURITY.md](SECURITY.md) | 🔴 Segurança | Vulnerabilidades |
| [CORRIGENDUM.md](CORRIGENDUM.md) | 📜 Histórico | Correções passadas |
| [CHANGELOG.md](CHANGELOG.md) | 📋 Mudanças | Versões anteriores |

</div>

---

## 🔗 Links Importantes

<div align="center">

| Recurso | URL |
|---|---|
| 🏠 **GitHub** | [github.com/MarceloClaro/opencode-ecosystem-core](https://github.com/MarceloClaro/opencode-ecosystem-core) |
| 🤗 **HuggingFace Core** | [huggingface.co/datasets/marceloclaro/opencode-ecosystem-core](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core) |
| 🔬 **HuggingFace Research** | [huggingface.co/datasets/marceloclaro/opencode-research](https://huggingface.co/datasets/marceloclaro/opencode-research) |
| 📄 **Licença MIT** | [LICENSE](LICENSE) |

</div>

---

## ⚠️ Limites Importantes

<div align="center">

| Limite | Descrição |
|---|---|
| 🔍 **Não é certificação** | Resultados são observados no checkout, não validados externamente |
| 👤 **Revisão humana** | Agentes são ferramentas, não decisores autônomos |
| 🏥 **Domínios sensíveis** | Clínico, jurídico e científico são apoio computacional |
| 🌐 **Serviços externos** | MCPs e modelos podem falhar ou estar indisponíveis |
| 📊 **Métricas internas** | Auto-score é interno, não certificação externa |

</div>

---

## 🤝 Contribuindo

```mermaid
flowchart LR
    FORK["🍴 Fork"] --> BRANCH["🌿 Criar Branch"]
    BRANCH --> CODE["💻 Escrever Código"]
    CODE --> TEST["🧪 Rodar Testes"]
    TEST --> COMMIT["📝 Commit"]
    COMMIT --> PR["📤 Pull Request"]
    PR --> REVIEW["👀 Revisão"]
    REVIEW --> MERGE["✅ Merge"]

    style FORK fill:#e3f2fd,stroke:#1565c0
    style BRANCH fill:#f3e5f5,stroke:#7b1fa2
    style CODE fill:#e8f5e9,stroke:#2e7d32
    style TEST fill:#fff3e0,stroke:#ef6c00
    style COMMIT fill:#fce4ec,stroke:#c62828
    style PR fill:#e0f7fa,stroke:#00838f
    style REVIEW fill:#f1f8e9,stroke:#558b2f
    style MERGE fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
```

---

## 👤 Sobre o Autor

<div align="center">

<img src="https://avatars.githubusercontent.com/u/58664974?s=400&u=b58dbf2c479bff1f942355f0ce28106f0b81ecae&v=4" width="200" height="200" style="border-radius: 50%; border: 4px solid #1565c0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);" alt="Marcelo Claro Laranjeira"/>

### **MARCELO CLARO LARANJEIRA**

**Professor de Geografia · Pedagogo · Desenvolvedor Científico**

---

![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
![ORCID](https://img.shields.io/badge/ORCID-0000--0001--8996--2887-A6CE39?style=for-the-badge&logo=orcid&logoColor=white)
![Website](https://img.shields.io/badge/Website-geomaker-00ACC1?style=for-the-badge&logo=googleearth&logoColor=white)
![Location](https://img.shields.io/badge/Location-Crateús%20CE-FF5722?style=for-the-badge&logo=googlemaps&logoColor=white)

---

**📍 Localização:** Crateús, Ceará, Brasil

**🔗 Links:**
- [GitHub](https://github.com/MarceloClaro)
- [ORCID](https://orcid.org/0000-0001-8996-2887)
- [Website Pessoal](https://bit.ly/geomaker)
- [Google Scholar](https://scholar.google.com/citations?user=marceloclaro)

**🎯 Áreas de Atuação:**
- Geografia e Geotecnologias
- Educação a Distância (EAD)
- Ciência Aberta e Dados Abertos
- Inteligência Artificial Aplicada à Educação
- Sistemas de Informação Geográfica (SIG)

**📊 Estatísticas GitHub:**
- **310** contribuições no último ano
- **55** seguidores
- **66** seguindo
- **Projetos** open source

---

**"A tecnologia é uma ferramenta poderosa, mas é o conhecimento humano que a transforma em soluções para a sociedade."**

</div>

---

## 📄 Licença

Este projeto é licenciado sob a [Licença MIT](LICENSE).

---

<div align="center">

### Feito com ❤️ por [Marcelo Claro Laranjeira](https://github.com/MarceloClaro)

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MarceloClaro)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/datasets/marceloclaro/opencode-ecosystem-core)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**[Voltar ao topo](#-opencode-ecosystem-core)**

</div>
