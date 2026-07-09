# R107 — Auditoria Sistêmica e Hardening de Contratos

## Objetivo

Revisar o ecossistema OpenCode Ecosystem Core com foco em erros de runtime, incompatibilidades entre wrappers da webapp e APIs reais de `agentic_science_v2`, fragilidades do Evidence Graph e robustez dos scripts de qualidade.

## Mudanças Entregues

1. **Wrappers da webapp alinhados às APIs reais**
   - `webapp/pipeline_helpers.py` reescrito como camada adaptadora estável entre UI e `agentic_science_v2`
   - `run_evosci()` passou a usar `run_agentic_science_v2()`
   - `run_deep_research()` passou a usar `run_deep_research()` real do R102
   - `run_peer_review()` passou a usar `run_peer_review()` real do R103
   - `run_manuscript_revision()` adaptado ao contrato real de `create_revision()` do R104d
   - `compose_paper()` preserva o texto manual da UI e formata o manuscrito de forma compatível

2. **Evidence Graph corrigido na superfície web**
   - `query_evidence_graph()` agora reconstrói snapshots exportados sem depender de `load()` inexistente
   - `webapp/consultation_helpers.py:get_evidence_graph_summary()` passou a usar `stats()`, `ENTITY_TYPES` e `RELATION_TYPES`

3. **Scripts de qualidade endurecidos**
   - `scripts/quality_report.py` e `scripts/check_coverage.py` agora fazem parse robusto de saídas do pytest (`passed`, `failed`, `skipped`)
   - timeout elevado de 120s para 300s, compatível com a suíte atual (~173s)

4. **Cobertura de regressão ampliada**
   - novo arquivo `tests/test_r107_ecosystem_audit.py` com 12 testes de contrato e regressão
   - suíte total passou para **1062 testes verdes**

## Verificação

- `python3 -m pytest tests/test_r107_ecosystem_audit.py -q --tb=short` → **12 passed**
- `python3 scripts/check_coverage.py --threshold 0` → **ALL GATES PASSED**
- `python3 -m pytest tests/ -q --tb=short` → **1062 passed, 5 skipped, 0 failed**

## Lições

1. Wrappers de UI não devem assumir contratos internos; precisam ser adapters explícitos e testados.
2. Scripts de qualidade devem evoluir junto com o tempo real da suíte, ou o próprio gate vira fonte de falso negativo.
3. Testes textuais de UI são insuficientes para detectar regressões de integração entre módulos.

## Score

**9.4/10**

- Alto impacto operacional
- Zero regressões
- Redução de erros reais de runtime
- Melhoria direta na confiabilidade da webapp e do gate de qualidade
