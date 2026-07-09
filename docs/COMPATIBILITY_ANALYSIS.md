# Análise de Compatibilidade: OpenCode Ecosystem Core → OpenCode_Ecosystem-main

## 1. Visão Geral dos Ecossistemas

| Aspecto | OpenCode Ecosystem Core | OpenCode_Ecosystem-main |
|---------|------------------------|------------------------|
| **Foco** | Inteligência acadêmica agentiva (descoberta, evolução, revisão) | Pipeline de pesquisa acadêmica (digestão, survey, escrita, submissão) |
| **Skills** | 11+ MCP tools registradas | 8 skills OpenCode (`digest-paper`, `explore-sota`, `write-survey`, `develop-contribution`, `write-paper`, `package-artifacts`, `manage-submission`, `adversarial-review`) |
| **Agentes** | 4+ agentes científicos especializados (EvoSci, Deep Research, Peer Review, Revision) | 38 agentes MASWOS (A0–A38) para pipeline completo de artigo |
| **Slash Commands** | 13+ comandos MCP (su_*) | 13 slash commands acadêmicos |
| **Infraestrutura** | `agentic_science_v2/`, `rag/`, `synthetic_university/` | `references.bib`, `sota/papers/`, `survey/`, `contributions/`, `papers/` |
| **Segurança** | MCP Security (R100) com guard, audit, rate-limit | Ausente |
| **Empacotamento** | 3 pacotes pip (`opencode-{evosci,deep-research,peer-review}`) | Skills auto-contidas |
| **Cobertura** | R82–R104: Descoberta → Evolução → Revisão → Revisão de Manuscritos | Pipeline completo: Digestão → Survey → Escrita → Revisão → Submissão |

## 2. Mapeamento Funcional

### Skills do Fork → Módulos do Core

| Skill do Fork | Função | Módulo Equivalente no Core | Complementar? |
|--------------|--------|---------------------------|:------------:|
| `digest-paper` | Digestão de PDF + síntese + bib | R99 Scientific RAG (AdaptiveRetriever) | Sim |
| `explore-sota` | Busca e triagem de literatura | R102 Deep Research (BFRS+DFRS) | Sim |
| `write-survey` | Escrita de survey em LaTeX | R99 OutlineSynthesizer | Sim |
| `develop-contribution` | Criação de contribuição | R101 Agentic Science (ciclo evolutivo) | Sim |
| `write-paper` | Escrita de manuscrito | R99 CitationGraph | Sim |
| `adversarial-review` | Revisão severa | R103 Peer Review V2 (4 especialistas) | Sim |
| `package-artifacts` | Pacote de submissão | — | Gap |
| `manage-submission` | Gerenciamento de submissão | — | Gap |

### Módulos do Core → Skills do Fork

| Módulo do Core | Função | Skill do Fork Equivalente | Complementar? |
|----------------|--------|--------------------------|:------------:|
| R100 MCP Security | Guard, audit, rate-limit | — (gap no fork) | Novo |
| R101 Agentic Science V2 | Ciclo evolutivo de hipóteses | — (gap no fork) | Novo |
| R102 Deep Research | Evidence Graph + BFRS/DFRS | `explore-sota` (parcial) | Sim |
| R103 Peer Review V2 | 4 especialistas + grafo | `adversarial-review` (parcial) | Sim |
| R104 Agentic Revision | Revisão de manuscritos pós-review | `manage-submission` (parcial) | Sim |
| R99 Scientific RAG | RAG adaptativo + citation graph | `digest-paper` (parcial) | Sim |
| R98 Novelty V2 | Detecção granular de novidade | — (gap no fork) | Novo |

## 3. Análise de Gaps

### O que o OpenCode Ecosystem Core tem que o fork NÃO tem

| Gap | Nosso Módulo | Impacto |
|-----|-------------|---------|
| **Segurança MCP** | R100 — MCPGuard, AuditLogger, ToolVetter, RateLimiter | Fork sem audit trail, rate limiting ou validação de entrada |
| **Evolução darwiniana de hipóteses** | R101 — Agentic Science V2 (seleção, crossover, mutação, herança) | Fork tem pipeline linear, sem descoberta evolutiva |
| **Evidence Graph com busca hierárquica** | R102 — Deep Research (BFRS + DFRS + sandbox) | Fork tem busca linear (`explore-sota`), sem grafo de evidências |
| **Rubrica 8-dimensões + auditagem em grafo** | R103 — Peer Review V2 (4 especialistas + ReviewLedger + AuditGraph) | Fork tem revisor único (`adversarial-review`), sem rastreabilidade |
| **Revisão agentiva de manuscritos** | R104 — Agentic Revision (ReviewAnalyzer, SectionMapper, DiffEngine, RebuttalLetter) | Fork gerencia submissão mas sem revisão agentiva |
| **Detecção granular de novidade** | R98 — Novelty V2 (OpenNovelty-style) | Fork sem análise de novidade |
| **Empacotamento pip** | 3 pacotes pip instaláveis | Fork usa skills OpenCode apenas |

