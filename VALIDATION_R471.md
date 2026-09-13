# VALIDATION_R471 — Auditoria dos critérios de aceitação CA1–CA10

Auditoria executada em 2026-09-13 (hermética; sem rede; sem credenciais).
**Esta validação é interna e não constitui certificação externa.**

| CA | Critério | Status | Evidência |
|---|---|---|---|
| CA1 | Sem config, opera idêntico (open_science_only + DEFAULT_SOURCES inalterados + doctor + suíte nativa) | pass | DEFAULT_SOURCES={openalex,crossref,europepmc,arxiv} (sources_ok=True, order_ok=True, sem_restritos=True) |
| CA10 | Anti-overclaim nos relatórios/specs (gate R142) | pass | violadores: nenhum (contexto de proibição/verificação técnica ignorado) |
| CA2 | M1 manuscrito-demo completo com relatório de auditoria por etapa | ressalva | Infraestrutura de auditoria presente (research_factory/audit.py JSONL + artifacts) e testes do estágio presentes; manuscrito-demonstração consolidado M1 com relatório único ainda não produzido (fábrica registra etapas individualmente). |
| CA3 | M2 política OpenShell: egresso autorizado funciona; não autorizado bloqueado com recibo | pass | egresso bibliográfico allow=True; egresso não autorizado deny=True com recibo |
| CA4 | M3 PAIR no doctor e roteador; fallback transparente sem PAIR | pass | sem PAIR -> ollama (fallback_used=True); com PAIR -> pair |
| CA5 | M4 workbench para workspace do Core + licenças em THIRD_PARTY_NOTICES | pass | THIRD_PARTY_NOTICES licenças_ok=True; launch_config workspace_ok=True |
| CA6 | M5 treinamento 64M com seed fixa ou limitação de hardware documentada | pass | seed 42 -> 8 passos; hardware_limitation=True; limitação documentada (sem GPU) |
| CA7 | M6 sem habilitação não aciona; com habilitação CLIExecutionReceipt completo | pass | sem habilitação -> denied/missing_enable; com habilitação -> exit 0, receipt com 10 campos obrigatórios |
| CA8 | Suíte dos módulos com mocks; sem rede/credenciais | pass | pytest tests/test_r471_research_factory.py tests/test_r473_tig_executor.py tests/test_r476_autonomy_reasoning_search.py tests/test_r478_sandbox_pair.py tests/test_r479_m4_m5.py tests/test_r480_m6_scihubeva.py -> 123 passed in 4.23s |
| CA9 | doctor pass (warns apenas CLIs opcionais) + core-check verde | pass | doctor 18/18 (failed=0); core-check exit 0 (overall presente) -> pass |
