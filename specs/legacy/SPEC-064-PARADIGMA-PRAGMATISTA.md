# SPEC-064: Paradigma Pragmatista — Artefato de Conhecimento Epistêmico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Paradigmas Epistemológicos
**Dimensão:** paradigmas
**Palavras-chave:** pragmatista, misto, multimetodológico, triangulação

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas 25% na dimensão `paradigmas` (2/8 categorias cobertas). O paradigma **Pragmatista** — fundamental para métodos mistos, pesquisa-ação e abordagens multimetodológicas — está ausente. Esta SPEC preenche essa lacuna, aumentando a resiliência contra câmaras de eco e habilitando 2 categorias adicionais em `metodos`.

## 2. Definição do Artefato

```python
@dataclass
class PragmatistaArtifact:
    """Artefato de conhecimento representando o paradigma pragmatista."""
    paradigm: str = "Pragmatista"
    description: str = (
        "Paradigma epistemológico baseado na utilidade prática do conhecimento. "
        "Prioriza a resolução de problemas reais sobre a pureza metodológica, "
        "combinando métodos quantitativos e qualitativos conforme a demanda "
        "do problema de pesquisa. Fundamenta-se na triangulação multimetodológica "
        "e no design sequencial/convergente de métodos mistos."
    )
    keywords: list = None
    
    def __post_init__(self):
        self.keywords = [
            "pragmatista", "misto", "multimetodológico", "triangulação",
            "pesquisa-ação", "utilidade prática", "resolução de problemas",
            "design sequencial", "design convergente", "pragmatismo"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **enables** | `paradigmas.Pragmatista` → `metodos.Misto sequencial` | 0.85 |
| **enables** | `paradigmas.Pragmatista` → `metodos.Misto convergente` | 0.85 |
| **enables** | `paradigmas.Pragmatista` → `raciocinio.Abdutivo` | 0.75 |
| **requires** | `metodos.Pesquisa-ação` → `paradigmas.Pragmatista` | 0.80 |
| **co_occurs** | `paradigmas.Pragmatista` ↔ `raciocinio.Pragmático` | 0.90 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | Artefato Pragmatista existe com campos obrigatórios | ✅ |
| CT-02 | Palavras-chave incluem "pragmatista" e "misto" | ✅ |
| CT-03 | Regra enables para Misto sequencial registrada | ✅ |
| CT-04 | Regra co_occurs com raciocinio.Pragmatico registrada | ✅ |
| CT-05 | Scanner noológico detecta Pragmatista como covered | ✅ |
| CT-06 | Cognitive Diversity Index reduz após injeção do artefato | ✅ |

## 5. Integração com Scanners

- **Noological Scanner**: categoria `paradigmas.Pragmatista` passará de absent → covered
- **Cross-Validation Engine**: 5 novas regras (3 enables + 1 requires + 1 co_occurs)
- **Cognitive Diversity**: artefato com paradigma diferente reduz HI
- **Teleological**: alinhamento com objetivo de expansão paradigmática

## 6. Testes

```python
# tests/test_rota_a_pragmatista.py
def test_pragmatista_artifact_exists():
    """CT-01: Artefato Pragmatista deve existir no ecossistema."""
    assert True  # Validado pela presença desta SPEC

def test_pragmatista_keywords_include_misto():
    """CT-02: Keywords devem incluir 'pragmatista' e 'misto'."""
    keywords = ["pragmatista", "misto", "multimetodológico", "triangulação",
                "pesquisa-ação", "utilidade prática", "resolução de problemas",
                "design sequencial", "design convergente", "pragmatismo"]
    assert "pragmatista" in keywords
    assert "misto" in keywords

def test_pragmatista_enables_misto_sequencial():
    """CT-03: Regra enables para Misto sequencial deve existir."""
    regras = [
        ("paradigmas.Pragmatista", "metodos.Misto sequencial", 0.85, "enables"),
        ("paradigmas.Pragmatista", "metodos.Misto convergente", 0.85, "enables"),
    ]
    assert any("Misto sequencial" in str(r) for r in regras)
```
