# SPEC-935-R412 — Expansão da pesquisa para eliminar limitações reais e relevantes

- **Ciclo**: R412
- **Data**: 2026-08-12
- **Status**: em implementação
- **Dependência**: R411 (artigo RBEP LaTeX/PDF) e R408 (auditoria de reprodutibilidade)

## Contexto

O usuário solicitou: "faltou a tabela 2 e melhore a pesquisa buscando eliminar as
limitações reais e relevantes". O bug da Tabela 2 foi corrigido no R411 (numeração
deslocada por `\caption*` + `\path`); este ciclo trata da **melhoria substantiva**
da pesquisa.

Limitações declaradas no R409/R410 e estratégia de eliminação:

| Limitação (R409) | Estratégia R412 | Status |
|---|---|---|
| (i) 7 países → poder/generalização | Ampliar painel para **≥ 20 países** com critério transparente (≥ 20 obs. não nulas de matrícula terciária e PIB per capita; exclui agregados) | **elimina** |
| (ii) cobertura parcial das variáveis educacionais | Painel maior + reporte explícito de cobertura por variável | **mitiga** |
| (iii) sem controles de qualidade educacional e instituições | Adicionar **WGI** (6 dimensões de governança do Banco Mundial) e controles estruturais (manufatura, exportação de alta tecnologia, expectativa de vida, investimento) | **elimina** |
| (iv) erros padrão sem ajuste de correlação serial | **Cluster por país** (statsmodels, `cov_type='cluster'`) + reporte de robustez | **elimina** |
| (v) caráter associativo | Mantém (inevitável em desenho observacional); reforça defasagens e limitações explícitas | declara |

## Requisitos funcionais

1. **Download auditável**: novos dados WDI (países ampliados + WGI) via API
   oficial, com cache imutável (URL, timestamp UTC, status HTTP, SHA-256) em
   `data/raw_expandido/` + `manifest_expandido.json`. Não altera os arquivos
   do R408 (`data/raw/`), preservando a auditoria histórica.
2. **Painel expandido**: `data/processed/panel_wdi_expandido_1960_2023.csv`
   com ≥ 20 países; variáveis: PIB pc, crescimento, matrícula terciária, gasto
   educacional, P&D, urbanização, WGI (média ou 6 dimensões), manufatura,
   alta tecnologia, expectativa de vida, investimento. Sem imputação.
3. **Análise expandida** (`scripts/analyze_expanded.py` → `outputs/expanded/`):
   - Correlações em níveis e primeiras diferenças (painel expandido).
   - LOOCV por país (N folds disjuntos).
   - Subperíodos (2 blocos temporais).
   - Painel com efeitos fixos de país (+ ano), defasagem de 5 anos, com
     controles WGI/estruturais, **erros padrão clusterizados por país**.
   - ML Random Forest com partição por linha vs LOOCV agrupado (resultado
     negativo reportado).
   - Proveniência numérica completa (`provenance_expanded.json`).
4. **Manuscrito atualizado**: `ARTIGO_RBEP_SUBMISSAO.md` (e LaTeX/PDF) com os
   novos números, nova seção de controles e erros robustos; anti-overclaim
   mantido; referências ABNT atualizadas.
5. **Testes**: `tests/test_r412_expansao_pesquisa.py` (RED→GREEN); testes
   R409–R411 atualizados para os novos números (mudança documentada);
   R408 permanece intacto.

## Critérios de aceitação

- Painel expandido com ≥ 20 países; LOOCV com ≥ 20 folds.
- Erros clusterizados por país presentes no painel FE.
- WGI presente como controle.
- Suíte acumulada R408–R412 verde.
- `doctor` sem falhas novas; ciclo R412 registrado; PROGRESS.md atualizado.
- PDF regenerado com numeração correta (Tabela 2 incluída).

## Entregáveis

- `scripts/download_expanded_data.py`, `scripts/analyze_expanded.py`
- `data/raw_expandido/` + `manifest_expandido.json`
- `data/processed/panel_wdi_expandido_1960_2023.csv`
- `outputs/expanded/` (tabelas + JSONs + provenance)
- `tests/test_r412_expansao_pesquisa.py`
- MD/tex/PDF atualizados do artigo RBEP

## Não escopo

- Não elimina a limitação (v) (desenho observacional) — declara com rigor.
- Não declara "Qualis A1" nem prontidão editorial.
- Não sobrescreve os dados/artefatos originais do R408 (auditoria histórica).
