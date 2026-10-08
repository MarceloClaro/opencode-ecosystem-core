# SPEC-935-R745 — Vigia de frescor dos federados sem rede no gate

**Status:** `em implementação`
**Ciclo:** R745→R746
**Data:** 2026-10-07
**Base:** R715 (janelas por classe) + pins R714 envelhecendo em silêncio

## 1. Problema

Pins federados envelhecem sem alarme: `research-engine` tinha 87d de 90d na
pinagem; ninguém é avisado quando um federado cruza a janela da classe. Falta
verificação determinística data vs janela que o operador rode antes de decidir.

## 2. Objetivo

`integrations/polymath_vigia.py` 100% local: `verificar(pins, janelas)` com
`agora` injetável retorna por lab `idade_dias, janela, dias_restantes, estado
(ok|aviso_7d|vencido)` + `emitir_relatorio` em `vigia.json`. Teste hermético com
datas fixas; sem rede.

## 3. Critérios de aceitação

- [ ] AC1 — `aviso_7d` quando 0 ≤ restantes ≤ 7; `vencido` quando < 0; sem `pushed_at` = `sem_dados`.
- [ ] AC2 — Relatório em tmp com schema; `doctor` íntegro.
- [ ] AC3 — Execução real sobre pins R714 reportando o estado atual.
- [ ] AC4 — Nada federado/decidido; sem rede.

## 4. Fora de escopo

- Re-pin, notificação automática, daemon.

## 5. Verificação

- Teste verde; relatório real anexado ao relato.
