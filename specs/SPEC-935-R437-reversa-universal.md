---
spec_id: SPEC-935-R437
component: reversa_universal.engine
title: Reversa Universal — Engenharia Reversa em Artigos, Repositórios, Códigos e Scanners de Gaps
version: 1.0.0
status: green
test_file: tests/test_r437_reversa_universal.py
---

# SPEC-935-R437 — Reversa Universal em Todas as Análises

## Meta
- **Ciclo**: R437
- **Antecessor**: R436 (99/9.9) — buscas/RAG/referências; agora universaliza Reversa como camada metacognitiva transversal
- **Alvo**: 9.9 (99) — Reversa aplicada a artigos, repos, códigos/scripts com metacognição, raciocínio e scanners de gaps aprimorados
- **Módulo**: `reversa_universal/engine.py` + `reversa_universal/bridge.py` + integração em `scanners/pipeline` e `marceloclaro/orchestrator`

## Diagnóstico
- Reversa existente é **pontual**: análise completa do `deepseek-harness` em `deepseek-harness/_reversa_sdd/` (13 módulos, 231 pacotes, inventory.md, modules, dependencies) via skills `.agents/skills/reversa*`, mas não é reutilizável como engine programática.
- `scanners/reversa_scanner.py` é textual (regex sobre corpus) — não analisa filesystem, AST, `package.json`/`requirements.txt`, nem gera `inventory.md`/`dependencies.md`/`data-dictionary.md`.
- Pipelines de **artigos** (`agentic_science_v2`, `academic/paper_composer`), **repositórios** (`research/hub`, `integrations/harness`), **códigos/scripts** (`rag`, `benchmarks`) e **scanners de gaps** (`diagnostic_pipeline` evolutionary/ gap) não invocam Reversa — perdem proveniência, correlações e soluções estruturais.

## Arquitetura R437

```
target_path (artigo/ repo/ script/ corpus)
        │
        ▼
ReversaUniversalEngine.analyze(path, output_root?)
  ├── Scout: inventory (métricas, linguagens, frameworks, integrações, módulos)
  ├── Archaeologist: modules (AST py, headings md, package.json), dependencies (requirements/pyproject/package.json), data-model (models.py, schemas)
  ├── Gaps: missing tests/docs, stale deps, TODO/FIXME, hardcoded secrets, correlações (módulo↔gap), soluções e inovações sugeridas
  └── Geração: inventory.md, modules.md, dependencies.md, gaps.md (opcional em output_root)
        │
        ├─► MetaBus: publish_subsystem_event("reversa_universal", "analysis.completed") + add_reflection + upsert_semantic_topic
        ├─► Reasoning: RAGEvolved/ModelRouter enriquecido com contexto estrutural
        ├─► Research/Manuscript: hub/paper_composer recebem contexto Reversa para melhorar pesquisas/manuscritos
        └─► Scanners: diagnostic_pipeline._reversa agora delega para engine quando corpus é path
```

### C1 — ReversaUniversalEngine (`reversa_universal/engine.py`)
| Método | Contrato |
|---|---|
| `analyze(path, output_root=None)` | Analisa filesystem ou corpus textual; retorna `{target, inventory, modules, dependencies, data_model, gaps, recommendations, files_written}`; se `output_root` fornecido, escreve `inventory.md` e `gaps.md` |
| `inventory(path)` | Conta arquivos, LOC por extensão, detecta linguagens, frameworks (via `package.json`/`requirements.txt`/`pyproject.toml`), integrações (db/cache), entry points |
| `modules(path)` | Agrupa por diretório raiz/pacote, extrai classes/funções via AST para `.py`, headings para `.md`, contagem de arquivos por módulo |
| `dependencies(path)` | Parse `requirements.txt`, `pyproject.toml` (`[tool.poetry.dependencies]`/`[project]`), `package.json` → lista `{name, version, source_file}` |
| `data_model(path)` | Busca `models.py`, `schema*`, `*.sql`, `data-dictionary` → lista de entidades/tabelas |
| `gaps(path, inventory, modules, dependencies)` | Detecta `missing_tests` (módulo sem `test_*.py`), `missing_docs` (sem README), `stale_deps` (sem version pin), `todo_fixme`, `hardcoded_secret`, `long_files` (>500 LOC), calcula correlações e sugere soluções/inovações |
| `enhance_reasoning(context)` | Enriquece `reasoning` com contexto estrutural (módulos + gaps) para `multi_reasoning.ensemble` |
| `enhance_research(query, analysis)` | Expande query de pesquisa com termos de módulos/gaps |
| `enhance_manuscript(sections, analysis)` | Sugere seções faltantes (ex. arquitetura, limitações) baseado em gaps |

