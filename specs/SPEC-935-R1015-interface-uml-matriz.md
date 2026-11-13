# Interface UML/Matriz - Monitoramento das 8 Métricas M1-M8

## 1. Visão Geral

Esta seção descreve a interface visual UML/matriz para monitoramento contínuo das 8 métricas comportamentais do pipeline RAG (M1 a M8), conforme definido em SPEC-935-R1006 e SPEC-935-R1010. A interface fornece uma visualização consolidada do status do sistema para operadores e stakeholders.

## 2. Métricas Monitoradas (M1-M8)

### M1: RAG Goal Drift Score (Score de Drift de Objetivo RAG)
- **Tipo**: Métrica primária
- **Faixa**: [0.0, 1.0]
- **Interpretação**: 
  - Drift < 0.2: Estável (nenhum drift detectado)
  - 0.2 ≤ Drift < 0.4: Moderado (drift leve detectado)
  - 0.4 ≤ Drift < 0.6: Aumento de risco
  - Drift ≥ 0.6: Alto risco (drift significativo)
- **Qualificação**: "drift observado", "drift leve", "drift significativo" ou "sem drift detectado"

### M2: Behavioral Coherence Index (Índice de Coerência comportamental)
- **Tipo**: Métrica secundária
- **Faixa**: [0.0, 1.0]
- **Interpretação**:
  - Coerência > 0.8: Alta coerência
  - 0.6 ≤ Coerência ≤ 0.8: Coerência moderada
  - Coerência < 0.6: Baixa coerência (risco de alucinação/inconsistência)
- **Qualificação**: "coerência alta", "coerência moderada", "coerência baixa" ou "coerência observada"

### M3: Retrieval-Stability Correlation (Correlação de Estabilidade de Recuperação)
- **Tipo**: Métrica de correlacionamento
- **Faixa**: [-1.0, 1.0]
- **Interpretação**:
  | Valor | Interpretação |
  |-------|-------------|
  | |ρ| > 0.7 | Alta estabilidade |
  | 0.3 < |ρ| ≤ 0.7 | Estabilidade moderada |
  | |ρ| ≤ 0.3 | Baixa estabilidade (instabilidade detectada) |
- **Qualificação**: "estabilidade alta", "estabilidade moderada", "estabilidade baixa" ou "instabilidade observada"

### M4: Mitigation Recommendation Quality (Qualidade das Recomendações de Mitigação)
- **Tipo**: Métrica de qualidade
- **Faixa**: [0.0, 1.0]
- **Interpretação**:
  - Qualidade > 0.8: Recomendações de alta qualidade
  - 0.6 ≤ Qualidade ≤ 0.8: Recomendações de qualidade moderada
  - Qualidade < 0.6: Recomendações de baixa qualidade
- **Qualificação**: "recomendação de alta qualidade", "recomendação de qualidade moderada", "recomendação de baixa qualidade" ou "recomendação observada"

### M5: Risk Level Stability (Estabilidade do Nível de Risco)
- **Tipo**: Métrica de status
- **Valores**: `stable` | `volatile` | `escalating`
- **Interpretação**:
  - `stable`: Nível de risco consistente across 3+ ciclos de observação
  - `volatile`: Risco varia sem padrão discernível
  - `escalating`: Risco aumenta consecutivamente
- **Qualificação**: "risco estável", "risco volátil", "risco escalando" ou "status observado"

### M6: Cross-Provider Consistency (Consistência entre Provedores)
- **Tipo**: Métrica de comparativo
- **Faixa**: [0.0, 1.0]
- **Interpretação**:
  - M6 > 0.6: Consistência alta across provedores
  - 0.3 < M6 ≤ 0.6: Consistência moderada
  - M6 ≤ 0.3: Consistência baixa (inconsistência detectada)
- **Qualificação**: "consistência alta", "consistência moderada", "consistência baixa" ou "inconsistência observada"

### M7: Context Window Sensitivity (Sensibilidade da Janela de Contexto)
- **Tipo**: Métrica de variabilidade
- **Faixa**: [-0.5, 0.5] (inclinação da regressão)
- **Interpretação**:
  - |M7| > 0.1: Sensibilidade significativa ao tamanho da janela
  - |M7| ≤ 0.1: Insensibilidade (qualidade estável across tamanhos)
- **Sinal**: Positive = qualidade melhora com janela maior; Negative = qualidade degrada com janela maior
- **Qualificação**: "sensibilidade alta", "sensibilidade baixa", "variabilidade observada" ou "insensibilidade detectada"

### M8: Temporal Decay of Retrieval Quality (Decaimento Temporal da Qualidade da Recuperação)
- **Tipo**: Métrica temporal
- **Faixa**: [0.0, 1.0] (porcentagem de decaimento)
- **Interpretação**:
  - M8 > 0.2 (20%): Obsolescência detectável; requer atualização de dataset
  - 0.1 < M8 ≤ 0.2: Decaimento moderado
  - M8 ≤ 0.1: Decaimento mínimo ou nenhum
- **Qualificação**: "decaimento observado", "decaimento mínimo detectado" ou "dados insuficientes"

## 3. Interface Matriz UML

### 3.1. Diagrama de Matriz de Métricas

```
       M1      M2      M3      M4      M5      M6      M7      M8
  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
  │ Drift│Coerência│Stability│Qualidade│Risco│Consistência│Sensibilidade│Decaimento│
  │ Score│Index   │Correlation│Rec. Quality│Level│Across Providers│Window│Temporal│
  └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

### 3.2. Cores e Status Visual

| Status | Cor | Significado |
|--------|-----|-------------|
| ✅ Green | Verde | Valor dentro de limites aceitáveis |
| ⚠️ Yellow | Amarelo | Aviso - monitorar |
| ❌ Red | Vermelho | Crítico - ação requerida |
| 🟡 Orange | Laranja | Decaimento/moderação |

### 3.3. Matriz de Dependências

```
M1 → M2 → M3 → M4 → M5 (cadeia de risco)
       ↑           ↑
       |           |