### O que o fork tem que o OpenCode Ecosystem Core NÃO tem

| Gap | Skill do Fork | Impacto |
|-----|--------------|---------|
| **Pipeline completo digestão→survey→escrita→submissão** | Todas as 8 skills encadeadas | Core foca em componentes de inteligência, não no pipeline completo |
| **38 agentes especializados (MASWOS)** | A0–A38 (editor, busca, curadoria, estatística, visualização, ABNT, Qualis, etc.) | Core tem agentes mais genéricos e poderosos, mas em menor número |
| **Slash commands integrados ao ecossistema OpenCode** | 13 comandos nativos | Core usa MCP tools, não slash commands nativos |
| **Template de contribuição com badges** | `develop-contribution` com badges de conformidade | Core não tem sistema de badges |
| **Geração de LaTeX/PDF** | `write-paper` com saída LaTeX → PDF via tectonic | Core gera HTML/DOCX mas não LaTeX nativamente |
| **Gerenciamento de submissão com rebuttal** | `manage-submission` com mapeamento de revisores | Core R104 cobre parte disso |

## 4. Plano de Integração

### Passo 1: Copiar Skills de Integração (R104a)

```bash
# Do OpenCode Ecosystem Core para o workspace do fork
cp -r skills/{evo-science,deep-research,peer-review-v2,mcp-security} \
  /path/to/OpenCode_Ecosystem-main/skills/
```

Cada skill é autocontida e pode ser usada imediatamente.

### Passo 2: Instalar Pacotes Pip (R104b)

```bash
# Opção A: Instalar do diretório local
pip install -e /path/to/packages/opencode-evosci
pip install -e /path/to/packages/opencode-deep-research
pip install -e /path/to/packages/opencode-peer-review

# Opção B: Copiar módulos diretamente
cp -r agentic_science_v2 /path/to/OpenCode_Ecosystem-main/
```

### Passo 3: Adaptar Comandos

Para usar os módulos do core dentro dos slash commands do fork:

```python
# Exemplo: dentro de um comando do fork
from opencode_evosci import MentorAgent, EvoEngine
from opencode_deep_research import BFRSAgent, DFRSAgent
from opencode_peer_review import OrchestratorReviewer
```

### Passo 4: Registrar MCP Tools

Registrar as 4 novas skills como MCP tools no servidor do fork:

```python
# register no MCP server do fork
server.register_tool("su_evo_science", ...)
server.register_tool("su_deep_research_skill", ...)
server.register_tool("su_peer_review_v2_skill", ...)
server.register_tool("su_mcp_security_skill", ...)
```

### Passo 5: Integração Profunda

Para integração mais profunda, conectar:

1. `explore-sota` → R102 Deep Research (BFRS para varredura, DFRS para mergulho)
2. `adversarial-review` → R103 Peer Review V2 (4 especialistas em vez de 1)
3. `manage-submission` → R104 Agentic Revision (revisão automática pós-review)
4. `develop-contribution` → R101 Agentic Science (evolução de hipóteses)

## 5. Roadmap de Convergência

### Fase 1 (Imediata) — Skills Plugáveis
- Copiar os 4 skills de integração para o fork
- Testar cada skill individualmente
- Documentar uso

### Fase 2 (Curto Prazo) — Integração nos Comandos
- Adaptar `explore-sota` para usar R102 Deep Research
- Substituir `adversarial-review` pelo R103 Peer Review V2
- Adicionar `/security-audit` como comando transversal

### Fase 3 (Médio Prazo) — Pipeline Unificado
- Criar skill `full-pipeline` que encadeia:
  `deep-research` (R102) → `evo-science` (R101) → `write-paper` (fork) → `peer-review-v2` (R103) → `agentic-revision` (R104)

### Fase 4 (Longo Prazo) — Fusão dos Ecossistemas
- Unificar agentes MASWOS com agentes do core
- Portar MCP Security como skill obrigatória
- Criar repositório único OpenCode Academic Ecosystem

## 6. Recomendações

1. **Prioridade alta**: Copiar `mcp-security` skill — segurança é requisito básico
2. **Prioridade alta**: Substituir `adversarial-review` por `peer-review-v2` — 4 especialistas > 1
3. **Prioridade média**: Integrar `deep-research` com `explore-sota` — BFRS+DFRS > busca linear
4. **Prioridade média**: Usar `evo-science` para `develop-contribution` — evolução > template fixo
5. **Prioridade baixa**: Empacotar como pip para distribuição mais ampla

---

*Documento gerado em 08/07/2026 como parte do OpenCode Ecosystem Core R104c.*
