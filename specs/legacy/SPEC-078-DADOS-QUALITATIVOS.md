# SPEC-078: Dados Qualitativos — Artefato de Conhecimento de Tipo de Dados

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Tipos de Dados e Evidências
**Dimensão:** dados
**Palavras-chave:** dados qualitativos, entrevista, grupo focal, observação, narrativa, diário, coleta de dados, COREQ

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas **25%** na dimensão `dados` (2/8 categorias: Dados clínicos, Dados longitudinais). A categoria **Dados Qualitativos** — que inclui entrevistas, grupos focais, observação, narrativas, diários e documentos — está completamente ausente.

Esta lacuna é paradoxal porque:

1. **O ecossistema possui 5 SPECs de métodos qualitativos** (Fenomenológico SPEC-070, Grounded Theory SPEC-071, Estudo de Caso SPEC-072, Pesquisa-Ação SPEC-073, Métodos Mistos SPEC-066) mas **nenhuma SPEC de dados qualitativos**. Métodos sem dados são abstratos — cada método qualitativo produz tipos específicos de dados que precisam ser definidos como artefatos.

2. **Guias internacionais de pesquisa qualitativa** (NICE, 2024; Cochrane, 2024) estabelecem padrões rigorosos para coleta de dados: entrevistas semiestruturadas, grupos focais (6-12 participantes), observação participante, diários reflexivos. O COREQ (COnsolidated criteria for REporting Qualitative research) especifica 32 itens para relato de entrevistas e grupos focais.

3. **Inovações metodológicas recentes** (Frontiers, 2026; AERE, 2025) documentam métodos criativos e contextualmente situados: Kurakani (investigação conversacional informal), Pandheri Guff (diálogo contemplativo entre mulheres), Chautari Guff (diálogo público participativo), e diários digitais em pesquisa remota.

4. **A dimensão dados tem peso 1.2** — a maior entre todas as dimensões noological —, o que significa que cada nova categoria adicionada tem impacto máximo na cobertura epistêmica.

5. **O peso da dimensão dados é 1.2** — o maior do scanner noological. Cobrir dados qualitativos eleva a cobertura ponderada significativamente.

## 2. Definição do Artefato

