---
name: landscape-curator
description: Curador da paisagem de agentes externos — consome o manifest curado da coleção 500-AI-Agents-Projects (20 agentes auto-contidos, MIT), cruza com o catálogo do Core (196 agent cards) por afinidade lexical auditável e gera LANDSCAPE_REPORT.md honesto, sem copiar código de terceiros e sem prometer integração.
version: '1.0.0'
skills:
- id: landscape-curation
  name: Curadoria de paisagem de agentes
  description: Executa curadoria de agentes externos conforme protocolo SDD/TDD (SPEC-935-R482).
  tags: [landscape, curation, manifest, catalog, matching]
  examples: [Atualize o landscape report, Cruze agentes externos com o catálogo do Core]
tags: [landscape, curation, catalog, research]
examples: [Atualize o LANDSCAPE_REPORT, Sugira agentes Core afins a um caso de uso externo]
type: curation-agent
category: research
---
# landscape-curator

Curadoria da paisagem de agentes (SPEC-935-R482).

## Uso
```python
from landscape.curator import LandscapeCurator

curator = LandscapeCurator()          # usa landscape/manifest.json + agents/catalog/
report = curator.build_report()        # dict com cases/unmatched/contadores
curator.write_report()                 # gera LANDSCAPE_REPORT.md na raiz
```

## Regras
- Manifest curado com os 20 agentes auto-contidos da coleção (MIT); o "500+"
  do README externo são links/casos de uso — nunca prometidos como integrados.
- Cruzamento lexical auditável (peso 2 em name/tags, 1 na descrição); casos sem
  afinidade entram em `unmatched` — nunca inventados.
- Sem código-fonte externo; testes herméticos sem rede/credenciais.
- Relatório contém disclaimer "não constitui certificação externa".