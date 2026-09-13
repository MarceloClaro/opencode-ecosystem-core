# social-media-content-agent — espelho 14-social-media-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/14-social-media-agent`
- **Descrição**: Generates platform-optimized content for Twitter, LinkedIn, and Instagram
- **Framework**: crewai · **LLM original**: gpt-4o-mini
- **Tags**: social-media, content, marketing, crewai, copywriting
- **Dificuldade**: beginner

## Padrão arquitetural

Construído com crewai; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

landscape curator R482: padrão MIT 'auto-contido e reexecutável'

Sugestão de ciclo: spec `SPEC-935-R***-social-media-content-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A crewai ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/14-social-media-agent`.*
