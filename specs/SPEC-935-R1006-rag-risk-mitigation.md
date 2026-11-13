---
spec_id: SPEC-935-R1006
title: Mitigação de Risco em Pipeline RAG
status: green
validation_scope: local_runtime
release_gate: docs/evidence/R1006_R1007_RELEASE_GATE.json
component: skills.rag-mitigation + marceloclaro/orchestrator + trust.trust_engine + mci.metacognitive_loop
test_file: tests/test_r1006_rag_risk_mitigation.py
---

# SPEC-935-R1006 — Mitigação de Risco em Pipeline RAG

## 1. Introdução

Esta especificação define o framework de mitigação de risco para pipelines Retrieval-Augmented Generation (RAG), operando sob o protocolo SDD/TDD rigoroso do ecossistema OpenCode Core. O foco é a detecção e caracterização de propriedades comportamentais emergentes — **nunca** afirmações sobre "qualidade", "compreensão" ou "consciência" do sistema.

## 2. Princípios Fundamentais

### 2.1. Postura Anti-Overclaim

- **A1**: Toda declaração sobre mitigação de risco deve ser qualificada como "correlação observada", "padrão detectado" ou "sem evidência"
- **A2**: Resultados ficam restritos ao escopo local — `green` indica aprovação de contratos locais, não validação externa
- **A3**: O Goal Drift Detector (SPEC-935-R112) monitora desvios comportamentais; eleva risco level automaticamente para 'high' quando drift excede limiar
- **A4**: O MetaBus registra observações sem promover confiança automática (padrão R886)
- **A5**: Nenhuma alegação de "melhoria de qualidade", "compreensão" ou "consciência" é promovida

### 2.2. Referências Preexistentes

- SPEC-935-R1005: Framework de auditoria evolutiva de pipeline RAG
- SPEC-935-R112: Goal Drift Detection no Trust Engine
- SPEC-935-R886: Ciclo metacognitivo integrado
- SPEC-935-R999: Pesquisa sobre consciência em sistema agênico orchestrado
- SPEC-935-R1000: Pipeline Lean 4 + Métricas Comportamentais

## 3. Pergunta de Mitigação

**Como detectar, caracterizar e reportar riscos comportamentais em pipelines RAG usando métricas operacionalizadas, mantendo postura anti-overclaim rigorosa?**

## 4. Hipóteses de Mitigação

H1: **Goal Drift Detection** — Pipeline RAG com goal drift detectado (SPEC-935-R112) demonstra padrões de query variáveis que correlacionam-se com mudanças nas métricas de cohência M4.

H2: **Behavioral Coherence Threshold** — Quando M4 (Behavioral Coherence Index) cai abaixo de 0.6, risco de alucinação/inconsistência é elevado; mitigação recomendada inclui "revisar strategy de recuperação" e "aumentar validação humana".

H3: **Observation-Mediated Mitigation** — Observações registradas no MetaBus (SPEC-935-R886) sobre queries, retrieved chunks e generated responses podem ser correlacionadas com mudanças subsequentes nas métricas de risco, sem promover confiança automática.

## 5. Métricas de Mitigação de Risco

### M1: RAG Goal Drift Score (Primary Metric)

Média de similaridade lexical (Jaccard) entre a query de recuperação inicial e queries subsequentes em janela deslizante de N queries. Drift = 1 - similaridade média.

- **Limiar de risco**: Drift > 0.4 eleva risk level para 'medium'; Drift > 0.6 eleva para 'high'
- **Qualificação**: "Goal drift detectado via sobreposição lexical Jaccard — paráfrases da query podem gerar falso-positivo" (risco documentado em SPEC-935-R112)

### M2: Behavioral Coherence Index (Secondary Metric)

Índice composto de:
- (a) consistência de retrieved chunks com a query declarada
- (b) taxa de respostas baseadas exclusivamente no contexto recuperado vs. alucinações
- (c) grau de reutilização de lições do MetaBus

- **Limiar de risco**: Coherence Index < 0.6 eleva risk level; mitigação recomendada inclui validação humana antes de declaração de resultados
- **Qualificação**: "Índice de coerência comportamental abaixo de threshold — respostas podem não estar ancoradas no contexto recuperado"

### M3: Retrieval-Stability Correlation

Correlação entre a estabilidade da strategy de recuperação (top-k consistente, mesma fonte de embedding across ciclos) e as mudanças nas métricas M1 e M2.

