# M0 — Diagnóstico e Contrato Acadêmico

## Identificação do Projeto

| Campo | Registro |
|---|---|
| **Tema** | Sesgo algorítmico em diagnóstico de diabetes: avaliação de equidade em populações sub-representadas |
| **Nível** | Artigo original (original research) |
| **Área** | Saúde Pública / Informática em Saúde |
| **Subárea** | Inteligência Artificial Aplicada / Equidade em Saúde |
| **Modalidade** | Estudo quantitativo-computacional |
| **Data** | 09/09/2026 |
| **Status** | Rascunho em produção |

## Pergunta de Pesquisa

**Pergunta principal:** Como modelos de machine learning para diagnóstico de diabetes se comportam em termos de equidade entre populações sub-representadas, considerando etnia e gênero?

**Subperguntas:**
1. Qual é o desempenho discriminativo de quatro algoritmos de ML (Regressão Logística, Random Forest, Gradient Boosting, SVM) para predição de diabetes?
2. Existem disparidades estatisticamente significativas nos fairness metrics (Equalized Odds, Demographic Parity) entre grupos demográficos?
3. A análise interseccional (etnia × gênero) revela disparidades ampliadas que não são captadas pela análise de atributo único?

## Dados Disponíveis

| Fonte | Descrição | Amostra | Status |
|---|---|---|---|
| Pima Indians Diabetes Database | Dataset UCI/8 features | 768 amostras | Disponível |
| Dados demográficos | Simulados (gênero/etnia) | 768 registros | Simulados |

## Periódico-Alvo

| Campo | Especificação |
|---|---|
| **Título** | Frontiers in Public Health |
| **ISSN** | 2296-2563 |
| **Fator de impacto** | 3.0 |
| **Taxa de aceitação** | ~50% |
| **Acesso** | Open Access (APC pago pelo autor) |
| **Formato** | Artigo original, seções IMRaD |
| **Extensão** | 8.000–12.000 palavras |
| **Referências** | 30–50 citadas |
| **Tabelas/Figuras** | Sem limite estrito |

## Restrições Éticas

- ✅ Dataset público e anônimo (UCI Machine Learning Repository)
- ⚠️ Dados demográficos simulados — declarar explicitamente
- ✅ Sem intervenção em seres humanos
- ✅ Sem necessidade de aprovação CEP (dados secundários públicos)

## Mapa de Entregáveis

| Módulo | Entrega | Status |
|---|---|---|
| M0 | Este diagnóstico | ✅ Concluído |
| M1 | Matriz de coerência (problema→pergunta→objetivos→método) | ⏳ |
| M2 | Matriz de referências auditadas com DOI | ⏳ |
| M3 | Protocolo metodológico completo | ⏳ |
| M4 | Tabelas de resultados com fonte | ⏳ |
| M5 | Manuscrito modular LaTeX | ⏳ |
| M6 | PDF formatado Frontiers | ⏳ |
| M7 | Relatório de auditoria da banca | ⏳ |

## Riscos Identificados

1. **Dados demográficos simulados** — deve ser declarado como limitação
2. **Amostra reduzida** (n=768) — pode limitar generalização
3. **Ausência de PyTorch/TensorFlow** — limita aDeep Learning
4. **Auto-score dependente de keyword matching** — não substitui avaliação semântica