M6 ← M7 ← M8 (correlações cross-métricas)
```

## 4. Interface de Usuário Projeto

### 4.1. Layout da Interface

```
+===========================================================================+
|                        MONITORAMENTO M1-M8 - RAG                          |
+===========================================================================+

+----------+------------------+------------------+------------------+
|  M1 M2 M3  |      M4          |      M5          |      M6          |
| Drift     | Qualidade Risk   |  Level           | Consistência     |
|  Score    |  Recommendation  |  Stable/Volat.   | Across Providers |
+----------+------------------+------------------+------------------+
|  M7 M8                                                              |
| Sens. Window  |  Decaimento Temporal                       |
|   M7          |      M8                                      |
+===========================================================================+

+----------+--------------------------------------------------------------+
|   STATUS GERAL                                                    |
+----------+--------------------------------------------------------------+
|  █████████ | Stable  |  ████████  | Volatile  |  ████████  | Escalating |
+----------+--------------------------------------------------------------+

+===========================================================================+
|                          NOTIFICAÇÕES                                    |
+===========================================================================+
| • M1 Drift: 0.35 ⚠️ - Drift moderado detectado - revisar strategy    |
| • M3 Stability: |ρ|=0.45 📊 - Estabilidade moderada - monitorar        |
| • M7 Sensitivity: |M7|=0.08 ✅ - Insensibilidade - ok                   |
| • M8 Decay: 0.15 ⚠️ - Decaimento moderado - planejar atualização |
+===========================================================================+
```

### 4.2. Atualização em Tempo Real

A interface é atualizada a cada ciclo de observação (padrão: a cada 10 queries processadas). As mudanças de status acionam notificações quando:

1. Alguma métrica atravessa um limiar de mudança de status
2. Padrão cross-métrico é detectado (ex: M1 aumento + M5 escalation)
3. Limiares de alerta são excedidos (definidos por configuração do operador)

## 5. Critérios de Aceitação da Interface

A1: Todas as 8 métricas (M1-M8) são exibidas na interface com seus valores atuais
A2: Cores/status visuais são consistentes com as definições de qualificação
A3: Matriz de dependências reflete correlações conhecidas entre métricas
A4: Notificações são acionadas corretamente quando limiares são excedidos
A5: Interface mantém postura anti-overclaim: nenhum status declara "qualidade profissional" ou "segurança absoluta"
A6: Qualificações textuais são sempre fornecidas junto com valores numéricos
A7: Interface é gerada a partir de dados reais do MetaBus e do Trust Engine, não de simulações

## 6. Limites e Responsabilidades

L1: A interface UML/matriz é uma ferramenta de monitoramento visual, não um
    julgamento de "qualidade do sistema" ou "performance aprovada"

L2: Status coloridos indicam estado observado, não garantia de funcionamento

L3: Qualificações textuais são obrigatórias - valores numéricos sozinhos não são
    exibidos sem contexto qualitativo

L4: O orchestrador marceloclaro permanece responsável pelo ciclo SDD/TDD; a
    interface é um adicional de visualização

L5: Dados da interface são derivados de métricas M1-M8 operacionalizadas, não
    de alegações filosóficas sobre "consciência" ou "compreensão" do sistema

## 7. Plano de Implementação

1. **RED**: Definir framework de interface UML/matriz (SPEC-935-R1015) e mock-ups
2. **GREEN**: Implementar interface conectada ao MetaBus e Trust Engine; exibir
   métricas M1-M8 em tempo real com qualificações adequadas
3. **REFACTOR**: Otimizar layout e cores; garantir que qualificações sejam
   consistentes com as definitions de cada métrica; validar hashes de
   artefatos de interface
4. **VERIFY**: Executar interface com dados reais do pipeline; gerar relatório
   de usabilidade da interface; validar que postura anti-overclaim é mantida
5. **REFLECT**: Registrar lições no MetaBus; atualizar confidence ledger apenas
   para falhas de exibição; registrar ciclo de evolução R1015

## 6. Evidência Esperada

- `specs/SPEC-935-R1015-interface-uml-matriz.md` (este documento)
- `docs/evidence/R1015_*/` - captures da interface em operação
- `tests/test_r1015_interface_uml.py` - testes de renderização e qualificação
- `evolution/cycles.py` - Registro de evolução R1015
- Diagramas UML em formatos Mermaid, PlantUML ou SVG

## 7. Referências Internas

- SPEC-935-R1014 — Integração com Mais Provedores de Embedding e LLM
- SPEC-935-R1013 — Hipóteses H9-H10 de Propriedades Emergentes Avançadas em RAG
- SPEC-935-R1012 — Hipóteses H6-H8 de Propriedades Emergentes Avançadas em RAG
- SPEC-935-R1010 — Expansão de Métricas M6-M8 para RAG
- SPEC-935-R1006 — Mitigação de Risco em Pipeline RAG
- SPEC-935-R886 — Ciclo Metacognitivo Integrado
- CORRIGENDUM.md — Histórico de Alegações Corrigidas

---
*Interface UML/matriz desenvolvida seguindo protocolo SDD rigoroso. Monitoramento
visual de métricas comportamentais M1-M8. Todos os resultados restritos ao escopo
local. Qualificações textuais obrigatórias junto com valores numéricos. Pósura
anti-overclaim mantida em todo o documento.*