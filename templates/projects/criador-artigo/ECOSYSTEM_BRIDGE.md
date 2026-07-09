---
name: criador-artigo-ecosystem-bridge
description: Bridge de integração entre Criador de Artigo v2 e o ecossistema OpenCode v4.2.1. Conecta 40 MCPs + Nexus sync barriers + Manus Evolve ao pipeline MASWOS para entregar manuscrito Qualis A1 100/100.
---

# Criador de Artigo v2 ↔ Ecossistema OpenCode v4.2.1 — Bridge de Integração

## Pipeline Otimizado com MCPs

Cada fase do MASWOS agora integrada com MCPs do ecossistema para eficiência máxima e precisão Qualis A1.

### FASE 1 — DIAGNÓSTICO (A0→A1→A40→A39→A14)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A1 (Diagnóstico) | `sequential-thinking` | Decompor escopo em passos lógicos, validar premissas |
| A39 (Multi-paradigma) | `time` | Verificar atualidade das referências, recorte temporal |
| A14 (Consistência) | `memory` | Cross-check de coerência com base de conhecimento existente |

**Sync Barrier:** SB0.1 (Context Alignment) + SB1.1 (Concept Extraction)
**Gate:** Nota ≥ 10 na rubrica antes de avançar para Fase 2

### FASE 2 — BUSCA & CURADORIA (A2→A3)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A2 (Busca/Curadoria) | `scihub` (search_scihub_by_keyword) | Busca papers reais no Sci-Hub por DOI/título |
| A2 (Busca/Curadoria) | `academic_search.py` | Busca arXiv com download automático de PDFs |
| A2 (Busca/Curadoria) | `websearch` | Ampliar escopo com DuckDuckGo para fontes complementares |
| A3 (Evidências) | `scihub` (download_scihub_pdf) | Download de PDFs para extração de citações |
| A3 (Evidências) | `pdf` | Extrair texto e metadados dos PDFs baixados |
| A3 (Evidências) | `fetch` | Acessar páginas de journals para verificar DOI/metadados |

**Sync Barrier:** SB1.5 (Relation Discovery) + SB1.9 (Law Inference)
**Gate:** Mínimo 55 referências com DOI válido + trecho original + tradução + fichamento

### FASE 3 — ESTRUTURA ARGUMENTATIVA (A4)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A4 (Estrutura) | `sequential-thinking` | Construir árvore de argumentos, identificar gaps lógicos |
| A4 (Estrutura) | `diff` | Comparar estruturas alternativas, escolher a mais robusta |

**Sync Barrier:** SB2.5 (Select Reasoning Type) + SB2.9 (Configure Parameters)
**Gate:** Mapa argumentativo completo com tese → antítese → síntese

### FASE 4 — PRODUÇÃO (A5→A11 + A44→A45)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A5 (Revisão Literatura) | `memory` | Associar conceitos novos ao grafo de conhecimento |
| A6 (Metodologia) | `code-runner` | Validar scripts Python/R de análise estatística |
| A7 (Estatística) | `code-runner` | Executar análises estatísticas em sandbox |
| A8 (Visualização) | `playwright` | Renderizar gráficos e validar layout |
| A9 (Resultados) | `sqlite` | Armazenar e consultar dados experimentais |
| A10 (Discussão) | `sequential-thinking` | Verificar coerência discussão ↔ resultados |
| A11 (Conclusão) | `sequential-thinking` | Garantir que perguntas da introdução foram respondidas |
| A44 (Correção Textual) | `eslint`-like | Verificar consistência de estilo ABNT |
| A45 (Refinamento) | `diff` | Comparar versões, rastrear melhorias incrementais |

**Sync Barrier:** SB3.10 (Match MCPs) + SB4.1 (Analyze Success Patterns)
**Gate:** Cada capítulo ≥ páginas mínimas, todas citações com DOI+Página

### FASE 4A — NÚCLEO ANALÍTICO (A17→A28)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A17 (Framework Reprodutível) | `code-runner` | Criar Dockerfile/requirements.txt |
| A18 (Engenharia Dados) | `sqlite` | Catalogar datasets com proveniência |
| A19 (Auditoria Código) | `diff` + `eslint` | Revisão de código científico |
| A20 (Estatística Avançada) | `code-runner` | Bootstrap, Bayes, meta-análise |
| A22 (ML/DL) | `code-runner` | Treinar/validar modelos |
| A27 (Computação Quântica) | `quantum/` scripts | Executar pipelines quânticos reais |
| A28 (Benchmark) | `diff` + `code-runner` | Comparar performance, ablação |

### FASE 5 — INTEGRAÇÃO EDITORIAL (A16→A12→A15)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A16 (Integração DOCX) | `pdf` | Gerar/manipular documento final |
| A12 (Auditoria ABNT) | `filesystem` | Verificar formatação, margens, fontes |
| A15 (Abstract) | `sequential-thinking` | Extrair essência em 250 palavras |

### FASE 6 — PEER REVIEW EMULADO (A31)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A31 (Blind Peer Review) | `sequential-thinking` | Simular revisor com checklist Qualis A1 |
| A31 (Blind Peer Review) | `memory` | Comparar com artigos previamente aprovados |

**Sync Barrier:** SB5.1 (Monitor Health) + L6 Feedback Points (120 pontos)

### FASE 7 — DEFESA & SLIDES (A37→A38)

