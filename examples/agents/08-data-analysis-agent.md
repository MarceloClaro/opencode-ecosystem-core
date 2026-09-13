# data-analysis-agent — espelho 08-data-analysis-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/08-data-analysis-agent`
- **Descrição**: Chat with CSV/Excel data using natural language queries powered by pandas
- **Framework**: langchain · **LLM original**: gpt-4o
- **Tags**: data-analysis, pandas, csv, analytics, natural-language
- **Dificuldade**: intermediate

## Padrão arquitetural

Construído com langchain; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

landscape curator R482: padrão MIT 'auto-contido e reexecutável'

Sugestão de ciclo: spec `SPEC-935-R***-data-analysis-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langchain ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/08-data-analysis-agent`.*
