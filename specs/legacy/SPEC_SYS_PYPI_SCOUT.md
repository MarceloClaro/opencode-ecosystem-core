# SPEC-SYS-PYPI_SCOUT: pypi-scout
Version: 1.0.0 | Domain: system

## Objective
Buscador inteligente de bibliotecas Python para o ecossistema OpenCode. Busca, cataloga e instala bibliotecas do PyPI com curadoria de 24+ bibliotecas em 5 categorias e metricas de afinidade. Integra-se com SEEKER, MASWOS e PhD Auditor.

## Acceptance Criteria
- [x] CT-1: SKILL.md exists with valid frontmatter (name, description, version, category, tags, status)
- [x] CT-2: category declared as "system"
- [x] CT-3: version field present ("1.0.0")
- [x] CT-4: description references CLI tool (pypi_scout.py), 5 curated categories (artigos_academicos, dados_mundiais, mcp_ecosystem, dados_cientificos, infra_ferramentas), and component affinity mapping (SEEKER, MASWOS, PhD Auditor, MCP Server, Data Analysis)
