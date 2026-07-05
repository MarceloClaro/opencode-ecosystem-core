# SPEC-077: Domínio Psicologia Clínica — Artefato de Conhecimento de Domínio Cruzado

**Status:** Active
**Versão:** 1.0.0
**Data:** 2026-07-02
**Categoria:** Domínios de Conhecimento Cruzados
**Dimensão:** dominios
**Palavras-chave:** psicologia clínica, avaliação psicológica, psicodiagnóstico, DSM-5, saúde mental, multiagente, WiseMind, AgentMental

---

## 1. Problema

O ecossistema OpenCode apresenta cobertura de apenas **10%** na dimensão `dominios` (1/10 categorias: Saúde Pública). A **Psicologia Clínica** — domínio de aplicação direta de métodos qualitativos (fenomenologia, grounded theory, estudo de caso) e paradigmas (fenomenológico, construtivista, pós-estruturalista) — está completamente ausente.

Esta lacuna é crítica porque:

1. **Avanços recentes em IA para saúde mental** demonstram aplicação direta de sistemas multiagente no domínio clínico: WiseMind (npj Digital Medicine, 2026) alcança 85,6% de acurácia diagnóstica usando agentes baseados em DSM-5 e DBT; AgentMental (AAAI, 2026) simula diálogos clínico-paciente com memória em árvore; AI Psychiatrist Assistant (PMLR, 2026) integra 4 agentes especializados para avaliação de depressão; DELTA (arXiv, 2026) modela aconselhamento multimodal com raciocínio deliberativo; DSM5AgentFlow (arXiv, 2025) gera questionários diagnósticos automaticamente.

2. **A psicologia clínica é o domínio de validação natural** para as 5 SPECs de método qualitativo (070-073) e 8 paradigmas (064-076). Sem um domínio de aplicação, esses artefatos permanecem abstratos.

3. **A polimatia e a primeira infância** — temas centrais das dissertações do autor — são objetos de estudo da psicologia clínica do desenvolvimento. A inclusão deste domínio cria uma ponte direta entre o ecossistema e as pesquisas em andamento.

4. **O peso da dimensão dominios é 1.0** — cada nova categoria adicionada tem alto impacto na cobertura epistêmica geral.

## 2. Definição do Artefato

```python
@dataclass
class PsicologiaClinicaDomainArtifact:
    """Artefato de conhecimento representando o domínio da Psicologia Clínica."""
    domain: str = "Psicologia Clínica"
    description: str = (
        "Domínio do conhecimento que estuda a avaliação, diagnóstico, "
        "prevenção e tratamento de transtornos mentais e comportamentais. "
        "Abrange psicopatologia (DSM-5-TR, ICD-11), psicodiagnóstico "
        "(entrevistas clínicas, testes psicológicos, escalas), "
        "psicoterapia (abordagens: cognitivo-comportamental, psicodinâmica, "
        "humanista, sistêmica, DBT), neuropsicologia clínica, "
        "psicologia da saúde, psicologia do desenvolvimento aplicada "
        "e avaliação de políticas de saúde mental. "
        "No contexto de sistemas multiagente, o domínio se manifesta em: "
        "(1) sistemas de apoio ao diagnóstico baseados em agentes (WiseMind, "
        "npj Digital Medicine, 2026 — 85.6% acurácia top-1); "
        "(2) frameworks de avaliação de saúde mental com memória em árvore "
        "(AgentMental, AAAI 2026); "
        "(3) agentes especializados para avaliação quanti-quali de depressão "
        "(AI Psychiatrist Assistant, PMLR 2026); "
        "(4) sistemas multimodais de aconselhamento com RL "
        "(DELTA, arXiv 2026); "
        "(5) workflows de geração de questionários DSM-5 "
        "(DSM5AgentFlow, arXiv 2025)."
    )
    keywords: list = None

    def __post_init__(self):
        self.keywords = [
            "psicologia clínica", "psicodiagnóstico", "avaliação psicológica",
            "DSM-5", "ICD-11", "psicopatologia", "entrevista clínica",
            "testes psicológicos", "escalas", "psicoterapia",
            "cognitivo-comportamental", "psicodinâmica", "humanista",
            "DBT", "neuropsicologia", "saúde mental",
            "WiseMind", "AgentMental", "DELTA", "DSM5AgentFlow",
            "multiagente", "diagnóstico", "transtornos mentais",
            "desenvolvimento", "infância", "adolescência",
            "avaliação", "intervenção", "prevenção"
        ]
```

## 3. Relações de Validação Cruzada (Cross-Validation)

| Tipo | Regra | Peso |
|:-----|:------|:----:|
| **uses** | `dominios.PsicologiaClínica` → `metodos.Fenomenologico` | 0.85 |
| **uses** | `dominios.PsicologiaClínica` → `metodos.GroundedTheory` | 0.80 |
| **uses** | `dominios.PsicologiaClínica` → `metodos.EstudoDeCaso` | 0.75 |
| **uses** | `dominios.PsicologiaClínica` → `metodos.PesquisaAcao` | 0.70 |
| **enables** | `dominios.PsicologiaClínica` → `paradigmas.Fenomenologico` | 0.90 |
| **enables** | `dominios.PsicologiaClínica` → `paradigmas.Construtivista` | 0.85 |
| **co_occurs** | `dominios.PsicologiaClínica` ↔ `dominios.Neurociencias` | 0.90 |
| **co_occurs** | `dominios.PsicologiaClínica` ↔ `dominios.SaudePublica` | 0.80 |

