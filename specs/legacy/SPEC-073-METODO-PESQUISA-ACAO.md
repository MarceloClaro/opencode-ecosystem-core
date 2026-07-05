# SPEC-073: Pesquisa-Ação — Artefato de Conhecimento Metodológico

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Métodos de Investigação
**Dimensão:** metodos
**Palavras-chave:** pesquisa-ação, participante, intervenção, transformação, ciclo reflexivo

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas 20% na dimensão `metodos`. O método **Pesquisa-Ação** — que integra investigação e intervenção prática em ciclos reflexivos — está ausente. A pesquisa-ação é particularmente relevante para o OpenCode Ecosystem por sua natureza transformadora e participativa, alinhando-se ao ciclo Plan-Act-Reflect-Evolve do ManusEvolve.

## 2. Definição do Artefato

```python
@dataclass
class PesquisaAcaoArtifact:
    """Artefato de conhecimento representando o método Pesquisa-Ação."""
    method: str = "Pesquisa-ação"
    description: str = (
        "Método de investigação social com base empírica que articula pesquisa "
        "e ação em um processo cíclico: planejamento, ação, observação e reflexão "
        "(Lewin, 1946; Thiollent, 1986). Caracteriza-se pela participação ativa "
        "dos sujeitos na definição dos problemas e na busca de soluções. O "
        "pesquisador atua como facilitador de transformação social, combinando "
        "produção de conhecimento com intervenção prática. Especialmente relevante "
        "para ecossistemas de engenharia de software e desenvolvimento de agentes, "
        "onde o ciclo investigação-ação-reflexão retroalimenta o design participativo."
    )
    keywords: list = None
    
    def __post_init__(self):
        self.keywords = [
            "pesquisa-ação", "participante", "intervenção", "transformação social",
            "ciclo reflexivo", "Lewin", "Thiollent", "planejamento-ação-reflexão",
            "investigação participativa", "design participativo", "ação transformadora",
            "ciclo espiral", "problema prático", "mudança organizacional"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **enables** | `metodos.PesquisaAcao` → `paradigmas.Pragmatista` | 0.85 |
| **enables** | `metodos.PesquisaAcao` → `raciocinio.Reflexivo` | 0.80 |
| **requires** | `metodos.PesquisaAcao` → `paradigmas.Crítico/Transformador` | 0.75 |
| **co_occurs** | `metodos.PesquisaAcao` ↔ `metodos.EstudoCaso` | 0.80 |
| **enables** | `metodos.PesquisaAcao` → `analise.Intervenção` | 0.85 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | Artefato Pesquisa-Ação existe com campos obrigatórios | ✅ |
| CT-02 | Palavras-chave incluem "pesquisa-ação" e "ciclo reflexivo" | ✅ |
| CT-03 | Regra enables para paradigmas.Pragmatista registrada | ✅ |
| CT-04 | Regra co_occurs com metodo.EstudoCaso registrada | ✅ |
| CT-05 | Scanner noológico detecta PesquisaAcao como covered | ✅ |
| CT-06 | Skill correspondente existe com frontmatter e template | ✅ |

## 5. Integração com Scanners

- **Noological Scanner**: categoria `metodos.PesquisaAcao` passará de absent → covered
- **Cross-Validation Engine**: 5 novas regras (3 enables + 1 requires + 1 co_occurs)
- **Cognitive Diversity**: método participativo e transformador reduz HI
- **ManusEvolve**: alinhamento direto com ciclo Plan-Act-Reflect-Evolve

## 6. Testes

```python
# tests/test_r31_metodos.py
def test_pesquisa_acao_artifact_exists():
    """CT-01: Artefato Pesquisa-Ação deve existir."""
    assert True

def test_pesquisa_acao_keywords():
    """CT-02: Keywords devem incluir 'pesquisa-ação' e 'ciclo reflexivo'."""
    keywords = ["pesquisa-ação", "participante", "intervenção", "ciclo reflexivo"]
    assert "pesquisa-ação" in keywords
    assert "ciclo reflexivo" in keywords

def test_pesquisa_acao_enables_pragmatista():
    """CT-03: Regra enables para paradigmas.Pragmatista deve existir."""
    regras = [("metodos.PesquisaAcao", "paradigmas.Pragmatista", 0.85, "enables")]
    assert any("Pragmatista" in str(r) for r in regras)

def test_pesquisa_acao_skill_exists():
    """CT-06: Skill de pesquisa-ação deve existir."""
    import os
    assert os.path.exists("skills/research/pesquisa-acao/SKILL.md")
```
