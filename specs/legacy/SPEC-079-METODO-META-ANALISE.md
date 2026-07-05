# SPEC-079: Método Meta-análise — Artefato de Conhecimento Metodológico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Métodos de Investigação
**Dimensão:** metodos
**Palavras-chave:** meta-análise, síntese quantitativa, effect size, forest plot, funnel plot, heterogeneidade, I², PRISMA

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de **20%** na dimensão `metodos` (2/10 categorias: Quantitativo experimental, Quantitativo correlacional). A **Meta-análise** — método de síntese quantitativa que combina estatisticamente resultados de múltiplos estudos — está completamente ausente.

Esta lacuna é crítica porque:

1. **A meta-análise é o complemento natural da Revisão Sistemática (SPEC-065).** Sem meta-análise, a revisão sistemática produz apenas síntese narrativa. A meta-análise adiciona: pooled effect size, intervalos de confiança, testes de heterogeneidade (I², Q de Cochrane), análise de viés de publicação (funnel plot, Egger test), meta-regressão e análise de subgrupos.

2. **Guias internacionais** (Cochrane Handbook, Cap. 10; PRISMA 2020; FRAMES — PeerJ, 2026) estabelecem protocolos rigorosos: modelos de efeito fixo (Mantel-Haenszel, Peto, inverse variance) e efeito aleatório (DerSimonian-Laird, REML), medidas de heterogeneidade, análise de sensibilidade e publicação bias.

3. **Avanços metodológicos recentes** (Open Public Health Journal, 2026) documentam extensões da meta-análise para desfechos complexos (time-to-event, dados multinível), e o FRAMES (Dwivedi, 2026) consolida checklists baseados em evidências para planejamento e execução.

4. **O peso da dimensão métodos é 1.1** — cada novo método adicionado tem alto impacto na cobertura epistêmica ponderada.

5. **A meta-análise conecta dimensões**: dados quantitativos (dados.clínicos), revisão sistemática (métodos.revisão), tipos de raciocínio (dedutivo, probabilístico) e população (cross-cultural, clínica).

## 2. Definição do Artefato