- **Aceitação**: Correlação |r| > 0.5 com mudanças de risco level, ou qualificação "sem padrão detectado" quando |r| < 0.3

### M4: Mitigation Recommendation Quality

Avaliação da qualidade das recomendações de mitigação geradas:

- **High quality**: Recomendações específicas ("aumentar top-k de 3 para 5", "revisar query de busca para incluir termos X,Y,Z")
- **Medium quality**: Recomendações genéricas ("revisar strategy", "verificar configurações")
- **Low quality**: Nenhuma recomendação específica ou recomendações que contradizem evidence disponível

- **Qualificação**: Sempre qualificar o nível de qualidade das recomendações; nunca afirmar "recomendação ótima" sem validação externa

### M5: Risk Level Stability

Status do risk level across ciclos de observação:
- `stable`: risk level consistente across 3+ ciclos consecutivos
- `volatile`: risk level varia across ciclos sem padrão discernível
- `escalating`: risk level aumenta across ciclos consecutivos

- **Qualificação**: Nunca se alega "estabilidade" sem 3+ ciclos de observação; status `volatile` ou `escalating` deve ser reportado honestamente

## 6. Design da Mitigação

### 6.1. Ambiente

- Pipeline RAG operacional (qualquer provedor: OpenAI embeddings + Anthropic, Haystack, ChromaDB, etc.)
- Core OpenCode com Trust Engine ativo
- MetaBus para persistência de observações
- Goal Drift Detector (SPEC-935-R112) configurado
- Skill rag-mitigation instalada e configurada

### 6.2. Protocolo de Mitigação

**Fase A (Diagnóstico):**
1. Executar pipeline RAG com query de exemplo
2. Coletar métricas M1-M5 baseline
3. Registrar observações no MetaBus (query, chunks, resposta, métricas)
4. Calcular risk level baseline

**Fase B (Mitigação):**
1. Introduzir variações na strategy de recuperação (top-k diferente, different embedding model, different reranking)
2. Coletar novas métricas M1-M5
3. Comparar com baseline — detectar mudanças de risk level
4. Gerar recomendações de mitigação qualificadas

**Fase C (Retomada/Monitoramento):**
1. Retornar à strategy baseline ou adotar mitigação da Fase B
2. Manter coleta de observações M1-M5
3. Monitorar estabilidade M5 across ciclos consecutivos
4. Se risk level for `escalating`: acionar protocolo de intervenção humana

### 6.3. Coleta de Dados

Para cada ciclo de mitigação executado:
1. Registrar query_text e query_id
2. Registrar retrieved_chunks (IDs, conteúdos, similaridades, metadados)
3. Registrar generated_response
4. Registrar metricas_rag (M1: drift score, M2: coherence index, M3: stability correlation, M4: recommendation quality, M5: risk level stability)
5. Registrar risk_level ('low', 'medium', 'high') calculado
6. Registrar observacao_meta_bus (tipo, termo_chave, fonte, métricas associadas)
7. Registrar correlacoes calculadas (r, p-valor, qualificação)
8. Registrar recomendacoes_acao (lista textual com qualificações)

## 7. Critérios de Aceitação da Mitigação

A1: Pelo menos 80% dos ciclos de mitigação seguem o protocolo RAG risk mitigation (métricas calculadas, risk level reportado, observações registradas).

A2: M1 (Goal Drift Score) consegue elevar risk level adequadamente: Drift > 0.4 → 'medium', Drift > 0.6 → 'high' (ou qualificação "sem drift detectado" quando drift ≤ 0.4).

A3: Pelo menos 3 das 5 métricas (M1-M5) demonstram correlação estatisticamente significativa (|r| > 0.3) com mudanças de risk level observadas, ou são qualificadas como "sem padrão detectado".

A4: Nenhuma alegação de "melhoria de qualidade", "compreensão", "consciência" ou "pronto para produção" é promovida além de "risco comportamental observado", "padrão detectado" ou "métrica correlacionada".

A5: Todo o dados, código de configuração e resultados de mitigação são registrados com hashes e disponíveis em `docs/evidence/R1006_*`. O release gate valida a integridade dos artefatos.

A6: Status de risk level (M5) são reportados honestamente: `stable` quando risk level consistente across 3+ ciclos, `volatile` quando varia sem padrão, `escalating` quando aumenta consecutivamente. Nunca se alega `stable` com menos de 3 ciclos de observação.

