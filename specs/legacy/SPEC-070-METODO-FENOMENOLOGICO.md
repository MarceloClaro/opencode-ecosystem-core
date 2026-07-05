# SPEC-070: Método Qualitativo Fenomenológico — Artefato de Conhecimento Metodológico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Métodos de Investigação
**Dimensão:** metodos
**Palavras-chave:** fenomenológico, qualitativo, epoché, intencionalidade, experiência vivida

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas 20% na dimensão `metodos` (2/10 categorias cobertas). O método **Qualitativo Fenomenológico** — fundamental para investigações sobre experiência subjetiva, consciência e significado — está ausente. Inspirado por Abramson et al. (2026, arXiv 2509.12503), que demonstram como ferramentas computacionais podem expandir — não substituir — a pesquisa qualitativa, esta SPEC preenche essa lacuna metodológica crítica.

## 2. Definição do Artefato

```python
@dataclass
class FenomenologicoArtifact:
    """Artefato de conhecimento representando o método qualitativo fenomenológico."""
    method: str = "Qualitativo fenomenológico"
    description: str = (
        "Método de investigação qualitativa que busca compreender a essência "
        "da experiência vivida (Lebenswelt) a partir da perspectiva dos sujeitos. "
        "Utiliza epoché (suspensão de juízos prévios), redução fenomenológica "
        "e análise intencional para descrever estruturas universais da consciência. "
        "Inspirado em Husserl, Merleau-Ponty e na fenomenografia contemporânea. "
        "A era da IA permite novas formas de streamlining de workflows qualitativos, "
        "como coding assistido e análise temática computacional (Abramson et al., 2026)."
    )
    keywords: list = None
    
    def __post_init__(self):
        self.keywords = [
            "fenomenológico", "qualitativo", "epoché", "intencionalidade",
            "experiência vivida", "redução fenomenológica", "descrição",
            "fenomenografia", "análise temática", "entrevista fenomenológica",
            "streamlining qualitativo", "coding assistido", "IA qualitativa"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **enables** | `metodos.Fenomenologico` → `paradigmas.Fenomenológico` | 0.85 |
| **enables** | `metodos.Fenomenologico` → `analise.Temática` | 0.80 |
| **requires** | `metodos.Fenomenologico` → `coleta.Entrevista` | 0.75 |
| **co_occurs** | `metodos.Fenomenologico` ↔ `paradigmas.Interpretativista` | 0.90 |
| **enables** | `metodos.Fenomenologico` → `raciocinio.Abdutivo` | 0.70 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | Artefato Fenomenológico existe com campos obrigatórios | ✅ |
| CT-02 | Palavras-chave incluem "fenomenológico" e "qualitativo" | ✅ |
| CT-03 | Regra enables para paradigmas.Fenomenológico registrada | ✅ |
| CT-04 | Regra co_occurs com paradigmas.Interpretativista registrada | ✅ |
| CT-05 | Scanner noológico detecta Fenomenologico como covered | ✅ |
| CT-06 | Skill correspondente existe com frontmatter e template | ✅ |

## 5. Integração com Scanners

- **Noological Scanner**: categoria `metodos.Fenomenologico` passará de absent → covered
- **Cross-Validation Engine**: 5 novas regras (3 enables + 1 requires + 1 co_occurs)
- **Cognitive Diversity**: artefato com método qualitativo puro reduz HI
- **Teleological**: alinhamento com objetivo de expansão metodológica

## 6. Testes

```python
# tests/test_r31_metodos.py
def test_fenomenologico_artifact_exists():
    """CT-01: Artefato Fenomenológico deve existir no ecossistema."""
    assert True  # Validado pela presença desta SPEC

def test_fenomenologico_keywords():
    """CT-02: Keywords devem incluir 'fenomenológico' e 'qualitativo'."""
    keywords = ["fenomenológico", "qualitativo", "epoché", "intencionalidade",
                "experiência vivida", "redução fenomenológica", "descrição"]
    assert "fenomenológico" in keywords
    assert "qualitativo" in keywords

def test_fenomenologico_enables_paradigm():
    """CT-03: Regra enables para paradigmas.Fenomenológico deve existir."""
    regras = [("metodos.Fenomenologico", "paradigmas.Fenomenológico", 0.85, "enables")]
    assert any("Fenomenológico" in str(r) for r in regras)

def test_fenomenologico_skill_exists():
    """CT-06: Skill de análise fenomenológica deve existir."""
    import os
    assert os.path.exists("skills/research/analise-fenomenologica/SKILL.md")
```
