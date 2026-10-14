---
spec_id: SPEC-935-R876
title: RX reprodução — composição por capacidade (motor por rota) e fail-closed real
component: outputs/core-r853-rx
status: implemented
round_id: R876
test_file: tests/test_r876_rx_capability.py
---

# SPEC-935-R876 — Servir cada capacidade com o melhor motor disponível

## Contexto e decisão

O operador relatou o erro:

```
{"detail":"motor de inferência indisponível — motor 'open_base' não cobre
 'detection' (tem ['sam'])"}
```

com `RX_MEDSAM_CKPT=/home/marceloclaro/.cache/rx-weights/medsam_vit_b.pth`.

Causa: a reprodução usava **um único motor ativo** (`_ACTIVE_ENGINE`) e aplicava
`_guard(eng, capability)` em cada rota. O motor `open_base` (Opção 3) só cobre
`sam`; logo, com ele ativo, `/predict` (capability `detection`) devolvia **409**
mesmo havendo outro motor capaz de detectar. O site ficava **inutilizável para
detecção** ou para segmentação, nunca as duas ao mesmo tempo.

Decisão (autorizada pelo operador ao colar o erro): **compor por capacidade** —
cada rota é servida pelo motor ATIVO quando ele cobre a capacidade; caso
contrário, pelo **melhor motor disponível**. O **fail-closed permanece** apenas
para o caso real de indisponibilidade: **409 só quando NENHUM motor disponível
cobre a capacidade**.

## Regra de resolução (engines.py)

- `_PREFERENCE = ("weights", "open_base", "stub")` — motores **reais** antes do
  stub sintético, na composição.
- `providers_for(cap)` — ids de motores de inferência que cobrem `cap`, nessa ordem.
- `resolve_capability(cap, preferred)`:
  1. usa `preferred` (o motor ativo) se ele cobre `cap` **e** está disponível;
  2. senão, o **primeiro provedor disponível** na ordem de preferência;
  3. senão, `None` → quem chama converte em **409** (fail-closed).
- `serving_map(preferred)` — mapa `capability → motor efetivo` (transparência).

## Mudanças em app.py

- `_service_engine(capability)` — resolve e devolve o motor efetivo; 409 só se `None`.
- `_detect()` devolve `(caixas, motor_efetivo)`; `/predict` reporta o motor **real**
  usado (não o ativo); `/predict/images` adiciona o cabeçalho `X-Engine`.
- `/segment/sam` usa `_service_engine("sam")` (ativo se cobrir; senão melhor disponível).
- `/health` expõe `engine.serving`; `/opcoes.json` idem; a página `/opcoes` mostra
  `capability→motor` (ou `409` em vermelho quando nenhum cobre).

## Critérios de aceitação

1. Com `RX_ENGINE=open_base` e sem pesos, `/predict` responde **200** com
   `engine: "stub"` (fallback), e `/segment/sam` responde **200**.
2. Com MedSAM disponível, `/segment/sam` continua usando `open_base` (MedSAM real).
3. `/health` expõe `engine.serving` cobrindo `detection`, `sam`, `bundle`.
4. `resolve_capability` devolve `None` quando **nenhum** motor disponível cobre a
   capacidade — e a rota responde **409** (fail-closed preservado).
5. O motor ativo tem precedência quando cobre e está disponível.

## Limites (anti-overclaim)

- Composição por capacidade **não** cria modelo odontológico: o fallback é o motor
  **sintético** `stub` quando não há pesos reais. Rótulos do stub são de demonstração.
- Não substitui silenciosamente por outro modelo real de domínio errado: só usa
  `weights` quando o operador aponta `RX_WEIGHTS_DIR` a pesos reais.
- Verificação **funcional** (contrato/HTTP); **não** afirma equivalência clínica ao alvo.
