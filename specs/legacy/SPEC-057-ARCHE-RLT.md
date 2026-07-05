# SPEC-057: ARCHE Reasoning Logic Tree (R28)

**Ciclo:** R28 — ARCHE RLT + OPUS + Witness + RUMI
**Status:** SDD Completo
**Prioridade:** Alta
**Dependências:** SPEC-028 (Scanner Noológico), SPEC-036 (Metacognição), SPEC-038 (TrustEngine)

---

## 1. Visão Geral

Formalizar os **212+ tipos de raciocínio** do ecossistema nos **6 tipos de inferência de Peirce** (ARCHE Benchmark) com uma **Reasoning Logic Tree (RLT)** que compõe inferências em árvores lógicas auditáveis.

**Inspiração:** ARCHE Benchmark (Linsonng/ARCHEBenchmark) — 6 tipos formais de inferência com Reasoning Logic Tree.

---

## 2. Os 6 Tipos de Inferência de Peirce

| # | Tipo | Sigla | Definição Lógica | Exemplo |
|:-:|:-----|:-----:|:-----------------|:--------|
| 1 | **Deduction-Rule** | DR | ∀x(P(x)→Q(x)), P(a) ⊢ Q(a) | Todo homem é mortal. Sócrates é homem. → Sócrates é mortal. |
| 2 | **Deduction-Case** | DC | ∀x(P(x)→Q(x)), Q(a) ⊢ P(a) [probabilístico] | Todo homem é mortal. Sócrates é mortal. → Sócrates é provavelmente homem. |
| 3 | **Induction-Common** | IC | P(a₁)∧Q(a₁), ..., P(aₙ)∧Q(aₙ) ⊢ ∀x(P(x)→Q(x)) | Observar n homens mortais → Todos os homens são mortais. |
| 4 | **Induction-Case** | IH | Q(a), P(a)∧Q(a) → ∀x(P(x)→Q(x)) [teste de hipótese] | Sócrates morreu. Se todos os homens morrem... → Hipótese confirmada. |
| 5 | **Abduction-Knowledge** | AK | Q(a), ∀x(P(x)→Q(x)) ⊢ P(a) [ontologia conhecida] | Sócrates morreu. Homens morrem. → Sócrates era homem. |
| 6 | **Abduction-Phenomenon** | AP | Q(a), ∃x(R(x)→Q(x)) ⊢ R(a) [nova categoria] | Sócrates morreu. Algo causa morte. → Sócrates tinha uma condição letal. |

---

## 3. Reasoning Logic Tree (RLT)

### 3.1 Estrutura do Nó

```python
class RLTNode:
    id: str                    # UUID do nó
    inference_type: PeirceType  # DR, DC, IC, IH, AK, AP
    premise: str               # Premissa do passo
    conclusion: str            # Conclusão do passo
    confidence: float          # 0.0 a 1.0
    children: List[RLTNode]    # Sub-inferências que suportam esta
    metadata: Dict             # Domínio, motores usados, etc.
```

### 3.2 Propriedades da Árvore

- **Profundidade máxima:** 10 níveis
- **Coerência lógica:** Toda conclusão de nó filho deve ser premissa do nó pai
- **Fecho:** A raiz é a conclusão final do raciocínio
- **Folhas:** Premissas originais (evidências, axiomas, dados)

### 3.3 Mapeamento da Taxonomia Atual

Os 59+ tipos existentes são mapeados para os 6 tipos de Peirce:

| Categoria Atual | Tipo Peirce | Critério de Mapeamento |
|:----------------|:-----------:|:-----------------------|
| Dedutivo, Silogístico, Formal, Algorítmico | DR | Regra universal + caso → resultado necessário |
| Probabilístico, Bayesiano | DC | Regra + resultado → caso com probabilidade |
| Indutivo, Generalização, Enumeração | IC | Casos + resultados → regra generalizada |
| Hipotético-Dedutivo, Teste | IH | Resultado + regra hipotética → confirmação |
| Abdutivo, Explicação, Diagnóstico | AK | Resultado + regra conhecida → explicação |
| Inovação, Descoberta, Criativo, Emergente | AP | Resultado → nova categoria explicativa |

