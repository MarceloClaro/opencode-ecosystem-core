---
spec_id: SPEC-935-R395
title: Daemon LiteRT-LM travado (não offline) reiniciado; diagnóstico de spawn deixa de ser descartado
component: integrations/litert_lm_supervisor.py, scripts/litert-lm-start.sh
status: verified
test_file: tests/test_r212_litert_supervisor.py
---

# SPEC-935-R395 — Daemon LiteRT-LM Travado e Diagnóstico Perdido

**Data:** 2026-08-03
**Motivação:** o usuário pediu para corrigir as duas limitações documentadas
no R394 ("opencode run" trava sem `--model` explícito; subagentes não
invocáveis via `--agent`). A segunda é comportamento do binário externo
`opencode` (fora deste repositório, não corrigível aqui — permanece
documentada, não escondida). A primeira revelou uma causa raiz real e
corrigível.

## 1. A causa real não era "daemon offline"

`doctor`/`PROGRESS.md` documentavam o LiteRT-LM como "offline" há vários
ciclos. Investigação real (não só leitura de estado persistido) revelou:
havia um processo `litert-lm serve --host 127.0.0.1 --port 9379` **vivo
desde 24 de julho** (11+ dias), ainda escutando na porta, mas **travado**
— aceitava a conexão TCP e nunca respondia na camada HTTP (confirmado com
`curl` real: timeout sem resposta, e `ps` mostrando uso de CPU
consistentemente perto de 0%, não um processo genuinamente processando).

`integrations/litert_lm_provider.py::start_server()` corretamente
detectava que esse processo não respondia e registrava falha a cada
tentativa — o `state.json` persistido acumulava `failure_count` (chegou a
41) e abria o circuit breaker repetidamente, exatamente como desenhado.
O sistema de proteção funcionava; o zumbi nunca foi encerrado.

**Ação corretiva imediata**: processo zumbi encerrado (`kill -9`); porta
liberada; `state.json`/`litert-lm.pid` obsoletos removidos; supervisor
iniciou um daemon novo e saudável via `scripts/litert-lm-start.sh ensure`.

## 2. Bug real de diagnóstico — causa raiz do próximo zumbi seria igualmente invisível

`integrations/litert_lm_supervisor.py::LiteRTSupervisor._spawn_locked()`
redirecionava `stdout`/`stderr` do processo filho para `subprocess.
DEVNULL`. Quando o binário real `litert-lm` morre logo após o spawn — por
exemplo com `OSError: [Errno 98] Address already in use`, reproduzido ao
vivo tentando iniciar um segundo daemon com a porta ainda ocupada pelo
zumbi — essa mensagem de erro real e específica era descartada
integralmente. O supervisor só via "o PID morreu, registra falha N", sem
nenhuma pista da causa. Diagnosticar o zumbi desta vez exigiu reprodução
manual fora do supervisor (`litert-lm serve --verbose` direto).

**Correção**: `SupervisorConfig.log_path` novo
(`<runtime_dir>/litert-lm.log`); `_spawn_locked()` abre esse arquivo em
modo append e redireciona `stdout`/`stderr` do processo filho para ele em
vez de `DEVNULL`. `scripts/litert-lm-start.sh --log` atualizado: quando
não há unidade `systemd --user` instalada (caso comum neste ambiente),
mostra as últimas 50 linhas desse arquivo real em vez de só reportar
"consulte o journal" sem nenhuma opção concreta.

## 3. Verificação real, não só reconciliação de estado

- `curl` direto ao daemon reiniciado confirmou inferência real
  funcionando: um `chat/completions` contra `Qwen3-0.6B` retornou uma
  resposta coerente em português.
- `doctor` mudou de `"status": "warn"` para `"status": "pass"` no check
  `litert_lm` após o reinício.
- `litert-lm-start.sh --log` agora mostra conteúdo real (`"Starting
  OpenAI-compatible API server..."`, linha de acesso HTTP real do health
  check), confirmado após um `ensure` limpo.

## 4. O que continua sem solução em código, documentado e não escondido

1. **Latência de cold-start real**: o modelo padrão configurado
   (`gemma-4-E2B-it-litert-lm`, 2.4 GB) leva bem mais de 2 minutos para a
   primeira resposta real neste hardware sem GPU — confirmado
   diretamente (`opencode run` sem `--model` excedeu 120s mesmo com o
   daemon saudável). Isso não é mais "travado para sempre" (o daemon
   responde a health checks e completions reais chegam), mas continua
   lento o suficiente para não ser interativo na prática com o modelo
   padrão atual. Trocar o modelo padrão do projeto é decisão editorial,
   não bug de código — fora do escopo deste ciclo.
2. **Subagentes não invocáveis via `opencode run --agent <nome>`**
   (documentado no R394): comportamento do binário externo `opencode`,
   que distingue agentes primários de subagentes e cai para o agente
   primário `build` quando um subagente é pedido diretamente. Nada em
   código deste repositório controla essa decisão do CLI externo — segue
   documentado, não fabricado como resolvido.

## 5. Critérios de aceitação

1. O processo zumbi identificado foi encerrado e um daemon saudável
   confirmado (`doctor` → `pass`, inferência real testada).
2. `_spawn_locked()` nunca mais descarta `stdout`/`stderr` do processo
   filho — grava em `SupervisorConfig.log_path`, testado com mock de
   `process_factory` (não abre processo real em teste).
3. `scripts/litert-lm-start.sh --log` mostra o log real quando a unidade
   systemd não está instalada, em vez de só uma mensagem sem alternativa.
4. Zero regressão: `test_r212_litert_supervisor.py` 19/19 (era 18),
   suíte completa 2694 aprovados (+1), 0 falhas.
5. Limitações genuinamente fora do controle deste código (latência de
   modelo grande sem GPU; subagentes não endereçáveis via `--agent` no
   CLI externo) documentadas explicitamente, não apresentadas como
   corrigidas.
