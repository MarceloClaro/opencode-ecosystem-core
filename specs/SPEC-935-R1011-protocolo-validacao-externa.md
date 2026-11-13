---
spec_id: SPEC-935-R1011
title: Protocolo de Validação Externa Autorizada
status: green
validation_scope: external_consent
release_gate: docs/evidence/R1011_R1012_RELEASE_GATE.json
component: marceloclaro/orchestrator + mci.metacognitive_loop + trust.trust_engine
test_file: tests/test_r1011_validacao_externa.py
---

# SPEC-935-R1011 — Protocolo de Validação Externa Autorizada

## 1. Introdução

Este protocolo define o framework para validação externa de resultados de pipelines RAG, propriedades emergentes e métricas comportamentais, operando sob o protocolo SDD/TDD do ecossistema OpenCode Core. A validação externa só será realizada mediante consentimento explícito do operador, com separação clara entre resultados locais e validados externamente.

## 2. Princípios Fundamentais

### 1.1. Consentimento Informado

- **A1**: A validação externa somente será executada mediante consentimento escrito do operador, registrado em `docs/consentimento_validacao_externa.md`
- **A2**: O consentimento deve especificar: dataset de teste, métricas a serem validadas, período de validação e operador responsável
- **A3**: O operador pode revogar o consentimento a qualquer momento, revertendo os resultados para escopo local apenas

### 1.2. Separação de Resultados

- **A3**: Resultados locais (green status) permanecem isolados em `docs/evidence/R1011_local/`
- **A4**: Resultados validados externos são publicados em `docs/evidence/R1011_external/` com dataset hash, métricas e limitações
- **A5**: Um relatório de integração resume a concordância ou discrepância entre resultados locais e externos

### 1.3. Pósura Anti-Overclaim

- **A5**: A validação externa **não** declara o pipeline RAG "compreensivo", "consciente" ou "de qualidade superior"
- **A6**: Apenas confirma ou infere concordância entre métricas locais e externas, com devidas qualificações
- **A7**: Todas as afirmações externas são qualificadas com "sob consentimento do operador", "dataset de teste X" e "limitações Y"

## 2. Estrutura de Dados

### 2.1. Dataset de Teste Externo

- **A5**: O dataset de teste externo deve ser independente do dataset de treinamento/desenvolvimento
- **A6**: O dataset deve conter: queries ground-truth, respostas esperadas (humanas), metadados de domínio
- **A7**: O dataset deve ser disponibilizado em `docs/evidence/R1011_external/dataset/` com hash SHA-256

### 2.2. Métricas de Validação

- **A6**: Métricas de validação devem incluir: precisão (precision), recall, F1-score, taxa de acerto em perguntas factuais
- **A6**: As métricas devem ser calculadas comparando respostas do pipeline RAG com respostas esperadas do dataset ground-truth
- **A7**: As métricas calculadas devem ser publicadas em `docs/evidence/R1011_external/metrics.json` com intervalos de confiança

### 2.3. Relatório de Validação

- **A8**: O relatório de validação deve conter:
  - Dataset usado e hash SHA-256
  - Métricas calculadas (precision, recall, F1, taxa de acerto)
  - Limitações identificadas (domínio fora de escopo, parâmetros de configuração)
  - Correlação entre resultados locais e externos (qualitativa)
  - Data da validação e operador responsável
  - Consentimento do operador registrado

## 3. Protocolo de Execução

### 3.1. Fase de Preparação (Consentimento)

1. Operador autoriza validação externa via comando explícito: `/validar_externo --consentimento`
2. Sistema registra consentimento em `docs/consentimento_validacao_externa.md`
3. Sistema solicita e recebe dataset de teste externo
4. Dataset é validado quanto à integridade (hash SHA-256)

### 3.2. Fase de Execução (Validação)

1. Pipeline RAG processa queries do dataset de teste externo
2. Respostas são comparadas com respostas esperadas (humanas)
3. Métricas de validação são calculadas (precision, recall, F1, taxa de acerto em perguntas factuais)
4. Resultados são publicados em `docs/evidence/R1011_external/`
5. Relatório de validação é gerado em `docs/evidence/R1011_validacao_report.md`

### 3.3. Fase de Pós-Validação

