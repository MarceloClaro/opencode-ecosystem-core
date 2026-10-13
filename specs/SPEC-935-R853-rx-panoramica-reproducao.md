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

## Resultado

- **REA**: 2 passadas; `ev_a4d5e31a…` (7 arquivos, 16.947 nós AST) e
  `ev_adc1c84b…` (5 módulos JS, 26.631 nós AST). Recuperou endpoints
  (`/health`, `/predict/images`, `/segment/sam`, `/feedback`, `/admin/api/session`),
  a chave `sessionStorage["panoramica-review-notice"]` e as 4 páginas.
- **Artefatos** (`api/`): `openapi.json`, `health.json`, `pages/{index.html,editor.js,review.html,validacao.html,docs.html}`
  com hashes registrados em `rea-evidence.json`.
- **Reprodução** (`repro/`): FastAPI + front-end fiel; teste `test_r853_rx_repro.py`
  **9/9** (ZIP_STORED, cards, dimensões, cabeçalhos, SAM, feedback, sessão admin).
- **Modelo treinado**: **não obtido**. `/health` só expõe hashes e métricas;
  `/models/`, `/weights/`, `/artifacts/`, `/static/models/` → **404**; admin → **401**.

## Limites

A qualidade clínica dos modelos não é reproduzida. Áreas administrativas
(`/admin/api/*`, `/validacao/api/*`) são reproduzidas como stub autenticado, sem
os dados reais de banco. Caminhos dinâmicos (`/admin/api/images/${id}`) não são
totalmente resolvidos pela análise estática. Presuma-se autorização do titular
para reutilização de código/ativos.
