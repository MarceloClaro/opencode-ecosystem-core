# meeting-notes-agent — espelho 10-meeting-notes-agent

> Espelho arquitetural do [500-AI-Agents-Projects](https://github.com/MarceloClaro/500-AI-Agents-Projects)
> (MIT, ashishpatel26). Referência de padrão — sem cópia de código.

## Origem

- **Pasta-fonte**: `agents/10-meeting-notes-agent`
- **Descrição**: Converts meeting transcripts into structured notes with action items and decisions
- **Framework**: langchain · **LLM original**: gpt-4o-mini
- **Tags**: productivity, meetings, summarization, action-items
- **Dificuldade**: beginner

## Padrão arquitetural

Construído com langchain; autônomo, com entrypoint `agent.py`, metadados em `metadata.yaml` e `requirements.txt` — o padrão 'auto-contido e reexecutável' que o R482 curou no manifesto.

## Adaptação Core (SDD/TDD)

auxjuris_email_drafter + templates locais; zero LLM externo por padrão

Sugestão de ciclo: spec `SPEC-935-R***-meeting-notes-agent.md` → RED → GREEN → verificação
SpecVerifier + BehavioralGate → reflexão no MetaBus. Prioridade depende da demanda.

## Lição de design

A langchain ensina: pipeline em etapas explícitas com saídas estruturadas — mesma filosofia do `ReverseScanner.scan` (R483).

---
*Gerado a partir do espelho local em `agents/10-meeting-notes-agent`.*
