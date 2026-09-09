# M7 — Auditoria Final (Simulação de Banca)

## Rubrica de Avaliação (5 Eixos)

### Eixo 1: Problema e Contribuição

| Critério | Status | Evidência | Risco | Correção |
|---|---|---|---|---|
| Relevância do problema | ✅ Atende | Sessão 1.1, Diabetes afeta 537M adultos | Baixo | — |
| Delimitação clara | ✅ Atende | Sessão 1.2, Pergunta e objetivos definidos | Baixo | — |
| Contribuição demonstrada | ⚠️ Parcial | Sessão 1.4, 4 contribuições listadas | Médio | Fortalecer originalidade |

### Eixo 2: Fundamentação e Debate

| Critério | Status | Evidência | Risco | Correção |
|---|---|---|---|---|
| Literatura revisada | ✅ Atende | 29 referências verificadas | Baixo | — |
| Lacuna demonstrada | ✅ Atende | Sessão 1.2, 3 tipos de lacuna | Baixo | — |
| Diálogo crítico | ⚠️ Parcial | Sessão 5.2, comparação com 3 estudos | Médio | Expandir debate |

### Eixo 3: Método e Ética

| Critério | Status | Evidência | Risco | Correção |
|---|---|---|---|---|
| Desenho justificado | ✅ Atende | Sessão 3.1, PROBAST | Baixo | — |
| Dados descritos | ✅ Atende | Sessão 3.2, variáveis e fonte | Baixo | — |
| Análise apropriada | ✅ Atende | Sessão 3.4, fairness metrics | Baixo | — |
| Ética e transparência | ✅ Atende | Sessão 3.6, dados públicos | Baixo | — |
| Reprodutibilidade | ✅ Atende | Código e dados abertos | Baixo | — |

### Eixo 4: Resultados e Coerência

| Critério | Status | Evidência | Risco | Correção |
|---|---|---|---|---|
| Resultados claros | ✅ Atende | 5 tabelas, sem interpretação | Baixo | — |
| Coerência com método | ✅ Atende | Métricas = objetivos | Baixo | — |
| Interpretação adequada | ✅ Atende | Discussão separada de resultados | Baixo | — |

### Eixo 5: Redação e Normalização

| Critério | Status | Evidência | Risco | Correção |
|---|---|---|---|---|
| Estrutura IMRaD | ✅ Atende | 8 módulos LaTeX | Baixo | — |
| Referências | ✅ Atende | 29 refs com DOI/URL | Baixo | — |
| Tabelas e figuras | ⚠️ Parcial | 5 tabelas, 0 figuras | Médio | Adicionar figuras |
| Linguagem | ⚠️ Parcial | PT/EN misturado | Médio | Traduzir para EN |

## Perguntas Prováveis da Banca

1. **"Como você justifica o uso de dados simulados para análise de equidade?"**
   → Resposta: Dados demográficos simulados são declarados como limitação. Estudo proof-of-concept que demonstra metodologia replicável.

2. **"A amostra de 768 é suficiente para generalização?"**
   → Resposta: Dataset benchmark amplamente aceito na literatura. Resultados devem ser validados em coortes maiores.

3. **"Por que não incluir Deep Learning?"**
   → Resposta: Restrição técnica (sem PyTorch/TensorFlow). Modelos escolhidos são padrão na literatura clínica.

4. **"Como garantir que a simulação de demografia não compromete a validade?"**
   → Resposta: Proporções baseadas em dados reais do CDC. Análise é proof-of-concept, não conclusiva.

## Decisão Editorial

| Status | Descrição |
|---|---|
| `pronto para revisão interna` | Manuscrito estruturado, referências auditadas, pendências menores |
| `não pronto para submissão` | Necessita tradução EN, figuras, seção Author Contributions |

## Ações Corretivas

| Prioridade | Ação | Responsável | Prazo |
|---|---|---|---|
| Alta | Traduzir manuscrito para inglês | Autor | — |
| Alta | Adicionar figuras (heatmap, barras) | Autor | — |
| Média | Adicionar Author Contributions | Autor | — |
| Média | Verificar extensão 8.000–12.000 palavras | Autor | — |
| Baixa | Revisar limitações e expandir discussão | Autor | — |
