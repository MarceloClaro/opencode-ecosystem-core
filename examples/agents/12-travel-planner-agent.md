# travel-planner-agent — espelho 12-travel-planner-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/12-travel-planner-agent`
- **Descrição**: Multi-agent CrewAI system creating personalized travel itineraries with budget planning
- **Framework**: crewai · **LLM original**: gpt-4o-mini
- **Tags**: travel, planning, crewai, itinerary, budget
- **Dificuldade**: intermediate

## Padrão arquitetural

Construído com crewai; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

web_search local + dados primários (R35) — sem alucinação de cotação

Sugestão de ciclo: spec `SPEC-935-R***-travel-planner-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A crewai ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/12-travel-planner-agent`.*
