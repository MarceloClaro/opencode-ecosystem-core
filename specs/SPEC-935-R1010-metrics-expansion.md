---
spec_id: SPEC-935-R1008
title: Expansão de Métricas M6-M8 para RAG
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R1008_R1009_RELEASE_GATE.json
component: marceloclaro/orchestrator + mci.metacognitive_loop + trust.trust_engine
test_file: tests/test_r1008_metrics_expansion.py
---

# SPEC-935-R1008 — Expansão de Métricas M6-M8 para RAG

## 1. Introdução

Esta especificação define três novas métricas para o framework de avaliação de pipelines RAG, operando sob o protocolo SDD/TDD rigoroso do ecossistema OpenCode Core. O foco é expandir as capacidades de monitoramento comportamental — **nunca** afirmar "melhoria de qualidade", "compreensão" ou "consciência" do sistema.

## 2. Princípios Fundamentais

### 2.1. Postura Anti-Overclaim

- **A1**: Toda declaração sobre novas métricas deve ser qualificada como "correlação observada", "padrão detectado" ou "sem evidência"
- **A2**: Resultados ficam restritos ao escopo local — `green` indica aprovação de contratos locais, não validação externa
- **A3**: Métricas M6-M8 complementam M1-M5 de SPEC-935-R1006; não as substituem
- **A4**: O Goal Drift Detector (SPEC-935-R112) continua operacional durante o uso das novas métricas
- **A5**: Nenhuma alegação de "melhoria de qualidade", "compreensão" ou "consciência" é promovida

### 2.2. Referências Preexistentes

- SPEC-935-R1006: Mitigação de Risco em Pipeline RAG
- SPEC-935-R1005: Framework de Auditoria Evolutiva de Pipeline RAG
- SPEC-935-R112: Goal Drift Detection no Trust Engine
- SPEC-935-R886: Ciclo metacognitivo integrado
- SPEC-935-R666: Orquestração evidenciada da evolução do conhecimento

## 3. Definição das Novas Métricas

### M6: Cross-Provider Consistency (Consistência entre Provedores)

**Descrição**: Mede a correlação entre outputs de embeddings de provedores diferentes (ex: OpenAI vs. HuggingFace vs. Cohere) para o mesmo conjunto de queries. Avalia se os patterns de recuperação são consistentes across provedores, o que indica comportamento comportamental estável independentemente do provedor usado.

**Formalização M6**:
- Se o pipeline RAG utiliza múltiplos provedores de embedding para o mesmo conjunto de queries
- E a similaridade de ordenação de resultados across provedores for calculada via Spearman correlation
- Então M6 = |ρ|, onde ρ é o coeficiente de correlação de Spearman entre rankings de resultados
- **Limiar de monitoramento**: M6 > 0.6 indica consistência comportamental across provedores; M6 < 0.3 indica inconsistidade que requer investigação

**Aceitação M6**:
- M6-1: M6 pode ser calculado quando pelo menos 2 provedores de embedding são utilizados para o mesmo queries set
- M6-2: M6 > 0.6 eleva "consistency flag" para 'alta'; M6 < 0.3 eleva para 'baixa'; 0.3 ≤ M6 ≤ 0.6 para 'moderada'
- M6-3: Todas as classificações de flag de consistência são qualificadas: "consistência observada", "inconsistência detectada" ou "dados insuficientes"
- M6-4: Nenhuma alegação de "provedor superior" ou "inferior" é promovida; apenas comportamentos observados são reportados

### M7: Context Window Sensitivity (Sensibilidade da Janela de Contexto)

**Descrição**: Mede como a qualidade da recuperação do pipeline RAG varia com o tamanho da janela de contexto fornecida ao modelo de linguagem. Avalia se há um threshold ótimo de contexto além do qual a qualidade não melhora (ou piora) — sinal de saturação ou ruído.

**Formalização M7**:
- Se o pipeline RAG é testado com múltiplos tamanhos de janela de contexto (ex: 512, 1024, 2048, 4096 tokens)
- E a qualidade da recuperação (ex: taxa de chunks relevantes, precisão da resposta) for medida para cada tamanho
- Então M7 = taxa de variação da qualidade vs. tamanho da janela, calculada como a inclinação da regressão linear da qualidade vs. log(tamanho da janela)
- **Limiar de monitoramento**: |M7| > 0.1 indica sensibilidade significativa ao tamanho da janela; |M7| ≤ 0.1 indica insensibilidade (qualidade estável across tamanhos)