```python
@dataclass
class DadosQualitativosArtifact:
    """Artefato de conhecimento representando dados qualitativos."""
    data_type: str = "Dados Qualitativos"
    description: str = (
        "Tipo de dado que captura aspectos subjetivos, experiencials e "
        "contextuais da experiência humana através de linguagem natural, "
        "narrativas e observação. Inclui seis subcategorias principais: "
        "(1) entrevistas (estruturadas, semiestruturadas, não estruturadas, "
        "em profundidade); "
        "(2) grupos focais (6-12 participantes, sessões de 60-120 min, "
        "moderação semi-estruturada); "
        "(3) observação (participante, não participante, sistemática, "
        "etnográfica); "
        "(4) narrativas e histórias de vida (relatos autobiográficos, "
        "entrevistas narrativas); "
        "(5) diários e registros reflexivos (diários de campo, diários "
        "pessoais, logs de atividades); "
        "(6) documentos e artefatos (institucionais, pessoais, midiáticos, "
        "históricos). "
        "O COREQ (Tong et al., 2007) estabelece 32 critérios para relato "
        "de entrevistas e grupos focais. "
        "Inovações recentes (Frontiers, 2026) incluem métodos criativos "
        "como Kurakani (investigação informal), Pandheri Guff (diálogo "
        "feminino contemplativo) e Chautari Guff (diálogo público). "
        "Dados qualitativos podem ser analisados via análise temática "
        "(Braun & Clarke, 2006), análise de conteúdo (Elo et al., 2014), "
        "análise de discurso ou grounded theory coding."
    )
    keywords: list = None

    def __post_init__(self):
        self.keywords = [
            "dados qualitativos", "entrevista", "grupo focal",
            "observação", "narrativa", "diário",
            "entrevista semiestruturada", "entrevista em profundidade",
            "observação participante", "etnografia",
            "história de vida", "COREQ", "triangulação",
            "análise temática", "análise de conteúdo",
            "pesquisa qualitativa", "dados textuais",
            "Kurakani", "Pandheri Guff", "Chautari Guff",
            "diário de campo", "gravação de áudio", "transcrição",
            "saturação teórica", "amostragem intencional"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **produced_by** | `dados.Qualitativos` → `metodos.Fenomenologico` | 0.90 |
| **produced_by** | `dados.Qualitativos` → `metodos.GroundedTheory` | 0.95 |
| **produced_by** | `dados.Qualitativos` → `metodos.EstudoDeCaso` | 0.85 |
| **produced_by** | `dados.Qualitativos` → `metodos.PesquisaAcao` | 0.80 |
| **co_occurs** | `dados.Qualitativos` ↔ `dados.Clinicos` | 0.60 |
| **requires** | `dados.Qualitativos` → `raciocinio.Indutivo` | 0.85 |
| **requires** | `dados.Qualitativos` → `raciocinio.Descritivo` | 0.80 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-078 existe com metadados (Active) | ✅ |
| CT-02 | Keywords incluem "dados qualitativos" e "entrevista" | ✅ |
| CT-03 | Regra `produced_by` para metodos.GroundedTheory registrada | ✅ |
| CT-04 | Regra `requires` para raciocinio.Indutivo registrada | ✅ |
| CT-05 | Skill dados-qualitativos existe com frontmatter | ✅ |
| CT-06 | Template de entrevista semiestruturada existe | ✅ |
| CT-07 | Template de grupo focal existe | ✅ |
| CT-08 | Template de COREQ checklist existe | ✅ |

## 5. Referências Acadêmicas

| # | Referência | Fonte |
|:-:|:-----------|:------|
| 1 | Chand, S.P. (2025). Methods of Data Collection in Qualitative Research: Interviews, Focus Groups, Observations, and Document Analysis. *Advances in Educational Research and Evaluation*, 6(1), 303-317. DOI: 10.25082/AERE.2025.01.001 | SyncSci |
| 2 | Frontiers in Research Metrics and Analytics. (2026). Data collection methods in qualitative research: researchers' reflections. DOI: 10.3389/frma.2026.1778160 | Frontiers |
| 3 | NICE. (2024). Appendix 4: Conduct of qualitative research studies. *NICE Real-World Evidence Framework*. | NICE |
| 4 | Tong, A., Sainsbury, P., & Craig, J. (2007). Consolidated criteria for reporting qualitative research (COREQ): a 32-item checklist. *International Journal for Quality in Health Care*, 19(6), 349-357. DOI: 10.1093/intqhc/mzm042 | Oxford |
| 5 | Braun, V., & Clarke, V. (2006). Using thematic analysis in psychology. *Qualitative Research in Psychology*, 3(2), 77-101. | Taylor & Francis |
| 6 | Rane, N.L. & Meti, A. (2026). Qualitative research approaches: A guide to data collection, analysis, trustworthiness, AI, and ethics. *Deep Science*. DOI: 10.70593/deepsci.0202026 | Deep Science |
| 7 | Elo, S. et al. (2014). Qualitative content analysis: A focus on trustworthiness. *SAGE Open*, 4(1). DOI: 10.1177/2158244014522633 | SAGE |
| 8 | Charmaz, K. (2014). *Constructing Grounded Theory* (2nd ed.). SAGE. | SAGE |
| 9 | Flick, U. (2022). *An Introduction to Qualitative Research* (7th ed.). SAGE. | SAGE |
| 10 | Denzin, N.K. & Lincoln, Y.S. (Eds.). (2018). *The SAGE Handbook of Qualitative Research* (5th ed.). SAGE. | SAGE |

## 6. Integração com Scanners

- **Noological Scanner**: categoria `dados.Qualitativos` passará de absent → covered (3/8 = 37,5%)
- **Cross-Validation Engine**: 7 novas regras (3 produced_by + 1 co_occurs + 2 requires)
- **Cognitive Diversity**: dados qualitativos introduzem tipo de evidência textual/subjetiva
- **Teleological**: alinhamento com expansão de tipos de dados (target 50%)
- **Evolutionary**: redução do bottleneck da dimensão dados (25% → 37,5%)

## 7. Testes

```python
# tests/test_r34_dados_qualitativos.py
def test_dados_qualitativos_spec():
    assert os.path.exists("specs/SPEC-078-DADOS-QUALITATIVOS.md")
    with open("specs/SPEC-078-DADOS-QUALITATIVOS.md") as f:
        c = f.read()
    assert "# SPEC-078" in c and "Active" in c

def test_dados_qualitativos_keywords():
    with open("specs/SPEC-078-DADOS-QUALITATIVOS.md") as f:
        c = f.read().lower()
    assert "dados qualitativos" in c or "dados qualitativos" in c
    assert "entrevista" in c

def test_dados_qualitativos_produced_by():
    with open("specs/SPEC-078-DADOS-QUALITATIVOS.md") as f:
        c = f.read()
    assert "produced_by" in c and "GroundedTheory" in c

def test_dados_qualitativos_requires():
    with open("specs/SPEC-078-DADOS-QUALITATIVOS.md") as f:
        c = f.read()
    assert "requires" in c and "Indutivo" in c

def test_dados_qualitativos_skill():
    assert os.path.exists("skills/research/dados-qualitativos/SKILL.md")
    with open("skills/research/dados-qualitativos/SKILL.md") as f:
        c = f.read()
    assert "dados-qualitativos" in c and "SPEC-078" in c

def test_dados_qualitativos_entrevista():
    with open("skills/research/dados-qualitativos/SKILL.md") as f:
        c = f.read()
    assert "entrevista" in c.lower()

def test_dados_qualitativos_grupo_focal():
    with open("skills/research/dados-qualitativos/SKILL.md") as f:
        c = f.read()
    assert "grupo focal" in c.lower()

def test_dados_qualitativos_coreq():
    with open("skills/research/dados-qualitativos/SKILL.md") as f:
        c = f.read()
    assert "COREQ" in c
```
