# customer-support-agent — espelho 13-customer-support-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/13-customer-support-agent`
- **Descrição**: RAG-powered customer support agent with escalation routing using LangGraph
- **Framework**: langgraph · **LLM original**: gpt-4o-mini
- **Tags**: customer-support, rag, langgraph, faiss, escalation
- **Dificuldade**: advanced

## Padrão arquitetural

Construído com langgraph; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

landscape curator R482: padrão MIT 'auto-contido e reexecutável'

Sugestão de ciclo: spec `SPEC-935-R***-customer-support-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langgraph ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/13-customer-support-agent`.*
