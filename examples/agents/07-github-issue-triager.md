# github-issue-triager — espelho 07-github-issue-triager

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/07-github-issue-triager`
- **Descrição**: Automatically triages GitHub issues with severity, category, and routing recommendations
- **Framework**: langchain · **LLM original**: gpt-4o-mini
- **Tags**: github, devops, triage, issue-management, automation
- **Dificuldade**: intermediate

## Padrão arquitetural

Construído com langchain; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

landscape curator R482: padrão MIT 'auto-contido e reexecutável'

Sugestão de ciclo: spec `SPEC-935-R***-github-issue-triager.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langchain ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/07-github-issue-triager`.*
