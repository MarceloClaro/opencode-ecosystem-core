---
name: landscape-curator
description: Curador da paisagem de agentes externos — consome manifests curados de múltiplas coleções (500-AI-Agents-Projects: 20 agentes auto-contidos, MIT, R482; awesome-llm-apps: 15 templates representativos, Apache-2.0, R521), cruza com o catálogo do Core (197 agent cards) por afinidade lexical auditável e gera LANDSCAPE_REPORT*.md honestos, sem copiar código de terceiros, sem prometer integração e com Observatório para entradas adversarial (veredito não-adotar/observar).
version: '1.1.0'
skills:
- id: landscape-curation
  name: Curadoria de paisagem de agentes
  description: Executa curadoria de agentes externos conforme protocolo SDD/TDD (SPEC-935-R482; R521 multi-coleção).
  tags: [landscape, curation, manifest, catalog, matching]
  examples: [Atualize o landscape report, Cruze agentes externos com o catálogo do Core]
tags: [landscape, curation, catalog, research]
examples: [Atualize o LANDSCAPE_REPORT, Atualize o LANDSCAPE_REPORT_AWESOME_LLM_APPS, Sugira agentes Core afins a um caso de uso externo]
type: curation-agent
category: research
---
# landscape-curator

Curadoria da paisagem de agentes (SPEC-935-R482; R521 multi-coleção).

## Uso
```python
from landscape.curator import LandscapeCurator

curator = LandscapeCurator()          # default: landscape/manifest.json (R482)
report = curator.build_report()        # dict com cases/unmatched/observatory/contadores

# Nova coleção (R521): manifest próprio com keywords por entrada
curator = LandscapeCurator(
    repo_root=".", manifest_path="landscape/manifest_awesome_llm_apps.json"
)
curator.write_report(filename="LANDSCAPE_REPORT_AWESOME_LLM_APPS.md")
```

## Regras
- Manifest curado com metadados (nunca código de terceiros); o "100+" do
  README externo são templates/links — nunca prometidos como integrados.
- Cruzamento lexical auditável (peso 2 em name/tags, 1 na descrição); keywords
  por entrada na coleção (fallback `CASE_KEYWORDS` da R482); casos sem
  afinidade entram em `unmatched` — nunca inventados.
- Entradas `adversarial` (modelos/alegações não validadas externamente) vão ao
  **Observatório** com veredito "não-adotar/observar" e NÃO recebem sugestões
  core (anti-overclaim R142; lição R474).
- Sem código-fonte externo; testes herméticos sem rede/credenciais.
- Relatório contém disclaimer "não constitui certificação externa".