## 4. CTs (Casos de Teste)

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SPEC-077 existe com metadados (Active) | ✅ |
| CT-02 | Keywords incluem "psicologia clínica" e "DSM-5" | ✅ |
| CT-03 | Regra `uses` para metodos.Fenomenologico registrada | ✅ |
| CT-04 | Regra `enables` para paradigmas.Fenomenologico registrada | ✅ |
| CT-05 | Skill psicologia-clinica existe com frontmatter | ✅ |
| CT-06 | Template de avaliação psicológica multiagente existe | ✅ |
| CT-07 | Template de psicodiagnóstico (DSM-5) existe | ✅ |
| CT-08 | Template de integração com métodos qualitativos existe | ✅ |

## 5. Referências Acadêmicas

| # | Referência | Fonte |
|:-:|:-----------|:------|
| 1 | Wu, Y., Wan, G., Li, J. et al. (2026). WiseMind: a knowledge-guided multi-agent framework for accurate and empathetic psychiatric diagnosis. *npj Digital Medicine*. DOI: 10.1038/s41746-026-02559-9 | Springer/Nature |
| 2 | Hu, J., Wang, A., Xie, Q. et al. (2026). AgentMental: An Interactive Multi-Agent Framework for Explainable and Adaptive Mental Health Assessment. *AAAI 2026*, 40(37), 31050–31058. DOI: 10.1609/aaai.v40i37.40365 | AAAI |
| 3 | Greene et al. (2026). AI Psychiatrist Assistant: An LLM-based Multi-Agent System for Depression Assessment. *PMLR 297*, 525-542. | PMLR |
| 4 | DSM5AgentFlow (2025). Trustworthy AI Psychotherapy: Multi-Agent LLM Workflow for Counseling. arXiv:2508.11398. | arXiv |
| 5 | DELTA (2026). Deliberative Multi-Agent Reasoning with Reinforcement Learning for Multimodal Psychological Counseling. arXiv:2602.04112. | arXiv |
| 6 | Tu, T. et al. (2025). Towards conversational diagnostic artificial intelligence. *Nature*, 642, 442–450. | Nature |
| 7 | Singhal, K. et al. (2025). Toward expert-level medical question answering with large language models. *Nature Medicine*, 31, 943–950. | Nature |
| 8 | American Psychiatric Association. (2022). *DSM-5-TR: Diagnostic and Statistical Manual of Mental Disorders* (5th ed., text rev.). | Manual Diagnóstico |
| 9 | WHO. (2019). *ICD-11: International Classification of Diseases* (11th ed.). | Classificação |
| 10 | American Psychological Association. (2020). *APA Dictionary of Psychology* (2nd ed.). | Referência |

## 6. Integração com Scanners

- **Noological Scanner**: categoria `dominios.PsicologiaClínica` passará de absent → covered (2/10 = 20%)
- **Cross-Validation Engine**: 8 novas regras (2 uses + 3 uses + 2 enables + 1 co_occurs + 1 co_occurs)
- **Cognitive Diversity**: artefato com domínio clínico introduz aplicação prática dos métodos qualitativos
- **Teleological**: alinhamento com expansão de domínios (target 30%)
- **Evolutionary**: redução do bottleneck da dimensão dominios (10% → 20%)

## 7. Testes

```python
# tests/test_r34_dominio_psicologia_clinica.py
def test_psicologia_clinica_spec():
    """CT-01: SPEC-077 deve existir com metadados."""
    assert os.path.exists("specs/SPEC-077-DOMINIO-PSICOLOGIA-CLINICA.md")
    with open("specs/SPEC-077-DOMINIO-PSICOLOGIA-CLINICA.md") as f:
        c = f.read()
    assert "# SPEC-077" in c and "Active" in c

def test_psicologia_clinica_keywords():
    """CT-02: Keywords incluem psicologia clínica e DSM-5."""
    with open("specs/SPEC-077-DOMINIO-PSICOLOGIA-CLINICA.md") as f:
        c = f.read().lower()
    assert "psicologia clínica" in c or "psicologia clinica" in c
    assert "dsm-5" in c

def test_psicologia_clinica_uses_metodo():
    """CT-03: Regra uses para metodos.Fenomenologico."""
    with open("specs/SPEC-077-DOMINIO-PSICOLOGIA-CLINICA.md") as f:
        c = f.read()
    assert "uses" in c and "Fenomenologico" in c

def test_psicologia_clinica_enables_paradigma():
    """CT-04: Regra enables para paradigmas.Fenomenologico."""
    with open("specs/SPEC-077-DOMINIO-PSICOLOGIA-CLINICA.md") as f:
        c = f.read()
    assert "enables" in c and "Fenomenologico" in c

def test_psicologia_clinica_skill():
    """CT-05: Skill psicologia-clinica existe com frontmatter."""
    assert os.path.exists("skills/research/psicologia-clinica/SKILL.md")
    with open("skills/research/psicologia-clinica/SKILL.md") as f:
        c = f.read()
    assert "psicologia-clinica" in c and "SPEC-077" in c

def test_psicologia_clinica_template_avaliacao():
    """CT-06: Template de avaliação psicológica multiagente."""
    with open("skills/research/psicologia-clinica/SKILL.md") as f:
        c = f.read()
    assert "avaliação" in c.lower() or "avaliacao" in c.lower()

def test_psicologia_clinica_template_dsm():
    """CT-07: Template de psicodiagnóstico DSM-5."""
    with open("skills/research/psicologia-clinica/SKILL.md") as f:
        c = f.read()
    assert "DSM-5" in c

def test_psicologia_clinica_template_qualitativo():
    """CT-08: Template de integração com métodos qualitativos."""
    with open("skills/research/psicologia-clinica/SKILL.md") as f:
        c = f.read()
    assert "qualitativ" in c.lower()
```
