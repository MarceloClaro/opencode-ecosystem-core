# code-review-agent — espelho 02-code-review-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/02-code-review-agent`
- **Descrição**: Reviews code for bugs, security issues, performance, and style violations
- **Framework**: langchain · **LLM original**: gpt-4o
- **Tags**: code-review, software-development, security, quality
- **Dificuldade**: beginner

## Padrão arquitetural

Construído com langchain; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

code-reviewer/coder + sd policy:: slashing do Trust Engine p/ entregas reprovadas

Sugestão de ciclo: spec `SPEC-935-R***-code-review-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langchain ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/02-code-review-agent`.*