**Aceitação M7**:
- M7-1: M7 pode ser calculado quando o pipeline RAG suporta múltiplos tamanhos de contexto configuráveis
- M7-2: |M7| > 0.1 eleva "sensibility flag" para 'alta'; |M7| ≤ 0.1 eleva para 'baixa'; -0.1 < M7 < 0.1 para 'moderada'
- M7-3: Todas as classificações de flag de sensibilidade são qualificadas: "sensibilidade observada", "insensibilidade detectada" ou "dados insuficientes"
- M7-4: Nenhuma alegação de "janela ótima" ou "tamanho ideal" é promovida; apenas comportamentos observados de variabilidade são reportados

### M8: Temporal Decay of Retrieval Quality (Decaimento Temporal da Qualidade da Recuperação)

**Descrição**: Mede como a qualidade da recuperação do pipeline RAG decai ao longo do tempo à medida que os chunks do dataset envelhecem. Avalia se há obsolescência detectável dos documentos recovery que requer atualização ou manutenção do dataset.

**Formalização M8**:
- Se o pipeline RAG for testado com chunks do dataset em diferentes faixas etárias (ex: últimos 30 dias, 30-90 dias, 90-180 dias, 180+ dias)
- E a taxa de recuperação bem-sucedida for medida para cada faixa etária
- Então M8 = taxa de decaimento = 1 - (taxa_success_latest / taxa_success_oldest), expressa como porcentagem
- **Limiar de monitoramento**: M8 > 0.2 (20% de decaimento) indica obsolescência detectável; requisita atualização de dataset; M8 ≤ 0.1 indica decaimento mínimo

**Aceitação M8**:
- M8-1: M8 pode ser calculado quando o pipeline RAG suporta timestamp tracking dos chunks recuperados
- M8-2: M8 > 0.2 eleva "obsolescence flag" para 'alta'; M8 ≤ 0.1 eleva para 'baixa'; 0.1 < M8 ≤ 0.2 para 'moderada'
- M8-3: Todas as classificações de flag de obsolescência são qualificadas: "decaimento observado", "decaimento mínimo detectado" ou "dados insuficientes"
- M8-4: Nenhuma alegação de "dataset desatualizado" ou "necessidade imediata de refresh" é promovida; apenas comportamentos observados de decaimento são reportados

## 3. Design da Expansão

### 3.1. Ambiente

- Pipeline RAG operacional com capacidade de:
  - M6: Utilizar múltiplos provedores de embedding (OpenAI, HuggingFace, Cohere)
  - M7: Suportar múltiplos tamanhos de contexto configuráveis
  - M8: Track timestamps dos chunks recuperados do dataset
- Core OpenCode com Trust Engine ativo (SPEC-935-R112)
- MetaBus para persistência de observações (SPEC-935-R886)
- Dataset de exemplo com chunks de diferentes idades (para M8)

### 3.2. Protocolo de Expansão

**Fase A (Baseline M6-M8):**
1. Estabelecer baseline com configurações padrão (um provedor, contexto padrão, chunks recentes)
2. Coletar M1-M5 de SPEC-935-R1006
3. Registrar observações no MetaBus
4. Definir parâmetros base para expansão

**Fase B (M6 - Cross-Provider):**
1. Configurar pipeline RAG para utilizar múltiplos provedores de embedding (pelo menos 2)
2. Executar mesmo queries set com todos os provedores
3. Calcular similaridade de ordenação (Spearman ρ) entre rankings
4. Classificar flag de consistência (alta/baixa/moderada) com qualificações
5. Registrar observações no MetaBus sobre variações de provedor

**Fase C (M7 - Context Window):**
1. Configurar pipeline RAG para testar múltiplos tamanhos de contexto (ex: 512, 1024, 2048)
2. Executar mesmo queries set com todos os tamanhos
3. Medir qualidade da recuperação para cada tamanho (taxa de chunks relevantes)
4. Calcular M7 = inclinação da regressão linear qualidade vs. log(tamanho)
5. Classificar flag de sensibilidade (alta/baixa/moderada) com qualificações
6. Registrar observações no MetaBus sobre variações de contexto

