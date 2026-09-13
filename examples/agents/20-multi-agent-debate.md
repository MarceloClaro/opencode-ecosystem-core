# multi-agent-debate-system — espelho 20-multi-agent-debate

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/20-multi-agent-debate`
- **Descrição**: Two AI agents debate any topic with an AI judge scoring the outcome
- **Framework**: langchain · **LLM original**: gpt-4o
- **Tags**: multi-agent, debate, reasoning, research, argumentation
- **Dificuldade**: advanced

## Padrão arquitetural

Construído com langchain; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

Blackboard A2A + Bernstein-style deterministic orchestration (lições R-bernstein)

Sugestão de ciclo: spec `SPEC-935-R***-multi-agent-debate-system.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langchain ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/20-multi-agent-debate`.*
