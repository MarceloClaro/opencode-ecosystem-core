---
spec_id: SPEC-935-R827
title: Cancelamento das rotas de conhecimento na fila MCP
status: implemented
component: integrations/ecosystem_mcp.py
test_file: tests/test_r827_remaining_mcp_cancellation.py
---

# R827 — Não iniciar operação cancelada depois da fila

A contraprova das rotas runtime, download e notebook mostrou que o cliente
recebia CancelledError, mas o worker iniciava após liberar a exclusão de execução.
O wrapper asyncio.to_thread não fornecia o sinal usado pela fila cooperativa R825.

Todas as sete rotas de conhecimento com mutação devem usar run_cancellable.
O worker cancelado na fila não alcança o método primário; o worker ativo recebe
o Event da requisição e permanece acompanhado até sua limpeza/conclusão.
As validações de domínio continuam anteriores ao despacho. O primário,
exclusão compartilhada e persistência MetaBus permanecem no mesmo caminho.

Os testes das rotas públicas isolam validadores/worker com fixtures sem rede,
inferência ou escrita externa. RED/GREEN cobre fila e sinal/espera de limpeza;
a contraprova prévia distingue os três casos demonstrados do quarto inconclusivo.

Limite: o wrapper não pode interromper à força uma thread Python arbitrária.
Providers que não consultam o Event permanecem acompanhados até o próprio
prazo/conclusão; cancelamento não desfaz efeitos já iniciados. Não declarar
interrupção imediata ou reversão de todos os providers a partir desta correção.

Aceite: 14 contraprovas RED falharam antes da troca dos wrappers; 64 casos
relacionados e 155 regressões ampliadas passaram após a correção. As sete
rotas públicas possuem testes de fila e worker cooperativo ativo. Evidências
em `outputs/core-r827/release-summary.json`; chamadas externas não foram usadas.