**Fase D (M8 - Temporal Decay):**
1. Configurar pipeline RAG para track timestamps dos chunks recuperados
2. Classificar chunks em faixas etárias (ex: últimos 30 dias, 30-90 dias, 90-180 dias, 180+ dias)
3. Medir taxa de recuperação bem-sucedida para cada faixa etária
4. Calcular M8 = 1 - (taxa_success_latest / taxa_success_oldest) como porcentagem
5. Classificar flag de obsolescência (alta/baixa/moderada) com qualificações
6. Registrar observações no MetaBus sobre decay temporal

**Fase C (Retomada):**
1. Retornar às configurações baseline
2. Manter coleta de M6-M8
3. Monitorar flags de consistência, sensibilidade e obsolescência across ciclos consecutivos
4. Se múltiplas flags indicarem problemas (baixa consistência, alta sensibilidade, alta obsolescência): acionar protocolo de revisão de pipeline

### 3.3. Coleta de Dados

Para cada experiência de expansão executada:
1. Registrar métrica tipo (M6, M7 ou M8)
2. Registrar parâmetros de configuração (provedores, tamanhos de contexto, faixas etárias)
3. Registrar valores brutos de métrica (ρ para M6, inclinação M7, taxa decaimento M8)
4. Registrar flag de classificação (alta/baixa/moderada) com qualificação
5. Registrar observacao_meta_bus (tipo, parametros, metricas associadas)
6. Registrar correlacoes calculadas (se applicable) e p-valores
7. Registrar resultado_experiencia (flag classificada com qualificacao)

## 4. Critérios de Aceitação da Expansão

A1: Pelo menos 80% dos experiments na Fase A seguem o protocolo M6-M8 (parametros definidos, metricas calculadas, flags classificadas).

A2: M6 consegue distinguir pipelines com múltiplos provedores vs. single provider (p-valor < 0.05 em teste estatistico, ou qualificacao "dados insuficientes" quando menos que 2 provedores disponiveis).

A3: M7 consegue distinguir pipelines com variacao de contexto significant vs. stantard (p-valor < 0.05 em teste estatistico, ou qualificacao "dados insuficientes" quando configuraoes de contexto nao disponiveis).

A4: M8 consegue distinguir datasets com decaimento detectable vs. dataset recentes (p-valor < 0.05 em teste estatistico, ou qualificacao "dados insuficientes" quando tracking de timestamp nao disponivel).

A5: Pelo menos 3 das 3 novas métricas (M6-M8) demonstram resultados calculaveis com qualificacoes adequadas (|r| > 0.3 ou flags classificadas adequadas).

A6: Nenhuma alegacao de "melhoria de qualidade", "provedor superior", "janela otima" ou "dataset desatualizado" eh promovido. Todas as classificacoes de flag sao qualificadas adequadamente.

A7: As flags de classificacao (M6: alta/baixa/moderada; M7: alta/baixa/moderada; M8: alta/baixa/moderada) sao sempre qualificadas: "consistencia observada", "insensibilidade detectada", "decaimento observado", ou "dados insuficientes".

A8: M6-M8 complementam M1-M5 de SPEC-935-R1006; nao as substituem. Toda relatoria integra as metrics novas e antigas com qualificacoes adequadas.

## 5. Limites e Responsabilidades

L1: Esta expansao de metricas **nao** demonstra que o pipeline RAG foi "melhorado", "otimizado" ou agora possui "consciencia" ou "compreendese melhor". Todas as afirmacoes sao sobre propriedades comportamentais observables e flags classificadas.

L2: M6 depende da disponibilidade de pelo menos 2 provedores de embedding. Menos que 2 provedores disponiveis resulta em flag "dados insuficientes" com qualificacao adequada.

L3: M7 depende do pipeline RAG suportar multiples tamanhos de contexto configuráveis. Pipeline sem essa capacidade resulta em flag "dados insuficientes" com qualificacao adequada.

