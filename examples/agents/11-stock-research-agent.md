# stock-research-agent — espelho 11-stock-research-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/11-stock-research-agent`
- **Descrição**: Real-time stock fundamentals with AI-powered investment analysis
- **Framework**: langchain · **LLM original**: gpt-4o-mini
- **Tags**: finance, stocks, investment, yfinance, analysis
- **Dificuldade**: intermediate

## Padrão arquitetural

Construído com langchain; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

scanners::data_analysis + estatística R07/R20; datasets/proveniência R18

Sugestão de ciclo: spec `SPEC-935-R***-stock-research-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langchain ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/11-stock-research-agent`.*