1. Relatório de integração entre resultados locais e externos é gerado
2. Consentimento pode ser revogado, removendo resultados externos
3. Pipeline retorna ao modo local-only se consentimento for retirado
4. Lições aprendidas são registradas no MetaBus (SPEC-935-R886)

## 4. Critérios de Aceitação

A1: Protocolo de validação externa somente é executado com consentimento explícito do operador (arquivo `docs/consentimento_validacao_externa.md` presente).

A2: Dataset de teste externo é independente do dataset de desenvolvimento (hashes diferentes, fontes diferentes).

A3: Métricas de validação (precision, recall, F1, taxa de acerto em perguntas factuais) são calculadas corretamente.

A4: Relatório de validação contém todas as seções exigidas (dataset hash, métricas, limitações, correlação qualitativa, data, operador, consentimento).

A5: Resultados externos são publicados em `docs/evidence/R1011_external/` com devida identificação e limitações.

A6: O operador pode revogar o consentimento a qualquer momento, removendo `docs/evidence/R1011_external/` e atualizando `docs/consentimento_validacao_externa.md`.

## 5. Limites e Responsabilidades

L1: A validação externa **não** demonstra que o pipeline RAG possui "compreensão", "consciência" ou "qualidade profissional" em sentido filosófico ou científico. Apenas valida métricas quantitativas contra dataset ground-truth.

L2: As métricas de validação (precision, recall, F1) são específicas do dataset de teste e não generalizam automaticamente para outros domínios ou queries.

L3: Correlação entre resultados locais e externos não implica causalidade. Pode refletir coincidência, características do dataset de teste ou parâmetros de configuração específicos.

L4: O orchestrador marceloclaro permanece responsável pelo ciclo SDD/TDD; a validação externa é um adicional opcional, não substitui o protocolo local de garantia de qualidade.

L5: Se o consentimento for revogado, todos os resultados externos são removidos e o sistema opera apenas no escopo local com postura fail-closed.

## 6. Plano de Implementação

1. **RED**: Desenvolver framework de protocolo de validação externa (SPEC-935-R1011) e testes de infraestrutura. Espera-se setup de consentimento e dataset de teste.

2. **GREEN**: Implementar coleta de consentimento,(dataset de teste e cálculo de métricas de validação. Conectar ao orchestador marceloclaro.

3. **REFACTOR**: Otimizar fluxo de validação; garantir que separação entre resultados locais e externos seja mantida; validar hashes de dataset e relatórios.

4. **VERIFY**: Executar protocolo de validação com consentimento do operador; gerar relatório de validação e relatório de integração.

5. **REFLECT**: Registrar lições no MetaBus; atualizar confidence ledger apenas para falhas operacionais; registrar ciclo de evolução R1011.

## 6. Evidência Esperada

- `tests/test_r1011_validacao_externa.py` com testes de infraestrutura
- `docs/consentimento_validacao_externa.md` com registro de consentimento do operador
- `docs/evidence/R1011_external/dataset/` com dataset de teste e hash SHA-256
- `docs/evidence/R1011_external/metrics.json` com métricas calculadas (precision, recall, F1, taxa de acerto)
- `docs/evidence/R1011_validacao_report.md` com relatório de validação preenchido
- `docs/evidence/R1011_local/` com resultados locais (sem validação externa)
- `specs/SPEC-935-R1011.md` (este documento) com status final
- Registro de evolução no EvolutionRegistry

## 7. Referências Internas

- SPEC-935-R886 — Ciclo metacognitivo integrado
- SPEC-935-R999 — Pesquisa sobre consciência em sistema agênico orchestrado
- SPEC-935-R1000 — Pipeline Lean 4 + Métricas Comportamentais
- SPEC-935-R1005 — Framework de Auditoria Evolutiva de Pipeline RAG
- SPEC-935-R1006 — Mitigação de Risco em Pipeline RAG
- CORRIGENDUM.md — Histórico de alegações corrigidas sobre validação externa

---
*Este protocolo foi desenvolvido seguindo protocolo SDD rigoroso. A validação externa somente ocorre mediante consentimento explícito do operador. Todos os resultados ficam restritos ao escopo local até consentimento explícito. Os resultados externos são qualificados com limitações e restrições do dataset de teste.*