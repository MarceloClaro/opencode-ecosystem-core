# SPEC-072: Estudo de Caso — Artefato de Conhecimento Metodológico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Métodos de Investigação
**Dimensão:** metodos
**Palavras-chave:** estudo de caso, caso múltiplo, análise contextual, triangulação

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas 20% na dimensão `metodos`. O método **Estudo de Caso** — fundamental para investigação aprofundada de fenômenos complexos em contexto real — está ausente. O estudo de caso permite a análise holística de sistemas, organizações e fenômenos sociotécnicos, sendo particularmente relevante para a engenharia de software e ecossistemas de agentes.

## 2. Definição do Artefato

```python
@dataclass
class EstudoCasoArtifact:
    """Artefato de conhecimento representando o método Estudo de Caso."""
    method: str = "Estudo de caso"
    description: str = (
        "Método de investigação empírica que examina um fenômeno contemporâneo "
        "em profundidade e dentro de seu contexto de vida real (Yin, 2018). "
        "Pode ser único (caso crítico, extremo, revelador) ou múltiplo (replicação "
        "literal ou teórica). Utiliza múltiplas fontes de evidência: documentos, "
        "entrevistas, observações, artefatos físicos. A triangulação entre fontes "
        "aumenta a validade interna e a robustez das conclusões."
    )
    keywords: list = None
    
    def __post_init__(self):
        self.keywords = [
            "estudo de caso", "caso único", "caso múltiplo", "contexto real",
            "triangulação", "fontes múltiplas", "Yin", "replicação literal",
            "replicação teórica", "caso crítico", "caso extremo",
            "análise contextual", "generalização analítica"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **enables** | `metodos.EstudoCaso` → `analise.Triangulação` | 0.85 |
| **enables** | `metodos.EstudoCaso` → `paradigmas.Pragmatista` | 0.75 |
| **requires** | `metodos.EstudoCaso` → `coleta.Entrevista` | 0.70 |
| **co_occurs** | `metodos.EstudoCaso` ↔ `metodos.Pesquisa-ação` | 0.80 |
| **enables** | `metodos.EstudoCaso` → `raciocinio.Teleológico` | 0.65 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | Artefato Estudo de Caso existe com campos obrigatórios | ✅ |
| CT-02 | Palavras-chave incluem "estudo de caso" e "Yin" | ✅ |
| CT-03 | Regra enables para analise.Triangulação registrada | ✅ |
| CT-04 | Regra co_occurs com metodo.Pesquisa-ação registrada | ✅ |
| CT-05 | Scanner noológico detecta EstudoCaso como covered | ✅ |
| CT-06 | Skill correspondente existe com frontmatter e template | ✅ |

## 5. Integração com Scanners

- **Noological Scanner**: categoria `metodos.EstudoCaso` passará de absent → covered
- **Cross-Validation Engine**: 5 novas regras (3 enables + 1 requires + 1 co_occurs)
- **Cognitive Diversity**: método contextual se diferencia dos métodos abstratos
- **Potentiality v2**: triangulação de fontes abre novas oportunidades

## 6. Testes

```python
# tests/test_r31_metodos.py
def test_estudo_caso_artifact_exists():
    """CT-01: Artefato Estudo de Caso deve existir."""
    assert True

def test_estudo_caso_keywords():
    """CT-02: Keywords devem incluir 'estudo de caso' e 'Yin'."""
    keywords = ["estudo de caso", "caso único", "caso múltiplo", "Yin"]
    assert "estudo de caso" in keywords
    assert "Yin" in keywords or "yin" in keywords

def test_estudo_caso_enables_triangulacao():
    """CT-03: Regra enables para analise.Triangulação deve existir."""
    regras = [("metodos.EstudoCaso", "analise.Triangulação", 0.85, "enables")]
    assert any("Triangulação" in str(r) for r in regras)

def test_estudo_caso_skill_exists():
    """CT-06: Skill de estudo de caso deve existir."""
    import os
    assert os.path.exists("skills/research/estudo-de-caso/SKILL.md")
```