---

## 4. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHE RLT Engine                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ReasoningMapper ──► mapeia 212+ tipos → 6 Peirce tipos     │
│                                                              │
│  RLTBuilder ──► constrói árvore lógica a partir de          │
│                  cadeia de raciocínio                        │
│                                                              │
│  RLTValidator ──► verifica coerência lógica:                │
│                    ├─ children→parent premise match          │
│                    ├─ fecho (root = conclusion final)        │
│                    └─ profundidade ≤ 10                      │
│                                                              │
│  RLTVisualizer ──► exporta árvore como dict/JSON/Mermaid    │
│                                                              │
│  MCP Tools ──► eco_run_arche_rlt_build                      │
│                eco_run_arche_rlt_analyze                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Integração com o Ecossistema

```
OQS (R27) ──► problema → pergunta ótima
    │
    ▼
ARCHE RLT (R28) ──► pergunta → árvore lógica de inferência
    │                           │
    ├─► DR/DC: Z3 verificação formal
    ├─► IC/IH: SymPy + estatística
    ├─► AK: miniKanren lógica relacional
    └─► AP: Critical (falácias + vieses)
    │
    ▼
Scanners (SPEC-028-032) ──► análise especializada
```

---

## 6. Métricas de Qualidade

| Métrica | Alvo | Descrição |
|:--------|:----:|:----------|
| Cobertura de mapeamento | 100% | Todos os 212+ tipos mapeados para os 6 Peirce |
| Coerência RLT | ≥95% | Toda conclusão filho é premissa do pai |
| Profundidade média | 3-6 | Equilíbrio entre profundidade e clareza |
| Precisão do tipo Peirce | ≥90% | Classificação correta por validação manual |
| Tempo de construção | <100ms | Para cadeias de até 10 nós |

---

## 7. Casos de Uso

1. **Análise de argumento científico:** Mapear cadeia de raciocínio de um paper para RLT
2. **Depuração de decisão de IA:** Visualizar como um agente chegou a uma conclusão
3. **Ensino de lógica:** Gerar árvores de inferência para materiais didáticos
4. **Auditoria de raciocínio:** Verificar se uma conclusão segue logicamente das premissas
5. **Descoberta de lacunas:** Identificar nós faltantes na árvore (premissas não declaradas)

---

## 8. 12 CTs TDD

| CT | Descrição | Entrada | Resultado Esperado |
|:---|:----------|:--------|:-------------------|
| CT-057-001 | Mapear tipo dedutivo para DR | reasoning_type="modus_ponens" | PeirceType.DR |
| CT-057-002 | Mapear tipo abdutivo para AK | reasoning_type="abduction" | PeirceType.AK |
| CT-057-003 | Construir RLT com 3 nós | 3 premissas encadeadas | Árvore com raiz + 2 filhos |
| CT-057-004 | Validar coerência RLT | Árvore coerente | True, 0 gaps |
| CT-057-005 | Detectar incoerência | Filho não alimenta pai | False, gap identificado |
| CT-057-006 | Profundidade máxima 10 | Cadeia de 12 nós | Truncada para 10 |
| CT-057-007 | Mapeamento dos 59 tipos | Lista completa | 100% mapeados |
| CT-057-008 | Exportar RLT como JSON | Árvore de 5 nós | JSON válido com todos os campos |
| CT-057-009 | Inferência composta DR→IC→AK | Cadeia híbrida | Árvore com 3 tipos diferentes |
| CT-057-010 | RLT com confidence score | Nós com confiança variada | Média propagada para raiz |
| CT-057-011 | Detectar ciclo lógico | Premissa circular | Erro "LogicalCycleError" |
| CT-057-012 | Pipeline OQS→ARCHE RLT | Pergunta → árvore | 12/12 passos encadeados |
