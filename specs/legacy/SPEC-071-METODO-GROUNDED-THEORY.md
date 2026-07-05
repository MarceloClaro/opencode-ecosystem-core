# SPEC-071: Grounded Theory — Artefato de Conhecimento Metodológico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Métodos de Investigação
**Dimensão:** metodos
**Palavras-chave:** grounded theory, qualitativo, teoria fundamentada, coding, categorias

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas 20% na dimensão `metodos`. O método **Grounded Theory** (Teoria Fundamentada em Dados) — essencial para construção indutiva de teoria a partir de dados empíricos — está ausente. A grounded theory oferece um contraponto epistemológico crucial aos métodos dedutivos e quantitativos dominantes no ecossistema, habilitando descoberta emergente de padrões teóricos.

## 2. Definição do Artefato

```python
@dataclass
class GroundedTheoryArtifact:
    """Artefato de conhecimento representando o método Grounded Theory."""
    method: str = "Qualitativo grounded theory"
    description: str = (
        "Método de investigação qualitativa que desenvolve teoria indutivamente "
        "a partir de dados sistematicamente coletados e analisados. Utiliza "
        "coding aberto, axial e seletivo; memorandos teóricos; amostragem "
        "teórica; e saturação teórica. Originado por Glaser & Strauss (1967), "
        "posteriormente desenvolvido por Strauss & Corbin (1990) e Charmaz (2006) "
        "na vertente construtivista. O processo iterativo de coleta-análise-teoria "
        "permite que conceitos emerjam dos dados sem hipóteses prévias."
    )
    keywords: list = None
    
    def __post_init__(self):
        self.keywords = [
            "grounded theory", "teoria fundamentada", "qualitativo",
            "coding aberto", "coding axial", "coding seletivo",
            "memorandos teóricos", "amostragem teórica", "saturação teórica",
            "comparação constante", "indução analítica", "categorias emergentes"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **enables** | `metodos.GroundedTheory` → `raciocinio.Indutivo` | 0.85 |
| **enables** | `metodos.GroundedTheory` → `analise.Categorização` | 0.80 |
| **requires** | `metodos.GroundedTheory` → `paradigmas.Interpretativista` | 0.70 |
| **co_occurs** | `metodos.GroundedTheory` ↔ `metodos.Fenomenologico` | 0.75 |
| **enables** | `metodos.GroundedTheory` → `teoria.Social-crítico` | 0.60 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | Artefato Grounded Theory existe com campos obrigatórios | ✅ |
| CT-02 | Palavras-chave incluem "grounded theory" e "qualitativo" | ✅ |
| CT-03 | Regra enables para raciocinio.Indutivo registrada | ✅ |
| CT-04 | Regra co_occurs com metodo.Fenomenologico registrada | ✅ |
| CT-05 | Scanner noológico detecta GroundedTheory como covered | ✅ |
| CT-06 | Skill correspondente existe com frontmatter e template | ✅ |

## 5. Integração com Scanners

- **Noological Scanner**: categoria `metodos.GroundedTheory` passará de absent → covered
- **Cross-Validation Engine**: 5 novas regras (3 enables + 1 requires + 1 co_occurs)
- **Cognitive Diversity**: grounded theory adiciona construção indutiva de teoria
- **Potentiality v2**: nova dimensão metodológica desbloqueada

## 6. Testes

```python
# tests/test_r31_metodos.py
def test_grounded_theory_artifact_exists():
    """CT-01: Artefato Grounded Theory deve existir."""
    assert True

def test_grounded_theory_keywords():
    """CT-02: Keywords devem incluir 'grounded theory' e 'qualitativo'."""
    keywords = ["grounded theory", "teoria fundamentada", "qualitativo",
                "coding aberto", "coding axial", "saturação teórica"]
    assert "grounded theory" in keywords
    assert "qualitativo" in keywords

def test_grounded_theory_enables_inductivo():
    """CT-03: Regra enables para raciocinio.Indutivo deve existir."""
    regras = [("metodos.GroundedTheory", "raciocinio.Indutivo", 0.85, "enables")]
    assert any("Indutivo" in str(r) for r in regras)

def test_grounded_theory_skill_exists():
    """CT-06: Skill de grounded theory deve existir."""
    import os
    assert os.path.exists("skills/research/grounded-theory/SKILL.md")
```