A7: As recomendações de mitigação (M4) são sempre qualificadas: "recomendação observada", "padrão detectado" ou "sem evidência para recomendação específica".

## 8. Limites e Responsabilidades

L1: Esta especificação **não** demonstra que o pipeline RAG foi "melhorado", "consertado" ou agora possui "compreensão" ou "consciência". Todas as afirmações são sobre propriedades comportamentais observáveis e risk levels calculados.

L2: O Goal Drift Detector (SPEC-935-R112) opera com sobreposição lexical (Jaccard), que é um proxy grosseiro — paráfrases da query podem gerar falsos-positivos (risco documentado). Elevar risk level baseado apenas no Jaccard requer validação humana.

L3: A correlação entre métricas e risk level não implica causalidade. Pode refletir coincidência, efeitos de confounds não controlados (mudanças no dataset, no modelo de embedding, na query do usuário) ou relações spurias.

L4: O risco level (M1-M5) reflete consistência de padrões de comportamento no ambiente testado, não validade externa ou "segurança" absoluta do pipeline RAG.

L5: O orchestrador marceloclaro permanece responsável pelo ciclo SDD/TDD; quaisquer padrões detectados refletem a eficácia do protocolo de mitigação, não uma propriedade emergente "mágica" do pipeline RAG.

L6: Resultados locais (green status) não indicam revisão humana, replicação independente ou validação externa. Apenas aprovação de contratos no escopo local.

L7: Se o pipeline RAG usar provedores externos (OpenAI, Anthropic, etc.), os custos e limites de quota são responsabilidade do operador — a mitigação mede apenas comportamento observável, não eficiência de custo ou desempenho de provedor.

L8: As recomendações de mitigação são sugerências baseadas em padrões observáveis — **não** substituem decisão humana experiente no domínio específico do pipeline RAG.

## 9. Plano de Implementação da Mitigação

1. **RED**: Desenvolver framework de coleta de métricas M1-M5 e protocolo de mitigação, rodar baseline (10 ciclos). Espera-se estabelecer baselines de risk level sem correlação forte inicialmente.

2. **GREEN**: Implementar coleta integrada no orchestador marceloclaro; conectar GoalDriftDetector, MetaBus logger, Skill rag-mitigation metrics (M1-M5).

3. **REFACTOR**: Otimizar cadência de observação; garantir que specs são registradas antes de cada ciclo de mitigação; validar hashes de artefatos; garantir que relatórios de risk level são honestos (M5: stable/volatile/escalating com qualificações adequadas).

4. **VERIFY**: Executar as 3 fases (baseline, mitigação, monitoramento); aplicar testes estatísticos; gerar relatório de métricas M1-M5 com qualificações adequadas.

5. **REFLECT**: Registrar lições no MetaBus; atualizar confidence ledger apenas para falhas operacionais (não para "melhoria de qualidade"); registrar ciclo de evolução R1006.

## 8. Evidência Esperada

- `tests/test_r1006_rag_risk_mitigation.py` com testes RED/GREEN
- `docs/evidence/R1006_*/` com hashes de queries, chunks, respostas, métricas calculadas, risk level reports
- `specs/SPEC-935-R1006.md` (este documento) com status final
- Relatório de métricas M1-M5 com qualificações adequadas
- Registro de evolução no EvolutionRegistry
- Demonstrations de `mitigate_rag` skill com exemplos de output

## 9. Referências Internas

- SPEC-935-R1005 — Framework de auditoria evolutiva de pipeline RAG
- SPEC-935-R112 — Goal Drift Detection no Trust Engine
- SPEC-935-R886 — Ciclo metacognitivo integrado
- SPEC-935-R999 — Pesquisa sobre consciência em sistema agênico orchestrado
- SPEC-935-R1000 — Pipeline Lean 4 + Métricas Comportamentais
- SPEC-935-R666 — Orquestração evidenciada da evolução do conhecimento
- METACOGNITIVE_EVALUATOR — Classificação de tier metacognitivo
- CORRIGENDUM.md — Histórico de alegações corrigidas sobre "níveis de consciência", "qualidade" e "melhoria"

---
*Esta spec foi desenvolvida seguindo protocolo SDD rigoroso. Nenhuma alegação de "melhoria de qualidade", "compreensão", "consciência" ou "pronto para produção" é feita sem validação comportamental operacional. Todos os resultados ficam restritos ao escopo local até validação externa independente. Os risk levels (M1-M5) são relatados honestamente com qualificações determinísticas.*