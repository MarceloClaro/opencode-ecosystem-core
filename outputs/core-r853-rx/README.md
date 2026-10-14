# ODONTOCA - Prof. Marcelo Claro — documentação (REA) e reprodução

> **Rebrand da reprodução.** A aplicação **reproduzida** (backend + páginas locais)
> chama-se agora **ODONTOCA - Prof. Marcelo Claro**. O **alvo observado**
> (`https://rx.engenhariaorofacial.com.br/`) permanece referido pelo seu nome real,
> **"Panoramica AI"**, nas evidências e no REA (abaixo) — por fidelidade; renomear
> capturas congeladas falsificaria a prova. Tokens de contrato (`panoramica-*.png`,
> `X-Panoramica-CSRF`, `panoramica-review-notice`) **não** foram alterados.

**Alvo:** `https://rx.engenhariaorofacial.com.br/` — aplicação web "Panoramica AI"
(visualização e análise assistida de radiografias panorâmicas odontológicas).
**Spec:** `specs/SPEC-935-R853-rx-panoramica-reproducao.md` · `specs/SPEC-935-R874-rx-admin-completude-persistencia.md` · `specs/SPEC-935-R875-medsam-real-cpu.md` · `specs/SPEC-935-R876-rx-composicao-por-capacidade.md`
**Rodada:** R853 (reprodução) · R874 (completude admin + persistência) · R875 (MedSAM real em CPU) · R876 (composição por capacidade) · **Testes:** `tests/test_r853_rx_repro.py`, `tests/test_r874_rx_admin.py`, `tests/test_r875_medsam_cpu.py`, `tests/test_r876_rx_capability.py`

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
- `repro/backend/app.py` — **FastAPI** que reproduz o contrato, com **seleção de motor**
  (`stub` determinístico por padrão; `weights`/`open_base` reais quando disponíveis;
  `training` apenas receita). **Fail-closed**: motor indisponível → **409**, nunca
  resultado falso.
- `repro/backend/engines.py` — registro dos motores com detecção honesta de dependências.
- `repro/training/` — pipeline de treino (Opção 2): receita publicada (Mask DINO + Swin-B),
  rota YOLO, datasets públicos e `download_datasets.sh` (só instruções).

### Três opções de motor (ver `OPCOES.md`)

| # | Motor | Precisa de | Aqui |
|---|---|---|---|
| 1 | `weights` | `ultralytics` + `RX_WEIGHTS_DIR` | **verificada** (`.venv` + `.pt`; ver `op1-verificacao/`) |
| 2 | `training` | GPU + datasets | não executável aqui |
| 3 | `open_base` | `torch`+`segment_anything`+`RX_MEDSAM_CKPT` | **verificada** (`.venv` + SAM ViT-B **e MedSAM real**; ver `op3-verificacao/`) |
| 0 | `stub` | — | **pronto** (padrão) |

As **Opções 1 e 3** foram verificadas ponta a ponta em `.venv`: `POST /predict`
retornou **detecções reais** (person/bus) e `POST /segment/sam` retornou um
contorno **real** de 2031 pontos. Evidências: `op1-verificacao/op1-live-evidence.json`
e `op3-verificacao/op3-live-evidence.json`. Os pesos usados são de **demonstração**
(COCO / SAM base), **não** odontológicos.

A **Opção 3** foi reforçada com o **MedSAM real** (`medsam_vit_b.pth`,
sha256 `34b34b78…`, SPEC-935-R875): `POST /segment/sam` retorna contorno real em
**CPU**. Defeito corrigido — o checkpoint MedSAM ancora storages em CUDA e o
`segment_anything` carrega sem `map_location`; a reprodução usa `_load_sam`
(`map_location="cpu"` + `load_state_dict(strict=True)`, cache por caminho).

Rodar:

```bash
# Forma recomendada — servidor DUAL-STACK (IPv4 + IPv6) num único processo (R878):
cd outputs/core-r853-rx/repro
RX_ENGINE=open_base RX_MEDSAM_CKPT=~/.cache/rx-weights/medsam_vit_b.pth \
    python3 serve.py
# Visualizador: http://127.0.0.1:8799/  (ou http://localhost:8799/)  Opções: /opcoes   Swagger: /docs
# LAN: http://<IP-do-host>:8799/   (ex.: http://172.17.162.153:8799/)
# Porta: RX_PORT=9000 python3 serve.py
# Escolher motor: RX_ENGINE=weights|open_base|stub  ou a interface /opcoes
# Banco (persistência): RX_ADMIN_DB=/caminho/admin.db  (default ~/.cache/rx-admin/admin.db)
```