| Agente | MCP Integrado | Função |
|--------|--------------|--------|
| A37 (Slides) | `playwright` | Gerar PDF de apresentação |
| A38 (Entrega Final) | `pdf` | Compilar manuscrito + slides + anexos |

### FASE 8 — EXPORTAÇÃO MULTI-FORMATO ABNT (A0→A16→A36→A38)

| Agente | MCP/Skill Integrado | Função |
|--------|---------------------|--------|
| A0 (Editor-Chefe) | `academic-export-abnt` | Orquestrar exportação nos 3 formatos |
| A16 (Integração Editorial) | `mcp-pandoc` | Converter MD → PDF via pdflatex (com `--top-level-division=chapter` para mapear capítulos ABNT) |
| A16 (Integração Editorial) | `mcp-pandoc` | Converter MD → HTML standalone |
| A36 (Exportação LaTeX/PDF) | `templates/gerar_template_abnt.py` | Gerar template ABNT DOCX via python-docx |
| A38 (Montagem Final) | `academic-ml-pipeline` | Validar 7/7 figuras, encoding, paths |

**Formatos Suportados:**
| Formato | Engine | Configuração ABNT | Estabilizações de Compilação |
|---------|--------|-------------------|-----------------------------|
| PDF (LaTeX) | pandoc + pdflatex | Times 12pt, margens 3/2cm, espaçamento 1.5, sumário | Mapeamento nativo `\chapter`, definição de `\tightlist`, `\headheight=15pt`, paginação `roman/arabic`, e tabelas de 7 colunas autoajustadas via `\scriptsize` + `\tabcolsep=3pt` local |
| DOCX | python-docx template | Margens 3/2cm, Times 12pt, 1.5 espaçamento, numeração | Formatação de tabelas e grids nativos |
| HTML | pandoc standalone | CSS ABNT embutido, figuras base64, self-contained | Estilos CSS responsivos para tabelas |

**Comando de Execução:**
```bash
python executor.py export caminho/artigo.md pdf docx html
```

**Sync Barrier:** SB7.1 (Export Validation) — validar 7/7 figuras, encoding UTF-8, paths absolutos

## Auto-Scoring Qualis A1

Antes de cada gate, o sistema executa validação automática:

```
python auto_score_qualis.py --phase 1 --output score_fase1.json
```

### Rubrica Automatizada (10 critérios, 10 pontos cada)

| # | Critério | MCP Validador | Peso |
|---|----------|--------------|------|
| 1 | Rigor acadêmico | sequential-thinking | 10 |
| 2 | Densidade de citações (≥55 refs) | scihub + academic_search | 10 |
| 3 | ABNT compliance | filesystem (verificar formatação) | 10 |
| 4 | Originalidade | diff (comparar com literatura) | 10 |
| 5 | Metodologia reprodutível | code-runner (validar scripts) | 10 |
| 6 | Análise estatística | code-runner (executar testes) | 10 |
| 7 | Coerência argumentativa | sequential-thinking | 10 |
| 8 | Qualidade visual | playwright (renderizar gráficos) | 10 |
| 9 | Internacionalização (EN abstract) | fetch (verificar journals) | 10 |
| 10 | Auto-containment (110+ páginas) | pdf (contar páginas) | 10 |

**Score total:** Soma dos 10 critérios = 100/100

## Execução Otimizada

```bash
# Pipeline completo com todos MCPs
# Fase 1: Diagnóstico
A1 diagnostica escopo via sequential-thinking
A14 valida consistência via memory

# Fase 2: Busca (paralela)
A2 busca 30+ papers via scihub + academic_search.py
A3 extrai citações via pdf + fetch
→ Min. 55 referências com DOI

# Fase 3: Estrutura
A4 constrói argumento via sequential-thinking + diff

# Fase 4: Produção (paralela por capítulo)
A5-A11 escrevem capítulos com validação MCP em cada
A44-A45 corrigem via diff iterativo

# Fase 5: Integração
A16 compila via pdf
A12 audita ABNT via filesystem

# Fase 6: Peer Review
A31 revisa às cegas com rubrica Qualis A1

# Fase 7: Entrega
A38 empacota manuscrito final

# Fase 8: Exportação Multi-Formato
A0 orquestra exportação via academic-export-abnt skill
A16 gera PDF/HTML via mcp-pandoc
A36 aplica template ABNT DOCX via python-docx
A38 valida 7/7 figuras

# Validação final
python auto_score_qualis.py --final
→ Score esperado: 100/100
```

## Integração com Nexus Sync Barriers

Cada transição de fase dispara a barrier correspondente:

```
Fase 1→2: SB0.1 + SB1.1 (Context + Concept)
Fase 2→3: SB1.5 + SB1.9 (Relation + Law)
Fase 3→4: SB2.5 + SB2.9 (Reasoning + Config)
Fase 4→5: SB3.10 + SB4.1 (MCP Match + Patterns)
Fase 5→6: SB5.1 (Monitor Health)
Fase 6→7: L6 Feedback (120 points)
Fase 7→8: SB7.1 (Export Validation)
```

## Integração com Manus Evolve

Cada ciclo completo de criação de artigo alimenta o Manus Evolve:
- Padrões de sucesso extraídos → novas skills em `evolution/`
- Erros corrigidos → refinamento de agentes
- Score 100/100 → confirmação de padrão, auto-aprovação futura
