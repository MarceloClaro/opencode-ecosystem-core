---
spec_id: SPEC-935-R268
title: Agentes literários e scanners de pesquisa literária internacional
component: agents/catalog + scanners/literary_research_scanners.py
status: verified
test_file: tests/test_r268_literary_agents_research_scanners.py
---

# SPEC-935-R268 — Agentes Literários + Pesquisa Literária Internacional

## Objetivo

Com base nas interações sobre `Molambudos`, criar uma suíte de agentes literários e um agente específico de busca/pesquisa literária para apoiar projetos de criação, estudo, crítica, fundamentação teórica, inovação formal, revisão ética e preparação editorial. Criar também scanners de pesquisa literária, calibrados para rigor técnico e literário internacional.

## Agentes esperados

1. `literary-orchestrator-phd` — coordena projetos literários, specs, scanners, revisão crítica e entregáveis.
2. `literary-narratology-architect-phd` — estrutura narrativa, enredo, rotas, tempo, focalização e arquitetura de partes.
3. `literary-style-voice-phd` — estilo, voz, ritmo, dicção, léxico, registro e revisão textual literária.
4. `literary-character-psychology-phd` — personagens, desejo, agência, conflito, transformação e coerência psicológica.
5. `literary-symbolic-imagery-phd` — símbolos, motivos, imagética, campos sensoriais e coesão metafórica.
6. `literary-ethics-trauma-phd` — ética da representação, trauma, alteridade, violência institucional e anti-exploração.
7. `literary-innovation-editorial-phd` — inovação formal, materialidade do livro, hipertexto, paratextos e design editorial narrativo.
8. `literary-research-scholar-phd` — busca e pesquisa literária: corpus comparativo, bibliografia, teoria, referências internacionais, lacunas e protocolo de evidências.

## Scanners de pesquisa literária esperados

1. **LiteraryBibliographyScanner** — qualidade bibliográfica, autores-chave, diversidade teórica, referências primárias/secundárias e lacunas.
2. **ComparativeCorpusScanner** — comparação de corpus, gêneros, tradições, obras análogas, posicionamento e diferenciação.
3. **TheoreticalFrameworkScanner** — fundamentação teórica, conceitos, adequação metodológica, interdisciplinaridade e operacionalização crítica.
4. **InternationalRigorScanner** — rigor internacional: anti-overclaim, transparência de escopo, limitações, ética, padrões de pesquisa e verificabilidade das fontes.

## Critérios de aceitação

1. Todos os 8 arquivos de agente existem em `agents/catalog/`.
2. Cada agente possui frontmatter válido com `name`, `description`, `mode: subagent`, `model` e `temperature`.
3. Cada agente declara protocolo SDD/TDD, anti-overclaim e uso dos scanners literários adequados.
4. O agente `literary-research-scholar-phd` possui protocolo explícito de busca/pesquisa literária: problema, corpus, teoria, fontes, comparação, lacunas, evidências e bibliografia.
5. `integrations.opencode_cli` regenera `opencode.json` sem erro.
6. `opencode.json` contém os 8 agentes literários.
7. Novo módulo `scanners/literary_research_scanners.py` existe.
8. O módulo exporta 4 scanners e `run_literary_research_scanner_suite`.
9. Cada scanner retorna contrato serializável com `scanner_id`, `score`, `grade`, `dimensions`, `evidence`, `warnings`, `recommendations`.
10. A suíte retorna `domain: literary_research`, `scanner_count: 4`, `international_research_rigor_score` e `overclaim_guard`.
11. Texto/ficha com bibliografia, corpus comparativo e teoria pontua mais que texto genérico.
12. Texto vazio não quebra e retorna recomendações acionáveis.
13. Os scanners de pesquisa são exportados em `scanners/__init__.py`.
14. Testes direcionados passam.
15. Doctor final permanece sem falhas críticas novas.

## Não escopo

- Não realizar busca web real neste ciclo.
- Não afirmar validação acadêmica internacional sem revisão externa.
- Não substituir crítica literária humana, peer review, pesquisa bibliográfica formal ou comparação de corpus conduzida por especialista.

## Resultado — 2026-07-27

Implementado:

- 8 agentes em `agents/catalog/`:
  - `literary-orchestrator-phd`
  - `literary-narratology-architect-phd`
  - `literary-style-voice-phd`
  - `literary-character-psychology-phd`
  - `literary-symbolic-imagery-phd`
  - `literary-ethics-trauma-phd`
  - `literary-innovation-editorial-phd`
  - `literary-research-scholar-phd`
- 4 scanners de pesquisa literária em `scanners/literary_research_scanners.py`:
  - `LiteraryBibliographyScanner`
  - `ComparativeCorpusScanner`
  - `TheoreticalFrameworkScanner`
  - `InternationalRigorScanner`
- Exportação em `scanners/__init__.py`.
- Integração no `DiagnosticPipeline` via `include_literary_research=True` e `domain="literary_research"`.
- Integração no CLI `python3 -m scanners.cli`.
- Exposição MCP futura `literary_research_scanner_suite`.
- `opencode.json` regenerado com 202 agentes.

Validações:

- `pytest -q tests/test_r268_literary_agents_research_scanners.py` → 7 passed.
- Lote combinado R267/R268/KDP/legal/scientific/super-rigor → 31 passed.
- `python3 -m integrations.opencode_cli --check` → OK: 202 agentes, 6 MCP servers, 9 comandos.
- Smoke MCP: `literary_scanner_suite` e `literary_research_scanner_suite` disponíveis; pesquisa literária retorna 4 scanners.

Observação anti-overclaim: os agentes e scanners declaram explicitamente que índices e achados não substituem crítica humana, pesquisa bibliográfica real, peer review, comparação de corpus por especialista ou validação acadêmica externa.
