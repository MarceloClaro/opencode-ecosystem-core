---
spec_id: SPEC-935-R482
title: Curadoria da paisagem de agentes — 500-AI-Agents-Projects (manifest + landscape-curator)
component: landscape (manifest + curator), agents/catalog/landscape-curator, THIRD_PARTY_NOTICES
test_file: tests/test_r482_landscape_curator.py
status: red
estoque: rc
data: 2026-09-13
---

# SPEC-935-R482 — Curadoria da paisagem de agentes externos

## Objetivo
Registrar a coleção externa `500-AI-Agents-Projects` (fork MIT de
ashishpatel26/500-AI-Agents-Projects) como **referência de paisagem**, sem
copiar código de terceiros: um manifest curado com os 20 agentes auto-contidos
(agents/), um agente `landscape-curator` que cruza cada caso de uso com o
catálogo do Core (205 agent cards) e gera relatório de paisagem auditável
JSON + Markdown.

## Não-objetivos
- Não importar código-fonte, requirements ou env-examples dos agentes externos.
- Não prometer "500 agentes integrados": o manifest curado cobre os 20
  auto-contidos; os demais casos do README são links externos (registrados como
  contexto, não como integração).
- Não alterar roteamento default do Core.
- Não alegar validação externa (gate anti-overclaim R142).

## Critérios de aceitação
- CA1: manifest carrega com 20 entradas; cada uma tem id, title, industry,
  framework, dependencies, env_required, swift, reference_url, license="MIT".
- CA2: `LandscapeCurator` cruza cada caso de uso e produz ≥1 sugestão core
  quando existe afinidade real; casos sem afinidade entram em `unmatched`
  (nunca inventados).
- CA3: relatório JSON + Markdown com contagens, roteamentos (top 3 por caso),
  licença e timestamp; sem créditos falsos.
- CA4: nenhum código externo copiado (relatório sem "import openai", sem "def "
  de funções externas); testes herméticos sem rede/credenciais.
- CA5: THIRD_PARTY_NOTICES registra a coleção (MIT); agent card
  `agents/catalog/landscape-curator.md` criado; agentes registrados no
  frontmatter padrão do Core.
- CA6: anti-overclaim; ciclo R482 registrado no EvolutionRegistry; suíte
  completa verde.

## Fonte
https://github.com/MarceloClaro/500-AI-Agents-Projects (fork do
ashishpatel26/500-AI-Agents-Projects; MIT). Referência curada em 2026-09-13.