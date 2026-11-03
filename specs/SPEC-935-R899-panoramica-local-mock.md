# SPEC-935-R899 — Panoramica AI local: backend simulado para tornar a cópia funcional

- **Status:** active
- **Data:** 2026-10-15
- **Orquestrador:** marceloclaro
- **Modo:** TDD estrito (RED → GREEN → REFACTOR)
- **Depende de:** SPEC-935-R898 (auditoria REA do site; cópia em `odonto/rx-site-local/`)

## 1. Contexto e problema

A cópia local do `rx.engenhariaorofacial.com.br` foi auditada com REA em
SPEC-935-R898. Ao servir a cópia com `python3 -m http.server`, o aplicativo
**não funciona**: o front-end faz `fetch(...).then(r => r.json())`, cada
endpoint devolvia a página 404 em HTML e o navegador falhava com:

```
Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

Evidência da falha (`.opencode/browser/evidence/6850e1d3…json`):
`Total messages: 9 (Errors: 9)` em `/health`, `/reviewer-ranking`,
`/reviewer-profiles`, `/administrator-statistics`, `/training-progress`,
`/admin/api/session`, `/og-image.png`, `/favicon.ico`, `/training-video.mp4`.

## 2. Objetivo

Tornar a cópia local **funcional como interface**, sem nunca sugerir que haja
inferência de IA rodando localmente.

## 3. Requisitos funcionais

| ID | Requisito | Critério de aceitação |
|---|---|---|
| FR-001 | Servir a cópia estática | `GET /`, `/editor.js`, `/navigation.js`, `/navigation.css` → 200 com tipos corretos; sem path traversal |
| FR-002 | Endpoints JSON | `/health`, `/admin/api/session`, `/training-progress`, `/reviewer-ranking`, `/reviewer-profiles`, `/administrator-statistics` devolvem `application/json` **válido** |
| FR-003 | Bundle de análise | `POST /predict/images` devolve ZIP **STORED** com `panoramica-anotada.png`, `panoramica-anatomia.png`, `panoramica-dentes.png`, `panoramica-impressao.json` e headers `X-Teeth-Count`, `X-Findings-Count`, `X-Additional-Status`, `X-Additional-Count`, `X-Anatomy-Count`, `X-Model-Scope` |
| FR-004 | Restrições do `readImageBundle` | ZIP sem data descriptor (`flags == 0`), `compression == 0`, `panoramica-dentes.png` com exatamente `layout.width × layout.height` |
| FR-005 | **Não fabricar detecções** | Padrão `--simulate 0`: `report.teeth == []`, `report.findings == []`, `X-Teeth-Count: 0`. Com `--simulate N`, caixas rotuladas `DEMO-FDI` e `"mock": true` no JSON |
| FR-006 | Aviso não bloqueante | O HTML injeta `#mock-notice` **no rodapé** com `pointer-events:none` — proibido cobrir a barra de navegação fixa |
| FR-007 | Rotas não capturadas | `/review`, `/validacao`, `/cadastro`, `/docs`, `/desejos` → página explicativa HTML (200), sem fingir ser o produto original |
| FR-008 | Admin/revisão | `/admin/api/images/*` → `404 JSON` com `detail` (exige backend real) |
| FR-009 | Assets ausentes | `favicon.ico`, `og-image.png`, `colaboradores/*` → PNG 1×1 transparente |
| FR-010 | Testes automatizados | `python3 -m pytest odonto/rx-site-local/tests/test_serve.py -q` → **10 passed** |

## 4. Não escopo

- Nenhuma inferência de IA, treino ou carregamento de modelo.
- Nenhum upload para servidor externo; tudo é local (`127.0.0.1`).
- Nenhum afamento de resultado clínico; a página não pode virar alegação de desempenho.

## 5. Evidências de execução

| Etapa | Evidência |
|---|---|
| Bundle/multipart/ZIP | `tests/test_serve.py` → 10 passed |
| HTTP real | `GET` dos 6 endpoints JSON + `POST /predict/images` (multipart com PNG real) → 200, headers e dimensões coerentes |
| Navegador (falha antes) | `.opencode/browser/evidence/6850e1d3…json` — 9 erros de console |
| Navegador (depois) | `.opencode/browser/evidence/9de7aeed…json` — **1 erro** (`training-video.mp4`, arquivo não capturado) |
| Navegação | `.opencode/browser/evidence/ff27ac01…json` — clique em *Revisão* → `/review`, `success: true` |

## 6. Defeito corrigido durante a implementação (REFACTOR)

O primeiro aviso injetado ficava `sticky` no topo e **interceptava os cliques** da
navegação (`<div>…MODO LOCAL…</div> intercepts pointer events`, evidência
`7898ed24…json`). Corrigido para rodapé fixo com `pointer-events:none`;
regressão coberta por `test_aviso_mock_nao_bloqueia_cliques`.

## 7. Riscos e limites

- `/review`, `/validacao`, `/cadastro`, `/docs`, `/desejos` não são as rotas
  originais (não capturadas na auditoria REA).
- `training-video.mp4` permanece 404 — arquivo genuinamente ausente; fabricar um
  vídeo seria pior que o aviso honesto de ausência.
- `editor.js` está truncado na análise estática da REA; a edição no navegador
  não foi exercitada.
- A cópia do site é material de terceiros, auditado sob uso analítico/documental;
  a propriedade permanece com o dono original do domínio.
