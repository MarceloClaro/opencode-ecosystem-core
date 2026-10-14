---
spec_id: SPEC-935-R853
title: REA — documentação e reprodução do site Panoramica AI (rx.engenhariaorofacial.com.br)
component: outputs/core-r853-rx, tests/test_r853_rx_repro.py
status: implemented
round_id: R853
test_file: tests/test_r853_rx_repro.py
---

# SPEC-935-R853 — Documentar (REA) e reproduzir o Panoramica AI

## Contexto e decisão

O operador pediu para **documentar com REA** o site
`https://rx.engenhariaorofacial.com.br/` e, em seguida, **reproduzi-lo**. O alvo
é a aplicação "Panoramica AI" (análise assistida de radiografias panorâmicas):
SPA + backend FastAPI (OpenAPI 0.1.0), com páginas `/` (visualizador), `/review`
(admin), `/validacao` (admin) e `/docs` (Swagger).

Decisão: ler apenas a **superfície pública** (HTTP GET, sem autenticação),
documentar com o REA 6.4.0 (análise estática, `analyze_javascript_application`)
e reproduzir **o contrato e o fluxo de I/O** — não os modelos de IA, que **não**
são acessíveis publicamente.

## Contratos de aceite

1. Documentar com REA e preservar `evidence_id` e hashes (duas passadas:
   `ev_a4d5e31a…`, `ev_adc1c84b…`).
2. Inventariar a superfície HTTP a partir de `/openapi.json` (23 rotas) e as 4 páginas.
3. Baixar e preservar os artefatos públicos com SHA-256.
4. **Reproduzir**: backend FastAPI que cumpre o contrato da superfície pública +
   front-end fiel; o motor de IA é substituído por um stub **determinístico explícito**.
5. A reprodução deve satisfazer a invariante do front-end: `/predict/images`
   devolve `ZIP_STORED` com `panoramica-anotada.png`, `panoramica-anatomia.png`,
   `panoramica-dentes.png` e `panoramica-impressao.json`, com as dimensões da
   prancha iguais a `layout.width × layout.height`, e os cabeçalhos `X-*`.
6. Teste automatizado replicando `readImageBundle` deve passar.
7. Não declarar acesso ao modelo treinado; nada promovido
   (`externally_validated=false`, `confidence_promoted=false`).
8. Ética: nada destrutivo, sem credenciais, sem contornar autenticação.
9. **Opções de motor** expostas ao usuário (pedido do operador): `stub` (padrão,
   sempre pronto), `weights` (Opção 1 — inferência real com `.pt` do operador via
   `RX_WEIGHTS_DIR`+`ultralytics`), `training` (Opção 2 — pipeline de treino em
   `repro/training/`, requer GPU/datasets) e `open_base` (Opção 3 — `/segment/sam`
   real via MedSAM). Selecionável em `/opcoes` (HTML) e `GET/POST /opcoes`, e por
   `RX_ENGINE`. **Fail-closed**: motor indisponível devolve **409** com o motivo —
   jamais resultado falso.

## Resultado

- **REA**: 2 passadas; `ev_a4d5e31a…` (7 arquivos, 16.947 nós AST) e
  `ev_adc1c84b…` (5 módulos JS, 26.631 nós AST). Recuperou endpoints
  (`/health`, `/predict/images`, `/segment/sam`, `/feedback`, `/admin/api/session`),
  a chave `sessionStorage["panoramica-review-notice"]` e as 4 páginas.
- **Artefatos** (`api/`): `openapi.json`, `health.json`, `pages/{index.html,editor.js,review.html,validacao.html,docs.html}`
  com hashes registrados em `rea-evidence.json`.
- **Reprodução** (`repro/`): FastAPI + front-end fiel; teste `test_r853_rx_repro.py`
  **16/16** (ZIP_STORED, cards, dimensões, cabeçalhos, SAM, feedback, sessão admin,
  opções de motor, fail-closed 409, scaffold de treino). Verificado ao vivo
  (uvicorn): `/opcoes.json` lista 4 motores; ativar `weights` sem `ultralytics` →
  `/predict/images` **409** com causa; `stub` → **200**.
- **Modelo treinado**: **não obtido**. `/health` só expõe hashes e métricas;
  `/models/`, `/weights/`, `/artifacts/`, `/static/models/` → **404**; admin → **401**.
  Extração de pesos via API foi **recusada** (model extraction não autorizado).

## Limites

A qualidade clínica dos modelos não é reproduzida. Áreas administrativas
(`/admin/api/*`, `/validacao/api/*`) foram reproduzidas como stub autenticado, sem
os dados reais de banco. Caminhos dinâmicos (`/admin/api/images/${id}`) não são
totalmente resolvidos pela análise estática. Presuma-se autorização do titular
para reutilização de código/ativos.

> **Continuação (R874):** a completude das rotas admin/validação e a persistência
> (SQLite) foram implementadas em `SPEC-935-R874-rx-admin-completude-persistencia.md`
> — as 11 rotas que o front `/review` e `/validacao` chamam de fato deixaram de
> faltar, com dados de **demonstração sintética**.
