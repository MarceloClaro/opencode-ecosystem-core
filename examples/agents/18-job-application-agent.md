# job-application-agent — espelho 18-job-application-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/18-job-application-agent`
- **Descrição**: Generates cover letter, interview prep, and salary range from job description + candidate profile
- **Framework**: crewai · **LLM original**: gpt-4o-mini
- **Tags**: hr, job-search, cover-letter, interview-prep, recruitment
- **Dificuldade**: intermediate

## Padrão arquitetural

Construído com crewai; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

landscape curator R482: padrão MIT 'auto-contido e reexecutável'

Sugestão de ciclo: spec `SPEC-935-R***-job-application-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A crewai ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/18-job-application-agent`.*
