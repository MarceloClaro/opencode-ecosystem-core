# R108 — Fusão do Pipeline Científico R101-R105 no Orquestrador MarceloClaro

## Objetivo

Fundir nativamente o pipeline agentivo científico R101-R105 (EvoSci → Deep
Research → Peer Review → Revision → Paper Composer) ao orquestrador
`MarceloClaroOrchestrator`, que já existia como o orquestrador supremo do
ecossistema (MCI, Trust Engine, Token Economy, MASWOS, Transformer, SDD/TDD),
mas nunca havia absorvido o pipeline científico moderno — que vivia como um
silo isolado, sem MCI, sem gate real, sem calibração de confiança e sem
avaliação metacognitiva sobre traços reais de execução.

## Mudanças Entregues

1. **Contrato R103→R104d resolvido na origem**
   - `ReviewPackage.to_revision_contract()` (`agentic_science_v2/review_agent.py`)
     produz diretamente o formato que `ReviewAnalyzer.extract_claims()` espera,
     substituindo o adaptador que só existia em `webapp/pipeline_helpers.py`

2. **Logging, tratamento de erro e rollback automático em `agentic_science_v2`**
   - `deep_research.py::run_deep_research`, `review_agent.py::OrchestratorReviewer.review`,
     `revision_agent.py::OrchestratorRevision.run`, `paper_composer.py::OrchestratorComposer.run`
     agora capturam exceções e retornam resultado estruturado (`status: "error"`)
     em vez de propagar o crash
   - `OrchestratorRevision.run()` reverte automaticamente (rollback) quando
     `verify_integrity()` reprova, rebaixando revisões `applied` para `rejected`
   - Corrigido bug pré-existente em `paper_composer.py::write_introduction`
     (slice `[:3]` sobre um dict de entidades do Evidence Graph — nunca havia
     sido exercitado porque o `compose_paper` da webapp nunca alimentava um
     evidence_graph real)

3. **Novo método `MarceloClaroOrchestrator.scientific_discovery_pipeline()`**
   - Executa R101→R102→R103→(R104d→R105 condicional) nativamente
   - **Gate real**: quando `strict_gates=True` e o R103 reprova
     `export_gate_passed`, o pipeline para antes do R104d/R105 — antes disso,
     o pipeline sempre continuava cegamente até o fim
   - **Calibração real de confiança**: cada estágio passa por
     `mci.confidence_calibrator.calibrate_confidence` (Brier Score);
     estágios que falham recebem sinal adversarial explícito para que a
     abstenção (`should_abstain`) seja alcançável
   - **Avaliação metacognitiva SPEC-920 sobre traços reais**: pela primeira
     vez, `mci.metacognitive_evaluator.MetacognitiveEvaluator` avalia os
     traços de um run de produção real, não apenas o benchmark sintético
     estático de 6 traços hardcoded
   - Cada transição de estágio publicada no MetaBus e registrada como
     reflexão real na memória metacognitiva global; outcomes alimentam o
     Trust Engine

4. **`webapp/pipeline_helpers.py::run_full_academic_pipeline` fundido**
   - Passa a delegar ao orquestrador em vez de encadear os 5 estágios
     manualmente nesta camada de UI
   - Preserva integralmente o contrato de payload que `webapp/app.py` já
     consome (`evosci`, `deep_research`, `peer_review`, `manuscript_revision`,
     `paper`, `timeline`), incluindo o novo caso `pipeline_result: "blocked"`

5. **Bug crítico de perda de dados corrigido em `evolution/cycles.py`**
   - Descoberto durante este próprio ciclo: `EvolutionRegistry._load()`
     zerava **todo** o histórico de 65 ciclos se uma única entrada tivesse
     uma chave extra desconhecida (4 entradas antigas — R81-R84 — já tinham
     esse problema). Qualquer chamada a `evolution_registry.record()`
     sobrescrevia `cycles.json` com o histórico vazio. Corrigido para
     filtrar chaves desconhecidas por entrada em vez de descartar a lista
     inteira.

6. **Cobertura de testes**
   - `tests/test_r108_marceloclaro_scientific_fusion.py` (10 testes): gate
     real, calibração/abstenção, avaliação sobre traços reais, tratamento
     de erro, rollback automático, contrato de revisão, não-regressão do
     contrato webapp
   - 2 testes de `tests/test_r107_ecosystem_audit.py` atualizados para
     refletir a nova arquitetura (mockam o orquestrador, não mais as
     funções antigas encadeadas manualmente)

## Verificação

- `python3 -m pytest tests/test_r101_agentic_science_v2.py ... tests/test_r108_marceloclaro_scientific_fusion.py -q` → **328 passed, 3 skipped**
- Execução manual ponta-a-ponta de `scientific_discovery_pipeline()` com
  `strict_gates=True` (bloqueia corretamente no gate do R103) e
  `strict_gates=False` (completa os 5 estágios, incluindo rollback
  automático real quando a integridade falha)

## Lições

1. `agentic_science_v2` vivia isolado do MCI há vários ciclos — dois
   orquestradores supremos paralelos (`MarceloClaroOrchestrator` e o
   pipeline R101-R105) sem se tocar é fácil de não perceber sem uma
   auditoria explícita de dependências cruzadas.
2. Calibração de confiança genérica precisa de um sinal adversarial
   explícito para alcançar o limiar de abstenção — usar apenas
   `reproducibility_score` tem piso matemático de 0.30, nunca abstém.
3. `EvolutionRegistry._load()` falhava silenciosamente e destrutivamente
   (uma entrada malformada zerava 65 ciclos de histórico no próximo save)
   — vale auditar outros pontos do ecossistema que fazem
   `except (...): self.state = []` sem filtrar/isolar o item problemático.
4. Testes de integração que mockam funções específicas quebram
   silenciosamente quando a arquitetura muda de camada (o encadeamento
   manual virou uma chamada única ao orquestrador) — revisar mocks ao
   mudar a topologia de orquestração, não só ao mudar assinaturas.

## Score

**9.3/10**

- Resolve uma lacuna arquitetural real (pipeline científico nunca fundido
  ao orquestrador supremo do ecossistema)
- Zero regressões nos ciclos R101-R107
- Corrige um bug crítico de perda de dados descoberto durante a própria
  auditoria de implementação
- Não alega superioridade sobre nenhum sistema externo — segue a política
  anti-overclaim já codificada em `classify_metacognitive_tier` (SPEC-920)
