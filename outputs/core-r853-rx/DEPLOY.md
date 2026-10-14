# Deploy da reprodução (container) — SPEC-935-R882

Guia para publicar a app **funcionando** (FastAPI) num host Python. O GitHub
Pages **não** serve para isto (é estático, sem Python); use um host que rode
Docker/Python. O código permanece no GitHub; só a *execução* vai para o host.

> **Escopo honesto**: este documento entrega o **pacote pronto e testado** e o
> passo a passo. O deploy é executado por você (o agente não tem sua conta do
> provedor e não declara "publicado" sem prova física — status, URL, bytes).

## O que a imagem contém

`repro/Dockerfile` (contexto de build = `outputs/core-r853-rx/repro`):

- Base `python:3.12-slim`; deps mínimas do `backend/requirements.txt`
  (`fastapi`, `uvicorn`, `pillow`, `python-multipart`).
- `serve.py` + `backend/` + `frontend/` (mesma árvore que roda local).
- Engine **`stub`** por padrão — a app completa (front, `/review`, `/validacao`,
  persistência SQLite, `/predict` stub, `/segment/sam` retangular) roda **sem
  pesos e sem torch** (SPEC-935-R882, testado com torch/cv2/numpy bloqueados).
- `HEALTHCHECK` em `/health`.

## Variáveis de ambiente

| Var | Default no container | Para quê |
|---|---|---|
| `RX_HOST` | `0.0.0.0` | Interface de bind (nuvem exige `0.0.0.0`) |
| `PORT` | (injetado pelo host) | Porta; tem precedência sobre `RX_PORT` |
| `RX_PORT` | `8799` | Porta quando o host não injeta `PORT` |
| `RX_ENGINE` | `stub` | `stub` \| `weights` \| `open_base` |
| `RX_ADMIN_DB` | `/data/admin.db` | Caminho do SQLite (use disco persistente) |
| `RX_WEIGHTS_DIR` | — | Só p/ engine `weights` (exige deps/volumes extras) |
| `RX_MEDSAM_CKPT` | — | Só p/ engine `open_base` (exige `torch` + checkpoint) |

## Opção 1 — Render (recomendada, mais simples)

1. Render → **New → Web Service** → conecte o repo `MarceloClaro/opencode-ecosystem-core`.
2. **Root Directory**: `outputs/core-r853-rx/repro`
   (é onde estão o `Dockerfile` e o contexto). **Runtime**: Docker.
3. **Health Check Path**: `/health`. Instância **Free** serve para demonstração.
4. Deixe `RX_HOST=0.0.0.0` (o `render.yaml` já traz) — a Render injeta `PORT`.
5. (Opcional, pago) **Disk** montado em `/data` para o SQLite durar entre deploys;
   sem disco, o banco é recriado a cada deploy (dados de demonstração).
6. Primeiro build leva ~2–4 min. A URL sai como `https://<nome>.onrender.com`.

Atalho (Blueprint): o **`render.yaml` na RAIZ do repositório** é o Blueprint
canônico — a Render **só** procura `render.yaml` na raiz, nunca em subpastas.
Use **New → Blueprint** → conecte o repo → ele já traz `rootDir:
outputs/core-r853-rx/repro`, `healthCheckPath: /health` e as envs; não precisa
preencher o Root Directory à mão. O `repro/render.yaml` é a **mesma** definição
mantida junto do app (referência e testes), mas **não** é auto-detectado.

> Plano Free hiberna após inatividade: o **primeiro** acesso depois disso é lento.
> Para os motores `weights`/`open_base` (SAM/MedSAM reais) o Free **não** serve —
> precisaria de imagem com `torch` (~1 GB+) e disco para o checkpoint.

## Opção 2 — Railway

1. New Project → Deploy from GitHub repo → seletor de diretório: `outputs/core-r853-rx/repro`.
2. Railway detecta o `Dockerfile`. Defina `RX_HOST=0.0.0.0` (Railway injeta `PORT`).
3. Healthcheck: `/health`.

## Opção 3 — Fly.io

```bash
cd outputs/core-r853-rx/repro
fly launch --no-deploy          # cria fly.toml; escolha app name/região
fly secrets set RX_HOST=0.0.0.0
fly deploy
```
Ajuste `internal_port = 8799` (ou o que o `serve.py` usar) no `fly.toml`.

## Opção 4 — Google Cloud Run

```bash
cd outputs/core-r853-rx/repro
gcloud run deploy odontoca-rx \
  --source . --region us-central1 --allow-unauthenticated \
  --port 8080 --set-env-vars RX_HOST=0.0.0.0,RX_ENGINE=stub
```
Cloud Run injeta `PORT` e exige bind em `0.0.0.0` (já coberto pelo `serve.py`).

## Opção 5 — Hugging Face Spaces (Docker)

Crie um Space (SDK: Docker) e copie `repro/` para o Space. O `Dockerfile` já
expõe `8799`; ajuste `app_port` no `README.md` do Space para `8799` se necessário.

## Verificação após o deploy (anti-overclaim)

```bash
U="https://SEU-APP"
curl -s -o /dev/null -w '%{http_code}\n' "$U/health"          # 200
curl -s "$U/health" | grep -q '"serving"'                     # engine map presente
curl -s -o /dev/null -w '%{http_code}\n' "$U/"                # 200 (index)
curl -s -o /dev/null -w '%{http_code}\n' "$U/review"          # 200
# inferência stub (substitua o caminho por uma radiografia de demo):
curl -s -o /dev/null -w '%{http_code}\n' -F "file=@pano.png" "$U/predict/images"
```
Só considere "publicado" com **status HTTP observado** e a URL respondendo o
marcador de conteúdo — nunca por "o build passou".

## Limites / avisos

- **Dados**: as rotas admin usam **credenciais de demonstração** (o login da
  reprodução não valida senha) e dados **sintéticos**. Não use com dados reais.
- **Persistência**: sem disco persistente, o SQLite (`/data/admin.db`) reinicia
  a cada deploy.
- **Motores reais**: `weights`/`open_base` exigem deps pesadas (torch/opencv) e
  checkpoints — fora da imagem mínima; trate como build separado.
- **Custo**: a imagem mínima é pequena e cabe no nível gratuito dos PaaS; os
  motores reais não.