Invariante: `analyze` nunca falha por path inexistente — retorna `error` diagnosticado; `output_root` é opcional; sem dependências externas além de `stdlib`+`tomllib` fallback.

### C2 — ReversaBridge (`reversa_universal/bridge.py`)
| Método | Contrato |
|---|---|
| `analyze_and_reflect(path, output_root)` | `engine.analyze` + `metabus.memory.add_reflection` (score por cobertura) + `upsert_semantic_topic("reversa_universal.<slug>")` + `publish_subsystem_event` |
| `enhance_gaps(diagnostic_report, analysis)` | Injeta gaps Reversa em `report["evolutionary"]["reversa_gaps"]` e `report["reversa"]` com recomendações priorizadas |
| `status()` | `{engine_available, last_analysis, metacognitive_topics}` |

### C3 — Integrações
- `scanners/reversa_scanner.py`: `ReversaScanner.scan` detecta se corpus é path existente → delega para `ReversaUniversalEngine` e combina score (max), mantendo compatibilidade textual.
- `scanners/pipeline.py`: `DiagnosticPipeline.run` inclui `reversa_universal` quando `domain="reversa"` ou `corpus` é path, mesclando `reversa_gaps` em `evolutionary`.
- `marceloclaro/orchestrator.py`: `reversa_analyze(path)`, `reversa_on_article(path)`, `reversa_on_repo(path)`, `reversa_on_scripts(pattern)`, `reversa_enhance_gaps(report, path)`, `reversa_status()` — todos lazy via bridge.

## Critérios de aceitação (teste R437)
1. AC1 — SPEC-935-R437 `green`.
2. AC2 — `engine.inventory(path)` para `rag/` retorna `languages` com `python`, `modules`≥1, `metrics.total_files`>0.
3. AC3 — `engine.modules(path)` identifica `rag/scientific.py` como módulo `rag` com classes `ScientificRAG`.
4. AC4 — `engine.dependencies(path)` parseia `requirements.txt` quando presente.
5. AC5 — `engine.gaps` detecta `todo_fixme` ou `missing_tests` em fixture sintética.
6. AC6 — `engine.analyze(path)` retorna `inventory, modules, dependencies, gaps, recommendations` e escreve `inventory.md` quando `output_root` fornecido.
7. AC7 — `bridge.analyze_and_reflect` publica reflexão no MetaBus e tópico semântico `reversa_universal.<slug>`.
8. AC8 — `bridge.enhance_gaps` injeta `reversa_gaps` em `diagnostic_report`.
9. AC9 — `scanners/reversa_scanner` com path delega para engine e retorna `score≥5` quando há código.
10. AC10 — `diagnostic_pipeline.run(corpus=path)` com path inclui `reversa` com `score` e `reversa_gaps` quando `domain="reversa"`.
11. AC11 — Orquestrador expõe `reversa_analyze`, `reversa_on_repo`, `reversa_on_scripts`, `reversa_enhance_gaps`, `reversa_status` e `enhance_reasoning/research/manuscript` via engine.
12. AC12 — `doctor` com 100 specs e `evolution` 255 ciclos.

## Não objetivos
- Não reexecuta o Reversa completo do `deepseek-harness` (artefato preservado em `_reversa_sdd/`); engine é heurística `stdlib` para uso universal.
- Não exige LLM para análise — AST + regex + `tomllib`; raciocínio LLM é opcional via `enhance_reasoning`.
- Não substitui `scanners/reversa_scanner` — estende-o.