> `serve.py` (R878) abre um socket AF_INET6 em `[::]` com `IPV6_V6ONLY=0` e o
> entrega ao uvicorn — o `uvicorn --host` liga só **uma** família por processo
> (`--host 127.0.0.1` = só IPv4; `--host ::` = só IPv6). Necessário porque
> `localhost` resolve para `::1` neste host. **Atenção:** expõe o serviço na LAN;
> as rotas admin usam credenciais de **demonstração** — não usar com dados reais.
>
> Forma alternativa (IPv4 apenas, uvicorn clássico):
> `python3 -m uvicorn app:app --app-dir outputs/core-r853-rx/repro/backend --port 8799`

### Publicar online (container) — R882

O GitHub Pages **não** roda a app (é estático/sem Python). Para publicar a app
**funcionando**, use um host Python via Docker — o pacote já está pronto em
`repro/`: `Dockerfile`, `backend/requirements.txt` (runtime mínimo: fastapi/
uvicorn/pillow/python-multipart), `.dockerignore` e o Blueprint `render.yaml`.
Com `RX_ENGINE=stub` a imagem roda **sem pesos e sem torch** (testado).
Passo a passo completo (Render/Railway/Fly/Cloud Run/HF Spaces) em
[`DEPLOY.md`](./DEPLOY.md). O deploy é executado pelo operador; a verificação é
por HTTP (`/health` 200), não por "o build passou".

### Áreas administrativas completas + persistência (R874)

A reprodução cobre agora **as 23 rotas do contrato** e as **11 rotas admin que o
front `/review` e `/validacao` realmente chamam** (antes ausentes → 404):

`/admin/api/images/{id}` (+`/thumbnail`,`/image`,`/age`,`/edit-lock`,`/segment`),
`/admin/api/jobs/{id}`, `/admin/api/batch[/{id}]`, `/admin/api/export`,
`/validacao/api/modelos/{slug}`, `/validacao/api/modelos/{slug}/imagens/{id}/revisao`,
`/validacao/{slug}` (HTML). Sessões, imagens, anotações, jobs, lotes, lock de
edição, feedback e relatórios de validação persistem em **SQLite** (`store.py`).

Os dados semeados são **DEMONSTRAÇÃO SINTÉTICA** (12 radiografias geradas
proceduralmente, 5 relatórios de modelo) — apenas para exercitar a interface;
**não** são o banco real do alvo nem dados clínicos. As páginas `/review`,
`/validacao` e `/validacao/{slug}` funcionam ponta a ponta (login → listar →
revisar → exportar).

Verificar: `python3 -m pytest tests/test_r853_rx_repro.py tests/test_r874_rx_admin.py -q`
(**R853**: 18 testes — contrato, ZIP_STORED, cards/dimensões, cabeçalhos, SAM,
feedback, admin 401, opções de motor, fallback honesto (R876), scaffold de treino,
Opções 1 e 3 reais sob `.venv`; **R874**: 19 testes — sessão/CSRF, statistics, reviews
paginadas, imagens PNG, idade, lock, job, lote, export ZIP, relatórios de validação,
persistência após reabertura, 401 sem sessão, 404 de slug).

### Composição por capacidade (R876)

O erro relatado pelo operador —
`{"detail":"motor 'open_base' não cobre 'detection' …"}` (409) com `RX_MEDSAM_CKPT`
— decorria de um **único motor ativo** com *guard* por rota. A reprodução agora
**compõe por capacidade**: o motor ativo serve o que ele cobre; o restante é
servido pelo **melhor motor disponível** (motores reais antes do `stub`). Com
`open_base` ativo, `POST /predict` responde **200** (detecção → `stub`) e
`POST /segment/sam` responde **200** via **MedSAM real**. `/health` e `/opcoes.json`
expõem `engine.serving` (`detection/sam/bundle`); a página `/opcoes` mostra o mapa.
O **fail-closed permanece**: 409 **apenas** quando nenhum motor disponível cobre a
capacidade. Ver: `specs/SPEC-935-R876-rx-composicao-por-capacidade.md`,
`tests/test_r876_rx_capability.py` (9 testes).

Verificar: `python3 -m pytest tests/test_r853_rx_repro.py tests/test_r874_rx_admin.py tests/test_r875_medsam_cpu.py tests/test_r876_rx_capability.py -q`

## 6. Ética e escopo

Leitura de conteúdo **publicamente servido**; nenhuma tentativa de contornar
autenticação, nada destrutivo, nenhum uso de credenciais. A reprodução destina-se
ao operador do domínio. Presuma-se autorização; em caso de titularidade de
terceiros, obtenha permissão antes de reutilizar código/ativos.
