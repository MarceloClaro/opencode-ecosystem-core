---
spec_id: SPEC-935-R480
title: Fase 4 da R471 — frontend de download opt-in SciHubEVA (M6)
component: workbench (scihubeva_frontend), scientific_lab.restricted_resolver (herdado)
test_file: tests/test_r480_m6_scihubeva.py
status: green
estoque: rc
data: 2026-09-13
---

# SPEC-935-R480 — Fase 4: frontend de download opt-in SciHubEVA

## Objetivo
Executar a Fase 4 do roadmap da SPEC-935-R471: empacotar a GUI SciHubEVA como
frontend do resolvedor de acesso restrito da R470 (allowlist `scihubeva`), com
recibos e autorização idênticos. A GUI **nunca altera a política**: todos os
gates da R470 (enabled → policy → allowlist → auth → rights → evidence → ask)
são herdados da fachada `scientific_lab.restricted_resolver`.

## Não-objetivos
- Não executar binário real, persistir arquivo ou usar rede em qualquer caminho
  desta versão (download permanece `pending_manual_execution`; CA7/CA8).
- Não tornar SciHubEVA/sci-hub padrão nem fallback automático (invariante 1 da
  R471 e R468/R469).
- Não contornar paywalls nem orientar violação de controles de acesso; a
  juridicidade cabe ao operador humano declarante (aviso não-jurídico R470).
- Não permitir que a GUI escolha política/allowlist/autorização (fake-neutral).

## Invariantes
1. A política efetiva vem apenas do ambiente (R470 `request_from_env`); o
   parâmetro `requested_policy` da GUI é deliberadamente não repassado à fachada
   (teria precedência e violaria a neutralidade da GUI).
2. Sem `RESTRICTED_RESOLVER_ENABLED=1`, nenhum caminho aciona SciHubEVA
   (recibo `denied`/`missing_enable`; executor nunca chamado).
3. Resolver `scihubeva` fora da allowlist é negado (`unknown_resolver`);
   autorização, base de direitos e evidência são obrigatórias (R470).
4. `argv` é sempre lista de strings (nunca shell); módulo sem import de
   subprocess/socket/urllib.request (CA8).
5. Recibos (`CLIExecutionReceipt` e download receipt) nunca contêm credenciais.
6. Download real: `status == "pending_manual_execution"`, `path=None`,
   `bytes=0`, `sha256=None`, com limitações fixas (no-redistribution,
   not-legal-advice).
7. Nenhum artefato com "superhuman"/"verificado"/"Qualis A1"/"superação".

## Critérios de aceitação
- CA7': sem habilitação → denied com código; com habilitação completa →
  `CLIExecutionReceipt` com todos os campos obrigatórios (command, resolver,
  policy_effective, enabled_effective, authorization_id, decision, deny_code,
  timestamp_utc, orchestrator, hash_sha256).
- CA8': 19 testes herméticos; módulo sem rede/binário; executor injetável nunca
  chamado na negação.
- CA9': doctor permanece pass (warn apenas de CLIs opcionais ausentes).
- CA10: anti-overclaim.
- CA11: ciclo R480 registrado no EvolutionRegistry com score e lições.

## Plano TDD
RED: 19 testes em `tests/test_r480_m6_scihubeva.py` antes da implementação —
falha na coleta. GREEN: `workbench/scihubeva_frontend.py` (SciHubEVARequest,
validate_target, launch_argv, SciHubEVAFrontend.submit herdando
dispatch_restricted); 2 ajustes de teste/vocabulário (argv usa `scihubeva`;
comentário sem nomes de módulos proibidos). VERIFY: 19/19; regressões do
estágio; suíte completa; doctor; ciclo registrado.

## Observação de licença
SciHubEVA (leovan) é MIT; o registro tolera a GUI como frontend opt-in, herda
gates fail-closed da R470 e nunca a torna padrão. Ver THIRD_PARTY_NOTICES.md.