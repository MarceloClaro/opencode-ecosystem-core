# web-research-agent — espelho 01-web-research-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/01-web-research-agent`
- **Descrição**: Searches the web for a topic and synthesizes a structured research report
- **Framework**: langgraph · **LLM original**: gpt-4o-mini
- **Tags**: research, web-search, rag, langgraph
- **Dificuldade**: intermediate

## Padrão arquitetural

Construído com langgraph; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

antigravity_web_search + PolymathicConvergence (R486): localizar correspondências externas

Sugestão de ciclo: spec `SPEC-935-R***-web-research-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langgraph ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/01-web-research-agent`.*
