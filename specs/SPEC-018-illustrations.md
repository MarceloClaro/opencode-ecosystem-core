# SPEC-018 — Subsistema de Ilustrações Científicas e Extração de Figuras Reais

```yaml
spec_id: SPEC-018
title: Ilustrações Científicas (Mermaid + Graphify + MIRA) e FigureHunter
status: ACTIVE
version: 1.0.0
depends_on: [SPEC-016, SPEC-017]
inspirations:
  - MarceloClaro/graphify (grafo de conhecimento do projeto)
  - sandeco/mira-animator (metáforas animadas, Regra Zero)
  - Mermaid (diagramas como código)
modules:
  - illustrations/mermaid_engine.py
  - illustrations/graphify_engine.py
  - illustrations/mira_engine.py
  - research/figure_hunter.py
```

## 1. Requisitos

| ID | Requisito |
|---|---|
| REQ-018.1 | O `MermaidEngine` DEVE gerar diagramas (flowchart, sequence, mindmap) a partir de estruturas de dados e sempre preservar o arquivo `.mmd`, renderizando PNG/SVG quando um renderizador (`manus-render-diagram`/`mmdc`) estiver disponível. |
| REQ-018.2 | O `GraphifyEngine` DEVE construir um grafo de conhecimento do manuscrito/fichamentos usando somente stdlib e exportar `graph.json`, `graph.html` (interativo) e `GRAPH_REPORT.md`. |
| REQ-018.3 | O `MiraEngine` DEVE gerar cards HTML animados aplicando o método da metáfora (dinâmica → sistema do cotidiano → mapeamento 1-para-1 → loop). |
| REQ-018.4 | O `FigureHunter` DEVE extrair figuras reais dos PDFs de `pesquisa/pdfs/` para `pesquisa/imagens/`, com legenda capturada quando possível. |
| REQ-018.5 | Cada figura extraída DEVE ser catalogada em `FONTES.md` com a referência da fonte em ABNT NBR 6023:2018 e APA 7ª ed., além de bloco LaTeX pronto com "Fonte:" na `\caption`. |
| REQ-018.6 | O orquestrador DEVE expor `illustrate()`, `knowledge_graph()` e `hunt_figures()`, registrando reflexões na memória metacognitiva. |
| REQ-018.7 | O pipeline `ResearchHub.run()` DEVE executar a extração de figuras automaticamente após o download dos PDFs, propagando os metadados (autores, ano, título, DOI) de cada `PaperRecord`. |

## 2. Invariantes (contratos)

| ID | Invariante |
|---|---|
| INV-018.1 | Regra Zero (MIRA): toda animação gerada usa loop CSS `infinite`; nenhum card é estático. |
| INV-018.2 | Títulos de cards MIRA têm no máximo 6 palavras. |
| INV-018.3 | Labels de arestas Mermaid não contêm parênteses (previne erro de parse `SQE/PS`). |
| INV-018.4 | Figuras menores que 220×160 px ou 12 KB são descartadas (anti-ícone/logo). |
| INV-018.5 | Nenhuma figura extraída é catalogada sem referência de fonte (ABNT + APA), ainda que com autor desconhecido explicitado. |
| INV-018.6 | O `.mmd` fonte é sempre preservado, mesmo quando a renderização PNG falha. |

## 3. Critérios de aceitação

1. `MermaidEngine.flowchart(...)` + `render(...)` produz `.mmd` e, com renderizador presente, `.png`.
2. `GraphifyEngine.build({...})` retorna grafo com nós ordenados por frequência e arestas com coocorrência ≥ 2; `export(...)` cria os três artefatos.
3. `MiraEngine.card(...)` escolhe a metáfora certa por keywords (pipeline→esteira, orquestração→maestro, contexto→mesa, débito→torre).
4. `FigureHunter.harvest_production(...)` em uma produção com PDFs reais extrai ≥ 1 figura e gera `FONTES.md` + `figuras.json`.
5. `ResearchHub.run(...)` reporta `figuras_extraidas` no manifest.