```python
@dataclass
class MetaAnaliseMethodArtifact:
    """Artefato de conhecimento representando o método de meta-análise."""
    method: str = "Meta-análise"
    description: str = (
        "Método de síntese quantitativa que combina estatisticamente "
        "resultados de dois ou mais estudos independentes para produzir "
        "um efeito sumário (pooled effect size) com maior poder estatístico "
        "e precisão. Divide-se em três etapas principais: "
        "(1) planejamento: definição do efeito (OR, RR, MD, SMD, HR), "
        "escolha do modelo (efeito fixo: Mantel-Haenszel, Peto, inverse "
        "variance; efeito aleatório: DerSimonian-Laird, REML); "
        "(2) execução: cálculo do pooled effect, heterogeneidade (I², "
        "Q de Cochrane, τ²), intervalos de confiança, forest plot; "
        "(3) diagnóstico: análise de viés de publicação (funnel plot, "
        "Egger test, Begg rank test, Trim and Fill), meta-regressão, "
        "análise de subgrupos, análise de sensibilidade. "
        "Protocolos: Cochrane Handbook (Cap. 10), PRISMA 2020, "
        "MOOSE, FRAMES (Dwivedi, PeerJ, 2026). "
        "Aplicações em ciência da computação: meta-análise de desempenho "
        "de algoritmos, comparação de modelos de ML, síntese de "
        "experimentos em interação humano-computador."
    )
    keywords: list = None

    def __post_init__(self):
        self.keywords = [
            "meta-análise", "síntese quantitativa", "effect size",
            "forest plot", "funnel plot", "heterogeneidade", "I²",
            "Q de Cochrane", "τ²", "efeito fixo", "efeito aleatório",
            "Mantel-Haenszel", "Peto", "inverse variance",
            "DerSimonian-Laird", "REML", "pooled effect",
            "viés de publicação", "Egger test", "Begg test",
            "Trim and Fill", "meta-regressão", "subgrupo",
            "PRISMA", "MOOSE", "Cochrane", "FRAMES",
            "odds ratio", "risk ratio", "risk difference",
            "SMD", "Hedges' g", "Cohen's d"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **requires** | `metodos.MetaAnalise` → `metodos.RevisaoSistematica` | 0.95 |
| **requires** | `metodos.MetaAnalise` → `dados.Clinicos` | 0.85 |
| **requires** | `metodos.MetaAnalise` → `raciocinio.Dedutivo` | 0.80 |
| **requires** | `metodos.MetaAnalise` → `raciocinio.Probabilistico` | 0.90 |
| **enables** | `metodos.MetaAnalise` → `dados.Longitudinais` | 0.70 |
| **synergizes** | `metodos.MetaAnalise` ↔ `metodos.QuantitativoExperimental` | 0.85 |
| **synergizes** | `metodos.MetaAnalise` ↔ `metodos.QuantitativoCorrelacional` | 0.80 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-079 existe com metadados (Active) | ✅ |
| CT-02 | Keywords incluem "meta-análise" e "effect size" | ✅ |
| CT-03 | Regra `requires` para metodos.RevisaoSistematica registrada | ✅ |
| CT-04 | Regra `requires` para raciocinio.Probabilistico registrada | ✅ |
| CT-05 | Skill meta-analise existe com frontmatter | ✅ |
| CT-06 | Template de forest plot existe | ✅ |
| CT-07 | Template de heterogeneidade (I²) existe | ✅ |
| CT-08 | Template de viés de publicação (funnel plot) existe | ✅ |

## 5. Referências Acadêmicas

| # | Referência | Fonte |
|:-:|:-----------|:------|
| 1 | Cochrane Collaboration. (2024). Chapter 10: Analysing data and undertaking meta-analyses. In *Cochrane Handbook for Systematic Reviews of Interventions* (v6.5). | Cochrane |
| 2 | Dwivedi, A. (2026). Step-by-step guide and checklists for selecting and conducting an evidence synthesis study using FRAMES. *PeerJ*, 14, e20897. DOI: 10.7717/peerj.20897 | PeerJ |
| 3 | Page, M.J. et al. (2021). The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ*, 372, n71. DOI: 10.1136/bmj.n71 | BMJ |
| 4 | DerSimonian, R. & Laird, N. (1986). Meta-analysis in clinical trials. *Controlled Clinical Trials*, 7(3), 177-188. DOI: 10.1016/0197-2456(86)90046-2 | Elsevier |
| 5 | Higgins, J.P.T. et al. (2003). Measuring inconsistency in meta-analyses. *BMJ*, 327(7414), 557-560. DOI: 10.1136/bmj.327.7414.557 | BMJ |
| 6 | Egger, M. et al. (1997). Bias in meta-analysis detected by a simple, graphical test. *BMJ*, 315(7109), 629-634. DOI: 10.1136/bmj.315.7109.629 | BMJ |
| 7 | Viechtbauer, W. (2010). Conducting meta-analyses in R with the metafor package. *Journal of Statistical Software*, 36(3), 1-48. DOI: 10.18637/jss.v036.i03 | JSS |
| 8 | Borenstein, M. et al. (2021). *Introduction to Meta-Analysis* (2nd ed.). Wiley. | Wiley |
| 9 | Open Public Health Journal. (2026). Synthesis Methods for Meta-Analysis: A Scoping Review. DOI: 10.2174/0118749445457182260412055033 | Bentham |
| 10 | Muka, T. et al. (2020). A 24-step guide on how to design, conduct, and successfully publish a systematic review and meta-analysis in medical research. *European Journal of Epidemiology*, 35, 49-60. DOI: 10.1007/s10654-019-00576-5 | Springer |

## 6. Integração com Scanners

- **Noological Scanner**: categoria `metodos.MetaAnalise` passará de absent → covered (3/10 = 30%)
- **Cross-Validation Engine**: 7 novas regras (3 requires + 1 enables + 2 synergizes)
- **Cognitive Diversity**: meta-análise introduz método quantitativo de síntese
- **Teleological**: alinhamento com expansão de métodos (target 50%)
- **Evolutionary**: redução do bottleneck da dimensão métodos (20% → 30%)

## 7. Testes

```python
# tests/test_r34_meta_analise.py
def test_meta_analise_spec():
    assert os.path.exists("specs/SPEC-079-METODO-META-ANALISE.md")
    with open("specs/SPEC-079-METODO-META-ANALISE.md") as f:
        c = f.read()
    assert "# SPEC-079" in c and "Active" in c

def test_meta_analise_keywords():
    with open("specs/SPEC-079-METODO-META-ANALISE.md") as f:
        c = f.read().lower()
    assert "meta-análise" in c or "meta-analise" in c
    assert "effect size" in c

def test_meta_analise_requires_revisao():
    with open("specs/SPEC-079-METODO-META-ANALISE.md") as f:
        c = f.read()
    assert "requires" in c and "RevisaoSistematica" in c

def test_meta_analise_requires_probabilistico():
    with open("specs/SPEC-079-METODO-META-ANALISE.md") as f:
        c = f.read()
    assert "requires" in c and "Probabilistico" in c

def test_meta_analise_skill():
    assert os.path.exists("skills/research/meta-analise/SKILL.md")
    with open("skills/research/meta-analise/SKILL.md") as f:
        c = f.read()
    assert "meta-analise" in c and "SPEC-079" in c

def test_meta_analise_forest_plot():
    with open("skills/research/meta-analise/SKILL.md") as f:
        c = f.read()
    assert "forest plot" in c.lower()

def test_meta_analise_heterogeneidade():
    with open("skills/research/meta-analise/SKILL.md") as f:
        c = f.read()
    assert "I²" in c or "heterogeneidade" in c.lower()

def test_meta_analise_publication_bias():
    with open("skills/research/meta-analise/SKILL.md") as f:
        c = f.read()
    assert "viés" in c.lower() or "funnel" in c.lower() or "Egger" in c
```
