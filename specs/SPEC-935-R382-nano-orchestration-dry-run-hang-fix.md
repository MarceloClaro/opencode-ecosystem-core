---
spec_id: SPEC-935-R382
title: Correção do travamento em dry-run do NanoOrchestrator (QualityChecker sem noção de dry_run)
component: nano_orchestration/quality_checker.py::QualityChecker
status: verified
test_file: tests/test_nano_orchestration.py
---

# SPEC-935-R382 — Corrige Travamento em Dry-Run do NanoOrchestrator

**Data:** 2026-08-03
**Motivação:** achado colateral documentado no `PROGRESS.md` do ciclo R381 —
`tests/test_nano_orchestration.py::TestIntegration` travava indefinidamente
ao rodar a suíte completa, sem exceção nem timeout, obrigando a sessão
anterior a excluir 3 testes (`--deselect`) para conseguir concluir a suíte.
O usuário pediu para investigar e corrigir com rigor, "superando o
desempenho anterior".

## 1. Causa raiz (achada por bissecção, não suposta)

`NanoOrchestrator(dry_run=True)` propaga `dry_run` para `PoolConfig`
(usado por `NanoWriterPool`), mas **nunca** para `QualityChecker`. A Fase
4 (Verificação) chama `quality_checker.verify_and_fix(block, plan)` para
cada bloco. Quando o `score` calculado por `check_block()` fica abaixo de
7.0 — o que acontece quase sempre com o conteúdo simulado do dry-run
("Parágrafo simulado..." repetido, que falha nos critérios de citação,
dados, transição, conclusão etc.) — `verify_and_fix()` chama
`rewrite_block()`, que faz uma chamada HTTP **real** via
`LiteRTMClient.chat()` para `http://localhost:9379/v1/chat/completions`,
com até `MAX_RETRIES=3` tentativas × `timeout=120s` cada, escalonando por
`REWRITE_MODELS` (3 modelos). Sem um daemon LiteRT-LM respondendo nessa
porta (confirmado pelo `doctor`: `litert_lm` → `warn`,
"unavailable... falhas registradas=25"), cada bloco reescrito trava até o
timeout de conexão — e com 30 blocos num plano típico, o tempo acumulado
passa de dezenas de minutos.

Reproduzido isoladamente com instrumentação de log
(`nano_orchestration/orchestrator.py::run()` com `dry_run=True`): a Fase 3
(Escrita) conclui em <10ms (30/30 blocos, dry-run correto); a Fase 4
trava no **primeiro** bloco, log `"Bloco 0: tentando reescrita (2
issues)"`, sem log seguinte. Confirmado por bissecção com timeout de 10s
por teste: `test_end_to_end_orchestration` (via `orch.run()`) e
`test_writer_to_quality_to_coherence` (via `QualityChecker()` direto, sem
`dry_run`) travam; `test_planner_to_sdd_to_writer` (não toca
`QualityChecker`) passa em 0.08s.

## 2. Correção

1. `QualityChecker.__init__` ganha parâmetro `dry_run: bool = False`.
2. `QualityChecker.rewrite_block()` retorna `None` imediatamente quando
   `self.dry_run`, com log explicando que a reescrita via rede é pulada
   em dry-run — **nunca** faz a chamada HTTP. `check_block()` continua
   computando o score real e honesto (não fabrica aprovação); apenas a
   tentativa de correção via modelo real é suprimida.
3. `NanoOrchestrator.__init__` propaga `dry_run=dry_run` para
   `QualityChecker(self.client, dry_run=dry_run)` — antes construía
   `QualityChecker(self.client)` sem o parâmetro.
4. `tests/test_nano_orchestration.py::TestIntegration::
   test_writer_to_quality_to_coherence` corrigido: instancia
   `QualityChecker(dry_run=True)` (antes `QualityChecker()`, sem
   dry_run, apesar do docstring do teste já dizer "(dry-run)" —
   bug de teste, não só de produção).

## 3. Critérios de aceitação

1. `tests/test_nano_orchestration.py` completo roda em segundos (medido:
   76/76 em 1.27s), sem travar, com ou sem `--timeout` externo.
2. `NanoOrchestrator(dry_run=True).run(...)` nunca abre socket de rede
   (comportamento antes quebrado: sempre abria ao menos 1 tentativa por
   bloco reprovado).
3. `dry_run=False` com um `client` real (mock ou LiteRT-LM de verdade)
   continua chamando `rewrite_block()` normalmente — nenhuma regressão de
   comportamento fora do dry-run.
4. Suíte completa (`pytest tests/ -q`) conclui sem `--deselect` e sem
   timeout: medido 343s (5m43s), 64 falhas / 2578 aprovados / 53 pulados
   — as 3 falhas de `TestIntegration` que antes exigiam exclusão manual
   agora passam de verdade, contadas como aprovadas.
5. Zero regressão fora do escopo: nenhuma das 64 falhas remanescentes
   toca `nano_orchestration/` (mesmo conjunto pré-existente de outras
   frentes, já documentado em ciclos anteriores).

## 4. Achado adicional corrigido no mesmo ciclo (fora do escopo original, mas trivial)

`tests/test_r237_diagrams_repair.py::test_readme_mermaid_syntax_blocks`
esperava a string literal `"Mapa da Arquitetura Completa (v3.6.0)"` no
README, mas o commit `5c061a5` (anterior a esta sessão) já havia
deliberadamente atualizado o README para `v3.7.0` sem atualizar este
teste — falha pré-existente desde então. Corrigido o valor esperado no
teste para `v3.7.0` (o README está correto; o teste estava desatualizado).
