# Exemplos de Agentes — Espelhos Arquiteturais (item 2B)

21 espelhos (1 fundação + 20 pilotos) extraídos do
[500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
(MIT, ashishpatel26), curados no Core como **referência de padrão** — nunca como
cópia de código. Cada espelho documenta: origem, padrão arquitetural, adaptação
SDD/TDD ao Core e lição de design.

## Uso recomendado

1. `python3 -m marceloclaro.cli reverse-scan --target <alvo>` — existe lacuna?
2. Ler o espelho correspondente (ex.: `10-meeting-notes.md` para anotações).
3. Abrir spec `SPEC-935-R***` e implementar com TDD seguindo o **Contrato de adaptação**
   (`00-agent-base-core.md`).

## Índice

| Espelho | Agente | Indústria | Framework |
|---|---|---|---|
| [00-agent-base-core](00-agent-base-core.md) | Fundação — contrato de adaptação | — | — |
| [01-web-research-agent](01-web-research-agent.md) | Web Research Agent | general | langgraph |
| [02-code-review-agent](02-code-review-agent.md) | Code Review Agent | general/code | langgraph |
| [03-pdf-qa-agent](03-pdf-qa-agent.md) | PDF Q&A Agent | general/doc | langchain |
| [04-sql-query-agent](04-sql-query-agent.md) | SQL Query Agent | general/data | langchain |
| [05-email-drafting-agent](05-email-drafting-agent.md) | Email Drafting Agent | general/productivity | langgraph |
| [06-news-summarizer-agent](06-news-summarizer-agent.md) | News Summarizer | general/research | langgraph |
| [07-github-issue-triager](07-github-issue-triager.md) | GitHub Issue Triager | general/code | langgraph |
| [08-data-analysis-agent](08-data-analysis-agent.md) | Data Analysis Agent | general/data | langchain |
| [09-resume-parser-agent](09-resume-parser-agent.md) | Resume Parser Agent | general/data | langchain |
| [10-meeting-notes-agent](10-meeting-notes-agent.md) | Meeting Notes Agent | general/productivity | langchain |
| [11-stock-research-agent](11-stock-research-agent.md) | Stock Research Agent | general/research | langgraph |
| [12-travel-planner-agent](12-travel-planner-agent.md) | Travel Planner Agent | general/productivity | langgraph |
| [13-customer-support-agent](13-customer-support-agent.md) | Customer Support Agent | general/support | langchain |
| [14-social-media-agent](14-social-media-agent.md) | Social Media Agent | general/creative | langgraph |
| [15-unit-test-generator](15-unit-test-generator.md) | Unit Test Generator | general/code | langchain |
| [16-documentation-writer](16-documentation-writer.md) | Documentation Writer | general/code | langgraph |
| [17-recipe-agent](17-recipe-agent.md) | Recipe Agent | general/creative | langchain |
| [18-job-application-agent](18-job-application-agent.md) | Job Application Agent | general/productivity | langgraph |
| [19-competitive-analysis-agent](19-competitive-analysis-agent.md) | Competitive Analysis Agent | general/research | langgraph |
| [20-multi-agent-debate](20-multi-agent-debate.md) | Multi-Agent Debate System | research | langchain |

## Proveniência

Fonte local: `/tmp/opencode/500-ai-agents-projects/agents/` (20 pastas com
`README.md`, `agent.py`, `metadata.yaml`, `requirements.txt`). Licença MIT.
Consolidado também em `_mirror-manifest.json`.