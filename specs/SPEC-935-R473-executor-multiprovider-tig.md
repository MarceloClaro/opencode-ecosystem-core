---
spec_id: SPEC-935-R473
title: Executor alternativo multi-provedor (tig) — M7 da resiliência científica (subspec da R471)
component: agent_runners/tig_executor
test_file: tests/test_r473_tig_executor.py
status: green
estoque: rc
data: 2026-09-12
---

# SPEC-935-R473 — Executor alternativo multi-provedor (tig) — M7

## Objetivo
Implementar o módulo M7 da SPEC-935-R471: um executor externo opcional que invoca o agente de terminal `tig` (upstream rsrohan99/tig) com fallback entre provedores de LLM (Ollama local → DeepSeek → Groq → Gemini → OpenAI) e registro de recibo auditável por execução. A integração é **somente por invocação externa** — o upstream não declara licença, portanto é vedada incorporação de código-fonte, redistribuição ou inclusão em bundle.

## Não-objetivos
- Não incorporar, copiar ou redistribuir código do upstream `rsrohan99/tig` (sem licença declarada).
- Não gerenciar credenciais de provedores; o `tig` lê seu próprio ambiente (`.env`) e o adaptador não intercepta, armazena nem transmite segredos.
- Não alterar o pipeline `open_science_only` nem a política da R470 (resolvedores restritos) — o executor é ortogonal ao acesso a artigos.
- Não executar LLM real em testes; toda a suíte é hermética com mocks de subprocess.

## Invariantes
1. A invocação do binário externo ocorre **sem `shell=True`**, com argumentos em forma de lista e `input=task` via stdin; qualquer outra forma é vedada.
2. Provedor fora da allowlist é bloqueado com recibo de negação; allowlist vazia equivale a nenhuma execução (fail-closed).
3. Ausência do binário (`shutil.which` nulo e `TIG_BIN` ausente) equivale a indisponibilidade; nenhuma tentativa de instalação automática é feita.
4. Toda execução, deferida ou negada, gera `TigExecutionReceipt` com: `invoked_at_utc`, `mode`, `task_sha256`, `bin_path`, `provider`, `exit_code`, `success`, `attempted_providers`, `orchestrator=marceloclaro`.
5. Fallback: falha de um provedor (exit != 0, timeout ou exceção controlada) tenta o próximo da lista ordenada; nenhum provedor disponível ⇒ recibo `success=False` com motivo.
6. O adaptador não contém credenciais, não abre rede própria e não grava conteúdo de secrets em recibo.
7. Anti-overclaim: nenhuma saída do executor declara "superhuman", "verificado", "Qualis A1" ou "superação" sem validação externa; o adaptador apenas reporta exit_code e saída truncada.
8. Modos restritos a `architect` e `code` (espelhando o par SDD/implementação do tig); modo desconhecido é negado com recibo.
9. O orquestrador `marceloclaro` permanece o único coordenador autorizado a ordenar despachos; o executor expõe função de status consumível pelo doctor, sem auto-despacho.
10. Esta spec não altera R468/R469/R470, `SECURITY.md` nem `THIRD_PARTY_NOTICES`; o `tig` entra como CLI externa opcional de primeira classe no doctor (EXTERNAL_CLIS), com sugestão `pip install tig-code`.

## Critérios de aceitação
- CA1: Com binário ausente, `TigExecutor.available()` retorna False e `run()` retorna recibo `success=False`, `provider=None`, sem exceção.
- CA2: Com binário presente (mock), `run(mode="architect", task="...", provider_fallback=["ollama","deepseek"])` invoca `subprocess.run([bin, "--mode", "architect", "--provider", "ollama"], shell=False, input=task)`, verificado por mock; nenhuma chamada com `shell=True`.
- CA3: Se o provedor primário falha (exit=1), o executor tenta o próximo; recibo registra `attempted_providers=["ollama","deepseek"]` e o provedor que teve sucesso.
- CA4: Se todos os provedores falham, recibo `success=False` com `exit_code` do último e `attempted_providers` completo.
- CA5: Provedor fora da allowlist (ex.: `"provedor-malicioso"`) é bloqueado; recibo `success=False`, `provider=None`; allowlist vazia ⇒ nenhuma execução.
- CA6: Modo desconhecido (ex.: `"hack"`) é negado com recibo; modos válidos `architect` e `code` executam.
- CA7: Task vazia é negada com recibo; `task_sha256` presente e determinístico no recibo.
- CA8: `tig` registrado em `marceloclaro.doctor.EXTERNAL_CLIS` com sugestão `pip install tig-code`; `_check_external_clis()` nunca falha quando ausente (warn, não fail).
- CA9: Higiene estática: módulo sem `shell=True`, sem `requests.get(`/`urlopen(`/credenciais; suíte sem rede real e sem chamadas reais de subprocess (mocks).
- CA10: Gateway do doctor permanece pass nos módulos essenciais após a mudança (apenas warns de CLIs opcionais); suíte dedicada verde; registro de ciclo R473 no EvolutionRegistry e reflexão no MetaBus.

## Plano TDD
RED: escrever `tests/test_r473_tig_executor.py` cobrindo CA1–CA9 antes da implementação (falha de import e vazios). GREEN: implementar `agent_runners/tig_executor.py` (dataclass `TigExecutionReceipt`, classe `TigExecutor` com allowlist, modos, fallback, invocação via mocks injetáveis) e registrar `tig` em `EXTERNAL_CLIS` no doctor. VERIFY: `pytest tests/test_r473_tig_executor.py`, depois suíte ampla (ignorando débitos pré-existentes R459 e v42_native) e `doctor`; registrar ciclo R473 com score e lições.