# SPEC-048: QualitativeCoder — Análise Qualitativa em Python

## Status: DRAFT
## Autor: Marcelo Claro (Orquestrador Supremo)
## Data: 2026-06-23
## Ciclo: R27

---

## 1. Visão Geral

Módulo Python para análise qualitativa de dados acadêmicos, substituindo ferramentas proprietárias (NVivo 12, MAXQDA) com código aberto, validável e reproduzível. Integra-se ao OpenCode Ecosystem como skill, MCP server e módulo de metacognição.

## 2. Objetivos

- **O1**: Codificação automática e semi-automática de dados qualitativos (entrevistas, observações, documentos)
- **O2**: Categorização temática com algoritmos de clustering e LLM
- **O3**: Triangulação visual de métodos e fontes
- **O4**: Geração de relatórios em LaTeX/Markdown
- **O5**: Integração total com ecossistema OpenCode (agents, skills, MCPs, hooks)

## 3. Arquitetura

```
qualitative_coder/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── coder.py          # Engine principal de codificação
│   ├── categorizer.py    # Clustering e categorização temática
│   ├── triangulator.py   # Triangulação de métodos/fontes
│   └── reporter.py       # Geração de relatórios
├── algorithms/
│   ├── __init__.py
│   ├── tfidf_cluster.py  # Clustering TF-IDF + K-Means
│   ├── bert_embed.py     # Embeddings BERT para semântica
│   ├── topic_model.py    # LDA/BERTopic para tópicos
│   └── sentiment.py      # Análise de sentimento acadêmico
├── io/
│   ├── __init__.py
│   ├── tex_parser.py     # Parser de arquivos .tex
│   ├── csv_loader.py     # Carregamento de dados tabulares
│   └── json_store.py     # Persistência em JSON
├── integration/
│   ├── __init__.py
│   ├── opencode_bridge.py # Integração com OpenCode Ecosystem
│   ├── mcp_server.py     # MCP server para ferramentas
│   └── hook_manager.py   # Hooks de pré/pós-processamento
├── tests/
│   ├── __init__.py
│   ├── test_coder.py
│   ├── test_categorizer.py
│   ├── test_triangulator.py
│   ├── test_reporter.py
│   ├── test_integration.py
│   └── conftest.py
└── specs/
    └── SPEC-048.md
```

## 4. Interfaces

### 4.1 API Principal

```python
from qualitative_coder import QualitativeCoder

coder = QualitativeCoder(language="pt-br")

# Codificação
codes = coder.code(texto_entrevista, method="axial")
# -> [{"code": "resistencia_mudanca", "span": [12, 45], "confidence": 0.87}]

# Categorização
categories = coder.categorize(codes, method="thematic")
# -> [{"category": "barreiras_implementacao", "codes": [...], "frequency": 12}]

# Triangulação
triang = coder.triangulate(dados_quant, dados_qual, method="convergence")
# -> {"convergence": 0.73, "divergence": [...], "gaps": [...]}

# Relatório
report = coder.report(triang, format="latex")
# -> "latex string pronta para compilar"
```

### 4.2 MCP Server

```json
{
  "name": "qualitative-coder",
  "tools": [
    {"name": "code_text", "description": "Codifica texto qualitativo"},
    {"name": "categorize_codes", "description": "Categoriza códigos"},
    {"name": "triangulate", "description": "Triangula dados"},
    {"name": "generate_report", "description": "Gera relatório"},
    {"name": "analyze_interview", "description": "Pipeline completo de entrevista"}
  ]
}
```

## 5. Algoritmos

### 5.1 Codificação Axial
- Extração de unidades de sentido
- Identificação de códigos emergentes vs. pré-definidos
- Scores de confiança por códigos

### 5.2 Clustering Temático
- TF-IDF + K-Means (baseline)
- BERT embeddings + HDBSCAN (avançado)
- LDA/BERTopic (topic modeling)

### 5.3 Triangulação
- Convergência: overlap semântico entre métodos
- Divergência: contradições identificadas
- Gaps: lacunas de informação

## 6. Requisitos

### 6.1 Dependências
- Python >= 3.10
- scikit-learn >= 1.3
- numpy >= 1.24
- pandas >= 2.0
- sentence-transformers >= 2.2 (opcional, para BERT)
- bertopic >= 0.15 (opcional, para topic modeling)

### 6.2 Performance
- Codificação: < 100ms por documento de 1000 palavras
- Clustering: < 5s para 100 documentos
- Triangulação: < 1s para 3 métodos

## 7. TDD

### 7.1 Testes Unitários
- `test_coder.py`: 12 CTs (codificação, códigos, confiança)
- `test_categorizer.py`: 10 CTs (clustering, categorias, temas)
- `test_triangulator.py`: 8 CTs (convergência, divergência, gaps)
- `test_reporter.py`: 6 CTs (LaTeX, Markdown, JSON)
- `test_integration.py`: 5 CTs (OpenCode, MCP, hooks)

### 7.2 Critérios de Aceite
- Cobertura >= 90%
- Todos os CTs passando
- Zero dependências proprietárias
- Documentação completa com docstrings

## 8. Integração com Ecossistema

### 8.1 Skill
- `qualitative-analysis`: Pipeline completo de análise qualitativa
- Ativado por: "análise qualitativa", "codificação", "entrevista", "triangulação"

### 8.2 Hook
- `pre_analysis`: Validação de dados de entrada
- `post_analysis`: Geração automática de relatório

### 8.3 Agente
- `qualitative-analyst`: Agente especializado em análise qualitativa

## 9. Roadmap

1. **R27**: SPEC + TDD base (este documento)
2. **R28**: Implementação core + algoritmos
3. **R29**: Integração OpenCode + MCP server
4. **R30**: Otimização BERT + production ready