L4: M8 depende do pipeline RAG suportar timestamp tracking dos chunks recuperados. Pipeline sem essa capacidade resulta em flag "dados insuficientes" com qualificacao adequada.

L5: A correlacao entre metrics M6-M8 e behavior observado nao implica causalidade. Pode refletir coincidencia, effects de confounds nao controlados (qualidade dos datasets dos provedores, configuracao do pipeline, randomidade inerente) ou relacoes spurias.

L6: As flags de classificacao (alta/baixa/moderada) refletem consistencia de padroes de comportamento no ambiente testado, nao validade externa ou "qualidade absoluta" do pipeline RAG.

L7: O orchestrador marceloclaro permanece responsavel pelo ciclo SDD/TDD; quaisquer padroes detectados refletem a eficacia do protocolo, nao uma propriedade emergente "magica" do pipeline RAG.

L8: Resultados locais (green status) nao indicam revisao humana, replicacao independente ou validacao externa. Apenas aprovacao de contratos no escopo local.

L9: Se o pipeline RAG usar provedores externos de embedding (OpenAI, HuggingFace, Cohere), os custos e limites de quota sao responsabilidade do operador -- a expansao de metrics mede apenas comportamento observavel, nao eficiência de custo ou performance de provedor.

L10: O tracking de timestamp para M8 adiciona overhead de storage e processamento no pipeline RAG. O operador deve considerar esse custo ao implementar o tracking.

## 6. Plano de Implementacao da Expansao

1. **RED**: Desenvolver framework de coleta de metricas M6-M8 e rodar baseline (10 experiments). Espera-se estabelecer baselines sem calculos fortes inicialmente (flags "dados insuficientes" quando configuracoes nao disponiveis).

2. **GREEN**: Implementar coleta integrada no orchestador marceloclaro; conectar metricas M6-M6; integrar com Trust Engine (SPEC-935-R112); registrar observacoes no MetaBus (SPEC-935-R886).

3. **REFACTOR**: Otimizar cadencia de experiencia; garantir que parametros sao configurados adequadamente; validar hashes de metricas e flags classificadas; garantir que relatorios de flags classificadas sao honestos (M6-M8: alta/baixa/moderada com qualificacoes deterministicas).

4. **VERIFY**: Executar as fases A-D (baseline, M6, M7, M8); aplicar testes estatisticos; gerar relatorio de metricas M6-M8 com qualificacoes adequadas.

5. **REFLECT**: Registrar liacoes no MetaBus; atualizar confidence ledger apenas para falhas operacionais (nao para "melhoria de qualidade"); registrar ciclo de evolucao R1008.

## 6. Evidencia Esperada

- `tests/test_r1008_metrics_expansion.py` com testes RED/GREEN
- `docs/evidence/R1008_*/` com hashes de configuracoes, metricas calculadas, flags classificadas
- `specs/SPEC-935-R1008.md` (este documento) com status final
- Relatorio de metricas M6-M8 com qualificacoes adequadas
- Registro de evolucao no EvolutionRegistry
- Demonstrations de calculos M6 (cross-provider), M7 (context window), M8 (temporal decay)

## 6. Referencias Internas

- SPEC-935-R1006 — Mitigação de Risco em Pipeline RAG
- SPEC-935-R1005 — Framework de Auditoria Evolutiva de Pipeline RAG
- SPEC-935-R112 — Goal Drift Detection no Trust Engine
- SPEC-935-R886 — Ciclo metacognitivo integrado
- SPEC-935-R666 — Orquestração evidenciada da evolução do conhecimento
- METACOGNITIVE_EVALUATOR — Classificação de tier metacognitivo
- CORRIGENDUM.md — Histórico de alegações corrigidas sobre "melhoria de qualidade", "provedor superior" e "janela ótima"

---
*Esta spec foi desenvolvida seguindo protocolo SDD rigoroso. Nenhuma alegação de "melhoria de qualidade", "provedor superior", "janela ótima" ou "dataset desatualizado" é feita sem validação comportamental operacional. Todas as flags de classificação são qualificadas: "consistência observada", "insensibilidade detectada", "decaimento observado" ou "dados insuficientes". Todos os resultados ficam restritos ao escopo local até validação externa independente.*