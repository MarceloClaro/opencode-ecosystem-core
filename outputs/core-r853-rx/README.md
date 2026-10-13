# Panoramica AI — documentação (REA) e reprodução

**Alvo:** `https://rx.engenhariaorofacial.com.br/` — aplicação web "Panoramica AI"
(visualização e análise assistida de radiografias panorâmicas odontológicas).
**Spec:** `specs/SPEC-935-R853-rx-panoramica-reproducao.md`
**Rodada:** R853 · **Teste:** `tests/test_r853_rx_repro.py`

> Documento produzido por leitura pública (HTTP GET, sem autenticação) e por
> análise estática do REA 6.4.0. Áreas administrativas foram sondadas em
> somente-leitura e recusaram com `401`. Nada foi promovido: `externally_validated=false`,
> `confidence_promoted=false`. A reprodução **não** inclui os modelos de IA.

## 1. Como o REA foi usado (documentação)

REA 6.4.0, provider `rea-javascript-application` (análise **estática e inerte** —
o bundle nunca é executado). Duas passadas documentadas em `rea-evidence.json`:

| Passada | Entrada | `evidence_id` | Arquivos | Nós AST |
|---|---|---|---|---|
| 1 | `api/pages/` (HTML + editor.js) | `ev_a4d5e31a13e4bb312d7de212c8f7a10c2d88728c48231d2df1b75e736fb31590` | 7 (1 JS) | 16.947 |
| 2 | scripts inline extraídos p/ `.js` | `ev_adc1c84bda0b19556be146095455b89aaae4a38cf84529eca3e4c70dc53a2251` | 5 (5 JS) | 26.631 |

O REA recuperou **endpoints de rede**, **chave de storage** e **renderers**:

- Endpoints: `/health`, `/predict/images`, `/segment/sam`, `/feedback`, `/admin/api/session`
- Storage: `sessionStorage["panoramica-review-notice"]`
- Renderers/páginas: `index.html`, `review.html`, `validacao.html`, `docs.html`

Limitações declaradas pelo REA: HTML/JS tratados como texto inerte; relações
estáticas **não provam execução**; caminhos dinâmicos (template literals como
`/admin/api/images/${id}`) podem ficar não resolvidos.

## 2. Superfície HTTP (fonte de verdade: `/openapi.json`, "Panoramica AI 0.1.0")

Backend = **FastAPI** (Swagger em `/docs`). 23 rotas:

**Públicas**
- `GET /health` — modelos, hashes, versões de treino, SAM, modelo adicional (31 classes)
- `POST /predict` — detecções (JSON)
- `POST /predict/image` — radiografia anotada (PNG)
- `POST /predict/images` — **ZIP_STORED**: `panoramica-anotada.png`, `panoramica-anatomia.png`, `panoramica-dentes.png`, `panoramica-impressao.json`
- `POST /segment/sam` — contorno a partir de uma caixa
- `POST /feedback`, `GET /feedback/{image_id}`, `GET /feedback/export`
- `GET /docs`, `GET /openapi.json`

Parâmetros de `/predict*`: `confidence` (0.25), `fdi_confidence` (0.40),
`anatomy_confidence`, `imgsz` (640), `min_iou` (0.5), `include_additional` (true),
`model_scope` (`combined`|`dental31`), `diagnose` (false). Corpo `multipart/form-data` com `file`.

Cabeçalhos de resposta de `/predict/images` (usados pelo front-end):
`X-Model-Scope`, `X-Additional-Status`, `X-Additional-Count`, `X-Anatomy-Count`,
`X-Teeth-Count`, `X-Findings-Count`.

**Autenticadas (sessão admin; 401 sem cookie)**
- `GET/POST /admin/api/login|session|logout`
- `GET /admin/api/reviews` (`page`, `status`, `class_group`, `class_label`, `age_group`, `probability_order`, `source_group`)
- `GET /admin/api/statistics`
- `GET/PUT/DELETE /admin/api/images/{image_id}` (+ `/thumbnail`, `/image`, `/age`, `/edit-lock`, `/segment`)
- `GET /admin/api/export` (`group`, `task`)
- `GET/POST/DELETE /admin/api/batch[/{batch_id}]`, `GET /admin/api/jobs/{job_id}`
- `GET /validacao/api/modelos[/{slug}]` (mesma sessão)

## 3. Páginas

| Rota | Arquivo (capturado) | Função |
|---|---|---|
| `/` | `api/pages/index.html` (49 KB) | Visualizador: upload, análise, 4 imagens, edição, laudo A4 |
| `/review` | `api/pages/review.html` (43 KB) | Revisão do banco (admin): radiografias, exemplos por classe, zoom |
| `/validacao` | `api/pages/validacao.html` (37 KB) | Validação dos modelos (admin): métricas, por classe, imagens |
| `/docs` | `api/pages/docs.html` | Swagger UI |
| — | `api/pages/editor.js` (93 KB) | Editor de caixas/contornos (canvas, pincel, SAM) |

O `index.html` contém o parser de resposta `readImageBundle()` — a **invariante**
central: o ZIP deve ser `ZIP_STORED` com exatamente `panoramica-anotada.png`,
`panoramica-anatomia.png`, `panoramica-dentes.png` e `panoramica-impressao.json`,
e as dimensões de `panoramica-dentes.png` **devem** coincidir com
`layout.width × layout.height`.

## 4. Modelo treinado: **não obtido**

`/health` expõe **apenas metadados**: hashes dos pesos
(`age/fdi/teeth/finding/additional_weights_sha256`) e métricas de treino
(ex.: `fdi.test_f1=0.83`, `teeth.dataset_manifest`, `article=10.1186/s12903-024-04129-5`;
`sam.model=medsam_vit_b`). Nenhuma rota pública serve `.pt/.pth`; sondagens a
`/models/`, `/weights/`, `/artifacts/`, `/static/models/` retornam **404**, e as
rotas administrativas retornam **401**. Portanto a reprodução cobre **contrato e
fluxo de I/O**, não a qualidade clínica.

## 5. Reprodução (`repro/`)

- `repro/frontend/` — cópia fiel dos artefatos públicos (`index.html`, `editor.js`, `review.html`, `validacao.html`)
- `repro/backend/app.py` — **FastAPI** que reproduz o contrato, com "motor"
  determinístico explícito (stub) que gera caixas/pranchas a partir do tamanho da
  imagem. Substitui os modelos reais; **não** é detecção clínica.

Rodar:

```bash
python3 -m uvicorn app:app --app-dir outputs/core-r853-rx/repro/backend --port 8799
# Front-end: http://127.0.0.1:8799/   Swagger: http://127.0.0.1:8799/docs
```

Verificar: `python3 -m pytest tests/test_r853_rx_repro.py -q`
(o teste replica `readImageBundle` e confere ZIP_STORED, cards, dimensões e cabeçalhos).

## 6. Ética e escopo

Leitura de conteúdo **publicamente servido**; nenhuma tentativa de contornar
autenticação, nada destrutivo, nenhum uso de credenciais. A reprodução destina-se
ao operador do domínio. Presuma-se autorização; em caso de titularidade de
terceiros, obtenha permissão antes de reutilizar código/ativos.
